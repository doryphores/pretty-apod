from datetime import datetime, time

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.shortcuts import get_object_or_404

from apod.models import Picture, Tag

ITEMS_LIMIT = 20


class LatestPicturesFeed(Feed):
	feed_type = Atom1Feed
	title = 'Pretty APOD recent images'
	link = '/'
	description_template = 'feed_summary.html'
	ttl = 60 * 24

	def items(self):
		return Picture.objects.all()[0:ITEMS_LIMIT]

	def item_pubdate(self, item):
		return datetime.combine(item.publish_date, time())


class TagPicturesFeed(LatestPicturesFeed):
	def get_object(self, request, tag):
		return get_object_or_404(Tag, slug=tag)

	def link(self, tag):
		return tag.get_absolute_url()

	def title(self, tag):
		return 'Pretty APOD recent images tagged with "%s"' % tag

	def items(self, tag):
		return Picture.objects.filter(tags=tag)[0:ITEMS_LIMIT]
