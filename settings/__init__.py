import os

# Django settings for pretty_apod project.

PROJECT_ROOT = '/'.join(os.path.dirname(__file__).split('/')[0:-1])

INTERNAL_IPS = ('127.0.0.1',)

ADMINS = (
	# ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "public", "assets")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/assets/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "public", "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Additional locations of static files
STATICFILES_DIRS = (
	os.path.join(PROJECT_ROOT, "ui", "assets"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
# IMPORTANT! In production, this is set in local active.py
SECRET_KEY = '=gsimol1xt7w9q!8(##!nzb5!05s(6g(z^^!b6m&im7m0afge5'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.contrib.auth.context_processors.auth',
	'django.core.context_processors.i18n',
	'django.core.context_processors.media',
	'django.core.context_processors.static',
	#'django.core.context_processors.tz',
	'django.contrib.messages.context_processors.messages',
	'django.core.context_processors.debug',
	'django.core.context_processors.request',
	'apod.context_processors.timestamp',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.transaction.TransactionMiddleware',
	'django.middleware.http.ConditionalGetMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
	os.path.join(PROJECT_ROOT, 'templates'),
)

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.admin',
	'south',
	'apod',
	'sorl.thumbnail',
)

LOGGING = {
	'version': 1,
	'disable_existing_loggers': True,
	'formatters': {
		'standard': {
			'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
		},
	},
	'handlers': {
		'default': {
			'level': 'DEBUG',
			'class': 'logging.handlers.RotatingFileHandler',
			'filename': os.path.join(PROJECT_ROOT, 'logs', 'django.log'),
			'maxBytes': 1024 * 512,  # 500 KB
			'backupCount': 5,
			'formatter': 'standard',
		},
		'request_handler': {
			'level': 'DEBUG',
			'class': 'logging.handlers.RotatingFileHandler',
			'filename': os.path.join(PROJECT_ROOT, 'logs', 'django_request.log'),
			'maxBytes': 1024 * 512,  # 500 KB
			'backupCount': 5,
			'formatter': 'standard',
		},
		'mail_admins': {
			'level': 'ERROR',
			'class': 'django.utils.log.AdminEmailHandler',
		}
	},
	'loggers': {
		'': {
			'handlers': ['default'],
			'level': 'DEBUG',
			'propagate': True
		},
		'django.db.backends': {  # Stop SQL debug from logging to main logger
			'handlers': ['request_handler'],
			'level': 'DEBUG',
			'propagate': False
		},
	}
}

# Session config

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SESSION_COOKIE_AGE = 3600

THUMBNAIL_UPSCALE = False

# Empty deploy timestamp

TIMESTAMP = ''

# APOD config

APOD_URL = "http://apod.nasa.gov/apod"

APOD_ARCHIVE_URL = APOD_URL + "/archivepix.html"
