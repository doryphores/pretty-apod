from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apod.views',
	url(r'^$', 'list'),
	url(r'^refresh/$', 'refresh'),
)