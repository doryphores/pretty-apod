from django.conf.urls.defaults import patterns, url, include
from apod.feeds import LatestPicturesFeed, TagPicturesFeed
from apod.api import PictureResource

picture_resource = PictureResource()

urlpatterns = patterns('apod.views',
	url(r'^$', 'picture', name='home'),
	url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'picture', name='picture'),

	url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'month', name='month'),
	url(r'^(?P<year>\d{4})/$', 'year', name='year'),

	url(r'^tags/$', 'tags', name='tags'),
	url(r'^tags/(?P<tag>[\w\-]+)/$', 'archive', name='tag'),
	url(r'^tags/(?P<tag>[\w\-]+)/feed/$', TagPicturesFeed(), name='tag_feed'),
	url(r'^tags/(?P<tag>[\w\-]+)/page(?P<page>\d+)/$', 'archive', name='tag_page'),
	url(r'^tags/(?P<tag>[\w\-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'archive', name='tag_month'),
	url(r'^tags/(?P<tag>[\w\-]+)/(?P<year>\d{4})/$', 'archive', name='tag_year'),
	url(r'^tags/(?P<tag>[\w\-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'picture', name='tag_picture'),

	url(r'^stats/$', 'stats', name='stats'),

	url(r'^ajax/picture/(?P<picture_id>\d+)/$', 'picture_json', name='picture_json'),
	url(r'^ajax/size-over-time/$', 'size_over_time', name='size_over_time'),

	url(r'^feed/$', LatestPicturesFeed(), name='feed'),

	(r'^api/', include(picture_resource.urls)),
)
