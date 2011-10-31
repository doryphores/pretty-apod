from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apod.views',
	url(r'^$', 'list', name="first_page"),
	url(r'^(?P<page>\d+)/$', 'list', name="page"),
	url(r'^tags/$', 'tags', name="tag_view"),
	url(r'^image/(?P<image_id>\d+)/$', 'image', name='image_view'),
)