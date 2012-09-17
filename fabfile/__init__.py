import sys
import os
import datetime

from fabric.api import *
from fabric.context_managers import prefix
from fabric.contrib import django, files
from fabric.colors import *


@task
def staging():
	"""
	Setup staging environment vars
	"""
	env.hosts = ['staging.apod']
	env.project_dir = '/home/martin/pretty-apod-2'
	env.python = 'python'
	env.pip = 'pip'


@task
def prod():
	"""
	Setup production environment vars
	"""
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
				'password': prompt(yellow('Database password:'))
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
		# run('%s install virtualenv' % env.pip)
		run('virtualenv -p %s --no-site-packages --system-site-packages %s' % (env.python, env.env_dir))
		run('virtualenv --relocatable %s' % env.env_dir)


def update_env():
	"""
	Updates virtual environment requirements
	"""
	print(green('Updating virtual environment requirements'))
	_run_ve('pip install -q -r %s/install/requirements.txt' % env.current_release_dir)


def update_code():
	"""
	Updates code from repository
	"""
	print(green('Updating code from repository'))
	with cd(env.repo_dir):
		run('git pull')


def prepare_release():
	"""
	Prepares new release for deployment
	"""

	print(green('Preparing release'))
	# Create new release folder and copy code
	run('mkdir -p %s' % env.current_release_dir)
	run('cp -R %s/* %s' % (env.repo_dir, env.current_release_dir))

	print(green('Symlinking shared assets'))
	# Symlink shared assets
	run('ln -s %s/media %s/public/media' % (env.shared_dir, env.current_release_dir))
	run('ln -s %s/logs %s/logs' % (env.shared_dir, env.current_release_dir))
	run('ln -s %s/active.py %s/settings/active.py' % (env.shared_dir, env.current_release_dir))

	update_env()

	# Collect static assets
	print(green('Collecting static assets'))
	_run_ve('%s/manage.py collectstatic --noinput --verbosity=0' % env.current_release_dir)

	print(green('Removing obsolete releases'))
	with cd(env.release_dir):
		run('ls -t | tail -n +%d | xargs rm -rf' % (env.releases_to_keep + 1))


def finalise():
	"""
	Runs DB migrations, symlinks new release and restarts app
	"""

	# Migrate DB
	print(green('Running database migrations'))
	_run_ve('%s/manage.py syncdb --migrate --noinput' % env.current_release_dir)

	print(green('Symlinking current release'))
	# Make release current
	run('rm -f %s' % env.current_dir)
	run('ln -s %s %s' % (env.current_release_dir, env.current_dir))

	print(green('Restarting app'))
	# Force app to reload
	run('touch %s/public/connector.wsgi' % env.current_dir)


def backup():
	"""
	Trigger remote DB backup
	"""

	if files.exists(env.current_dir):
		print(green('Backing up database'))
		with cd(env.current_release_dir):
			_run_ve('fab prod backup_db')

		print(green('Removing obsolete backups'))
		with cd(env.backup_dir):
			run('ls -t | tail -n +%d | xargs rm -f' % (env.backups_to_keep + 1))


@task
def backup_db():
	"""
	Backs up DB (run on remote only)
	"""
	sys.path.append(env.current_dir)
	django.settings_module('settings.active')
	from django.conf import settings

	local('pg_dump -U %s %s > %s/%s.sql' % (
		settings.DATABASES['default']['USER'],
		settings.DATABASES['default']['NAME'],
		env.backup_dir,
		env.release_timestamp
	))


@task
def deploy():
	"""
	Deploy to server
	"""
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
