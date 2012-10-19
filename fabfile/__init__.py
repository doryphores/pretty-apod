import sys
import os
import datetime
import random

from fabric.api import *
from fabric.context_managers import prefix
from fabric.contrib import django, files
from fabric.colors import *
from fabric.utils import abort


@task
def staging():
	"""
	Setup staging environment vars
	"""
	env.default_refspec = 'develop'
	env.hosts = ['staging.apod']
	env.project_dir = '/home/martin/pretty-apod'
	env.python = 'python'
	env.pip = 'pip'

	config()


@task
def prod():
	"""
	Setup production environment vars
	"""
	env.default_refspec = False
	env.hosts = ['doryphores@doryphores.webfactional.com']
	env.project_dir = '/home/doryphores/webapps/prettyapod'
	env.python = 'python2.7'
	env.pip = 'pip-2.7'

	config()


def config():
	env.git_url = 'git@github.com:doryphores/pretty-apod.git'

	env.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
	env.env_dir = os.path.join(env.project_dir, 'env')
	env.backup_dir = os.path.join(env.project_dir, 'backup')
	env.repo_dir = os.path.join(env.project_dir, 'repo')
	env.release_dir = os.path.join(env.project_dir, 'releases')
	env.shared_dir = os.path.join(env.project_dir, 'shared')
	env.current_dir = os.path.join(env.project_dir, 'current')

	env.release_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
	env.current_release_dir = os.path.join(env.release_dir, env.release_timestamp)

	env.releases_to_keep = 3
	env.backups_to_keep = 3


@task
def check_requirements():
	"""
	Checks requirements no remote host
	"""
	missing = []

	print(green('Checking requirements'))

	for tool in ['compass', 'cake', 'virtualenv', 'git', 'exiftool']:
		with settings(hide('warnings', 'stdout'), warn_only=True):
			result = run('which %s' % tool)
			if result.failed:
				missing.append(tool)

	if missing:
		abort(red('Please install missing packages: %s' % ', '.join(missing)))

	missing = []

	print(green('Checking node requirements'))

	for package in ['stitch', 'uglify-js', 'coffee-script']:
		with settings(hide('warnings', 'stdout'), warn_only=True):
			result = run('npm ls | grep "%s"' % package)
			if result.failed:
				missing.append(package)

	if missing:
		abort(red('Please install missing node packages: %s' % ', '.join(missing)))


def setup():
	"""
	Setup directories, repository and virtual environment
	"""
	print(green('Setting up project structure'))
	run('mkdir -p %s' % env.backup_dir)
	run('mkdir -p %s' % env.repo_dir)
	run('mkdir -p %s' % env.release_dir)
	run('mkdir -p %s/media' % env.shared_dir)
	run('mkdir -p %s/logs' % env.shared_dir)

	active_settings = '%s/active.py' % env.shared_dir
	if not files.exists(active_settings):
		print(green('Creating active settings file'))
		files.upload_template(
			filename='%s/active.tpl' % env.template_dir,
			context={
				'name': prompt(yellow('Database name:')),
				'user': prompt(yellow('Database user:')),
				'password': prompt(yellow('Database password:')),
				'cdn_host': prompt(yellow('CDN host (include http, optional):')),
				'email_host': prompt(yellow('Mail server host:')),
				'email_port': prompt(yellow('Mail server port:')),
				'email_use_tls': prompt(yellow('Mail server uses TLS (True or False):')),
				'email_user': prompt(yellow('Mail server user name:')),
				'email_password': prompt(yellow('Mail server password:')),
				'email_from': prompt(yellow('From email address:')),
				'email_server_email': prompt(yellow('Server email address:')),
				'memcache_location': prompt(yellow('Memcache location:')),
				'secret_key': "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)])
			},
			destination=active_settings
		)

	with cd(env.repo_dir):
		with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
			result = run('git status')
			if result.failed:
				print(green('Cloning git repository'))
				run('git clone %s %s' % (env.git_url, env.repo_dir))

	if not files.exists(env.env_dir):
		print(green('Creating virtualenv'))
		run('virtualenv -p %s --distribute --system-site-packages %s' % (env.python, env.env_dir))


