import sys
import os
import datetime

from fabric.api import *
from fabric.context_managers import prefix
from fabric.contrib import django
from fabric.colors import *

env.hosts = ['staging.apod']

project_dir = '/home/martin/pretty-apod'
env_dir = os.path.join(project_dir, 'env')
backup_dir = os.path.join(project_dir, 'backup')
repo_dir = os.path.join(project_dir, 'repo')
release_dir = os.path.join(project_dir, 'releases')
shared_dir = os.path.join(project_dir, 'shared')
current_dir = os.path.join(project_dir, 'current')

release_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
current_release_dir = os.path.join(release_dir, release_timestamp)

releases_to_keep = 3
backups_to_keep = 3


def update_env():
	"""
	Updates virtual environment requirements
	"""
	print(green('Updating virtual environment requirements'))
	with prefix('source %s/bin/activate' % env_dir):
		run('pip install -q -r %s/install/requirements.txt' % current_release_dir)


def update_code():
	"""
	Updates code from repository
	"""
	print(green('Updating code from repository'))
	with cd(repo_dir):
		run('git pull')


def prepare_release():
	"""
	Prepares new release for deployment
	"""

	print(green('Preparing release'))
	# Create new release folder and copy code
	run('mkdir -p %s' % current_release_dir)
	run('cp -R %s/* %s' % (repo_dir, current_release_dir))

	print(green('Symlinking shared assets'))
	# Symlink shared assets
	run('ln -s %s/media %s/media' % (shared_dir, current_release_dir))
	run('ln -s %s/logs %s/logs' % (shared_dir, current_release_dir))
	run('ln -s %s/active.py %s/settings/active.py' % (shared_dir, current_release_dir))

	update_env()

	with prefix('source %s/bin/activate' % env_dir):
		# Collect static assets
		print(green('Collecting static assets'))
		run('%s/manage.py collectstatic --noinput --verbosity=0' % current_release_dir)

	print(green('Removing obsolete releases'))
	with cd(release_dir):
		run('ls -t | tail -n +%d | xargs rm -rf' % (releases_to_keep + 1))


def finalise():
	"""
	Runs DB migrations, symlinks new release and restarts app
	"""

	# Migrate DB
	with prefix('source %s/bin/activate' % env_dir):
		print(green('Running database migrations'))
		run('%s/manage.py migrate --noinput' % current_release_dir)

	print(green('Symlinking current release'))
	# Make release current
	run('rm %s' % current_dir)
	run('ln -s %s %s' % (current_release_dir, current_dir))

	print(green('Restarting app'))
	# Force app to reload
	run('touch %s/public/connector.wsgi' % current_dir)


def backup():
	"""
	Trigger remote DB backup
	"""

	print(green('Backing up database'))
	with prefix('source %s/bin/activate' % env_dir):
		with cd(current_release_dir):
			run('fab backup_db')

	print(green('Removing obsolete backups'))
	with cd(backup_dir):
		run('ls -t | tail -n +%d | xargs rm -f' % (backups_to_keep + 1))


@task
def backup_db():
	"""
	Backs up DB (run on remote only)
	"""
	sys.path.append(current_dir)
	django.settings_module('settings.active')
	from django.conf import settings

	local('pg_dump %s > %s/%s.sql' % (
		settings.DATABASES['default']['NAME'],
		backup_dir,
		release_timestamp
	))


@task
def deploy():
	"""
	Deploy to servers
	"""
	update_code()
	prepare_release()
	backup()
	finalise()
