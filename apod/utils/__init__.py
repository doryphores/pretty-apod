import time

from django.utils.http import http_date
from django.conf import settings


def get_last_modified(date):
	max_date = max(date, settings.LAST_MODIFIED)
	return http_date(time.mktime(max_date.timetuple()))
