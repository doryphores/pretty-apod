from django import template

import calendar
import math

register = template.Library()

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