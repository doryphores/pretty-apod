from django import template

import calendar

register = template.Library()

@register.filter
def month_name(month_number):
    return calendar.month_name[month_number]