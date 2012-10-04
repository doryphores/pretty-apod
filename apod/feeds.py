from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.shortcuts import get_object_or_404

from apod.models import Picture, Tag
from apod.utils import get_last_modified

ITEMS_LIMIT = 20


class LatestPicturesFeed(Feed):
	feed_type = Atom1Feed
	title = 'Pretty APOD recent images'
	link = '/'
	description_template = 'feed_summary.html'

	def __call__(self, request, *args, **kwargs):
		response = super(LatestPicturesFeed, self).__call__(request, *args, **kwargs)
		response['Last-Modified'] = get_last_modified(self.items()[0].created_date)
		return response

	def items(self):
		return Picture.objects.all()[0:ITEMS_LIMIT]

	def item_pubdate(self, item):
		return item.created_date


class TagPicturesFeed(LatestPicturesFeed):
	def get_object(self, request, tag):
		return get_object_or_404(Tag, slug=tag)

	def link(self, tag):
		return tag.get_absolute_url()

	def title(self, tag):
		return 'Pretty APOD recent images tagged with "%s"' % tag

	def items(self, tag):
		return Picture.objects.filter(tags=tag)[0:ITEMS_LIMIT]
