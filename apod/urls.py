from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apod.views',
	url(r'^$', 'list'),
	url(r'^refresh/$', 'refresh'),
	url(r'^image/(?P<image_id>\d+)/$', 'image', name='image_view'),
)