def update_env():
	"""
	Updates virtual environment requirements
	"""
	print(green('Updating virtual environment requirements'))
	_run_ve('pip install -q -r %s/requirements/prod.txt' % env.current_release_dir)


def update_code():
	"""
	Updates code from repository
	"""
	refspec = select_tag()
	print(green('Updating code from repository'))
	with cd(env.repo_dir):
		run('git fetch && git checkout %s' % refspec)


def prepare_release():
	"""
	Prepares new release for deployment
	"""

	try:
		print(green('Creating new release and copying code'))
		run('mkdir -p %s' % env.current_release_dir)
		run('cp -R %s/* %s' % (env.repo_dir, env.current_release_dir))

		print(green('Symlinking shared assets'))
		run('ln -s %s/media %s/public/media' % (env.shared_dir, env.current_release_dir))
		run('ln -s %s/logs %s/logs' % (env.shared_dir, env.current_release_dir))
		run('ln -s %s/active.py %s/settings/active.py' % (env.shared_dir, env.current_release_dir))

		update_env()

		print(green('Compiling CSS'))
		with cd('%s/ui/scss/' % env.current_release_dir):
			run('compass compile --force -e production')

		print(green('Compiling JS'))
		with cd('%s/ui/coffee/' % env.current_release_dir):
			run('cake -m build')

		print(green('Collecting static assets'))
		_run_ve('%s/manage.py collectstatic --noinput --verbosity=0' % env.current_release_dir)
	except:
		print(red('Something went wrong, rolling back release'))
		run('rm -rf %s' % env.current_release_dir)
		abort(red('Deploy failed'))


def finalise():
	"""
	Runs DB migrations, symlinks new release and restarts app
	"""

	print(green('Running database migrations'))
	_run_ve('%s/manage.py syncdb --migrate --noinput' % env.current_release_dir)

	print(green('Symlinking current release'))
	run('rm -f %s' % env.current_dir)
	run('ln -s %s %s' % (env.current_release_dir, env.current_dir))

	print(green('Restarting app'))
	run('touch %s/connector.wsgi' % env.current_dir)

	print(green('Removing obsolete releases and backups'))
	with cd(env.release_dir):
		run('ls -t | tail -n +%d | xargs rm -rf' % (env.releases_to_keep + 1))
	with cd(env.backup_dir):
		run('ls -t | tail -n +%d | xargs rm -f' % (env.backups_to_keep + 1))


def backup():
	"""
	Trigger remote DB backup
	"""

	if files.exists(env.current_dir):
		print(green('Backing up database'))
		with cd(env.current_release_dir):
			_run_ve('fab prod backup_db:timestamp=%s' % env.release_timestamp)


@task
def backup_db(timestamp):
	"""
	Backs up DB (run on remote only)
	"""

	# Add project to path and retrieve settings
	sys.path.append(env.current_dir)
	django.settings_module('settings.active')
	from django.conf import settings

	# Run pg_dump on DB
	local('pg_dump -c -U %s %s > %s/%s.sql' % (
		settings.DATABASES['default']['USER'],
		settings.DATABASES['default']['NAME'],
		env.backup_dir,
		timestamp
	))


@task
def deploy():
	"""
	Deploy to server
	"""
	check_requirements()
	setup()
	update_code()
	prepare_release()
	backup()
	finalise()


@task
def rollback():
	"""
	Rollback to previous release
	"""
	pass


def _run_ve(command):
	with prefix('source %s/bin/activate' % env.env_dir):
		run(command)


def select_tag():
	# Push and fetch tags
	local('git push --tags')
	local('git fetch --tags')

	# Get last 5 tags and prompt for which to use
	tags = local('git tag | sort -V | tail -5', capture=True)
	print(yellow('Available tags: %s' % ', '.join(tags.split())))
	latest = tags.split().pop()
	refspec = prompt(blue('Choose tag to build from: '), default=latest)

	# Check tag is valid
	local('git tag | grep "%s"' % refspec)

	return refspec
