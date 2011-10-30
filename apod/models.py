from django.db import models
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files import File
from django.conf import settings

from apod import api

import os
import urllib2
import re

from BeautifulSoup import BeautifulSoup as BSoup
from dateutil import parser as dateparser


# Managers

class PhotoManager(models.Manager):
	def import_archive(self, force_download=False):
		# Wrap the whole thing in a transaction

		transaction.commit_unless_managed()
		transaction.enter_transaction_management()
		transaction.managed(True)

		try:
			for apod in api.get_archive_list():
				photo = Photo(publish_date=apod["publish_date"], title=apod["title"])
				photo.save()
		except:
			transaction.rollback()
			transaction.leave_transaction_management()
			raise
		
		transaction.commit()
		transaction.leave_transaction_management()


# Models

class Photo(models.Model):
	publish_date = models.DateField(unique=True)
	title = models.CharField(max_length=255)
	description = models.CharField(max_length=4000, blank=True)
	credit = models.CharField(max_length=255, blank=True)
	original_image_url = models.URLField(blank=True)
	image = models.ImageField(upload_to='images', blank=True, null=True)

	objects = PhotoManager()

	@models.permalink
	def get_absolute_url(self):
		return ('image_view', (), { 'image_id': str(self.pk) })

	def __unicode__(self):
		return u'%s' % self.title
	
	def get_apod_url(self):
		return u'%s/ap%s.html' % (settings.APOD_URL, self.publish_date.strftime('%y%m%d'))

	def load_from_apod(self, force=False):
		details = api.get_apod_details(self.publish_date)
		
		self.title = details['title']
		self.description = details['explanation']
		self.credits = details['credits']
		self.original_image_url = details['image_url']

		if force or not self.image:
			# Download the image
			f = urllib2.urlopen(self.original_image_url)
			self.image.save(os.path.basename(self.original_image_url), ContentFile(f.read()))
		
		self.save()

	@property
	def next(self):
		try:
			return self.get_next_by_publish_date()
		except Photo.DoesNotExist:
			return None
	
	@property
	def previous(self):
		try:
			return self.get_previous_by_publish_date()
		except Photo.DoesNotExist:
			return None
	
	class Meta:
		ordering = ['-publish_date']