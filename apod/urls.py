from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apod.views',
	url(r'^$', 'picture', name='home'),
	url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'picture', name='picture'),
	url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'month', name='month'),
	url(r'^(?P<year>\d{4})/$', 'year', name='year'),
	url(r'^tags/$', 'tags', name='tags'),
	url(r'^tags/(?P<tag>[\w\-]+)/$', 'tag', name='tag'),
	url(r'^tags/(?P<tag>[\w\-]+)/page(?P<page>\d+)/$', 'tag', name='tag_page'),
	url(r'^tags/(?P<tag>[\w\-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'picture', name='tag_picture'),
	url(r'^tags/(?P<tag>[\w\-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'tag', name='tag_month'),
	url(r'^tags/(?P<tag>[\w\-]+)/(?P<year>\d{4})/$', 'tag', name='tag_year'),

	url(r'^ajax/picture/(?P<picture_id>\d+)/$', 'picture_json', name='picture_json'),
)