from tastypie.resources import ModelResource

from django.conf.urls.defaults import url
from django.http import Http404

from apod.models import *

import datetime


class PictureResource(ModelResource):
	class Meta:
		queryset = Picture.objects.all()

	def dispatch(self, request_type, request, **kwargs):
		# year = int(kwargs.pop('year'))
		# month = int(kwargs.pop('month'))
		# day = int(kwargs.pop('day'))
		# try:
		# 	d = datetime.date(year, month, day)
		# except ValueError:
		# 	raise Http404

		kwargs['publish_date'] = datetime.date.today()

		return super(PictureResource, self).dispatch(request_type, request, **kwargs)

	def prepend_urls(self):
		return [
			url(r'^(?P<resource_name>%s)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$' % self._meta.resource_name, self.wrap_view('dispatch_detail'), name='api_dispatch_detail'),
		]
