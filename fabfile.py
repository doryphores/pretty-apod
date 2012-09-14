import os
import datetime

from fabric.api import *
from fabric.context_managers import prefix
from fabric.contrib import django
#from fabric.contrib.console import confirm

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


def update_code():
	with cd(repo_dir):
		run('git pull')


def prepare_release():
	# Create new release folder and copy code
	run('mkdir -p %s' % current_release_dir)
	run('cp -R %s/* %s' % (repo_dir, current_release_dir))

	# Symlink shared assets
	run('ln -s %s/media %s/media' % (shared_dir, current_release_dir))
	run('ln -s %s/logs %s/logs' % (shared_dir, current_release_dir))
	run('ln -s %s/active.py %s/settings/active.py' % (shared_dir, current_release_dir))

	with prefix('source %s/bin/activate' % env_dir):
		# Collect static assets
		run('%s/manage.py collectstatic --noinput --verbosity=0' % current_release_dir)


def finalise():
	# Make release current
	run('rm %s' % current_dir)
	run('ln -s %s %s' % (current_release_dir, current_dir))

	# Force app to reload
	run('touch %s/public/connector.wsgi' % current_dir)


def backup():
	run('fab _backup')


def _backup():
	django.settings_module('myproject.settings')
	from django.conf import settings

	local('pgdump %s > %s/%s.sql' % (
		settings.DATABASE_NAME,
		backup_dir,
		release_timestamp
	))


def deploy():
	update_code()
	prepare_release()
	backup()
	finalise()
