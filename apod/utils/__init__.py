import time

from django.utils.http import http_date


def format_http_date(date):
	return http_date(time.mktime(date.timetuple()))
