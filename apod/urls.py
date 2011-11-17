from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apod.views',
	url(r'^$', 'image', name='home'),
	url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'image', name='image'),
	url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'month', name='month'),
	url(r'^(?P<year>\d{4})/$', 'year', name='year'),
	url(r'^archive/$', 'archive', name="archive"),
	url(r'^archive/(?P<page>\d+)/$', 'archive', name="archive_page"),
	url(r'^tags/$', 'tags', name="tag_view"),

	url(r'^ajax/picture/(?P<picture_id>\d+)/$', 'image_only', name='image_only'),
)