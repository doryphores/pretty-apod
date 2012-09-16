from settings.production import *

DATABASES = {
	'default': {
		'ENGINE'	: 'django.db.backends.postgresql_psycopg2',
		'NAME'		: '%(name)s',
		'USER'		: '%(user)s',
		'PASSWORD'	: '%(password)s',
		'HOST'		: '',
		'PORT'		: '',
	}
}
