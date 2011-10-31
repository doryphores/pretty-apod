from django.db import models
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from sorl.thumbnail import ImageField

from apod import apodapi

import os
import urllib2
import re


# Managers

class PhotoManager(models.Manager):
	def import_archive(self, force_download=False):
		try:
			from_date = self.latest().publish_date
		except:
			from_date = None
		for apod in apodapi.get_archive_list(from_date=from_date):
			photo = Photo(publish_date=apod["publish_date"], title=apod["title"])
			photo.save()


# Models

class Photo(models.Model):
	publish_date = models.DateField(unique=True)
	title = models.CharField(max_length=255)
	explanation = models.TextField(max_length=4000, blank=True)
	credits = models.TextField(max_length=4000, blank=True)
	original_image_url = models.URLField(blank=True)
	image = ImageField(upload_to='images', blank=True, null=True)
	loaded = models.BooleanField(default=False)

	objects = PhotoManager()

	@models.permalink
	def get_absolute_url(self):
		return ('image_view', (), { 'image_id': str(self.pk) })

	def __unicode__(self):
		return u'%s' % self.title
	
	def get_apod_url(self):
		return apodapi.get_apod_url(self.publish_date)

	def load_from_apod(self, download_image=False):
		details = apodapi.get_apod_details(self.publish_date)
		
		self.title = details['title']
		self.explanation = details['explanation']
		self.credits = details['credits']
		self.original_image_url = details['image_url']
		self.loaded = True
		
		if download_image and not self.image and self.original_image_url:
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
		get_latest_by = 'publish_date'