from django import template
from django.conf import settings

from ..models import Picture

import calendar
import re

register = template.Library()


@register.simple_tag
def timestamp():
	return settings.TIMESTAMP


@register.simple_tag(takes_context=True)
def abs_url(context, url):
	return context['request'].build_absolute_uri(url)


@register.filter
def month_name(month_number):
	return calendar.month_name[month_number]

CLOUD_CLASSES = ['xxs', 'xs', 's', 'l', 'xl', 'xxl']


@register.simple_tag
def cloud_class(count, min_count, max_count):
	count = float(count)
	min_count = float(min_count)
	max_count = float(max_count)

	step = (max_count - min_count) / 5

	return CLOUD_CLASSES[int(round((count - min_count) / step))]


@register.tag(name="apodhtml")
def do_apodhtml(parser, token):
	tokens = token.split_contents()

	absolute_urls = False

	if len(tokens) == 2:
		tag_name, absolute_urls = tokens

	nodelist = parser.parse(('endapodhtml',))
	parser.delete_first_token()
	return ApodHTML(nodelist, absolute_urls)


class ApodHTML(template.Node):
	def __init__(self, nodelist, absolute_urls=False):
		self.nodelist = nodelist
		self.absolute_urls = absolute_urls

	def render(self, context):
		output = self.nodelist.render(context)

		# Trim href attributes
		output = re.sub(r'href="\s*([^"]+)\s*"', r'href="\1"', output)

		self.context = context

		# Convert APOD links to PRETTY APOD links
		output = re.sub(r'ap[0-9]{6}\.html', self.picture_url, output)
		# Convert relative links to point to actual page on APOD site
		output = re.sub(r'href="((?!(http|/))[^"]+)"', r'href="%s/\1"' % settings.APOD_URL, output)

		return output

	def picture_url(self, match):
		try:
			p = Picture.objects.get_by_apodurl(match.group(0))
		except Picture.DoesNotExist:
			# Don't know what to do here
			pass

		if self.absolute_urls:
			return self.context['request'].build_absolute_uri(p.get_absolute_url())

		return p.get_absolute_url()
