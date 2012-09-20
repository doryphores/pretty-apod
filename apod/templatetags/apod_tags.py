from django import template
from django.conf import settings

from ..models import Picture

import calendar
import re

register = template.Library()


@register.simple_tag
def timestamp():
	return settings.TIMESTAMP


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


def picture_url(match):
	try:
		p = Picture.objects.get_by_apodurl(match.group(0))
	except Picture.DoesNotExist:
		# Don't know what to do here
		pass
	return p.get_absolute_url()


@register.filter
def apod_html(html):
	# Trim href attributes
	html = re.sub(r'href="\s*([^"]+)\s*"', r'href="\1"', html)
	# Convert APOD links to PRETTY APOD links
	html = re.sub(r'ap[0-9]{6}\.html', picture_url, html)
	# Convert relative links to point to actual page on APOD site
	html = re.sub(r'href="((?!(http|/))[^"]+)"', r'href="%s/\1"' % settings.APOD_URL, html)
	return html
apod_html.is_safe = True
