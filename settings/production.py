from settings import *

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
		'LOCATION': 'unix:/home/doryphores/memcached.sock',
		'KEY_PREFIX': 'PRETTY_APOD',
		'VERSION'	: 1,
	}
}

LOGGING['loggers']['django.request'] = {
	'handlers': ['mail_admins'],
	'level': 'ERROR',
	'propagate': False,
}

STATIC_URL = '/static/assets/'
MEDIA_URL = '/static/media/'
