from django.db import models
from django.core.files.base import ContentFile

from sorl.thumbnail import get_thumbnail

import os
import urllib2
import re

from apod import apodapi


# Models

class Keyword(models.Model):
	label = models.CharField(max_length=400, unique=True)

	def __unicode__(self):
		return u'%s' % self.label

	class Meta:
		ordering = ['label']


def get_image_path(instance, filename):
	return os.path.join('images', str(instance.publish_date.year), str(instance.publish_date.month), filename)

class Photo(models.Model):
	publish_date = models.DateField(unique=True)
	title = models.CharField(max_length=255)
	explanation = models.TextField(max_length=4000, blank=True)
	credits = models.TextField(max_length=4000, blank=True)
	original_image_url = models.URLField(blank=True)
	image = models.ImageField(upload_to=get_image_path, width_field="image_width", height_field="image_height", blank=True, null=True)
	image_width = models.PositiveSmallIntegerField(editable=False, null=True)
	image_height = models.PositiveSmallIntegerField(editable=False, null=True)
	loaded = models.BooleanField(default=False, verbose_name='Loaded from APOD')

	keywords = models.ManyToManyField(Keyword, related_name='photos')

	@models.permalink
	def get_absolute_url(self):
		return ('image', (), { 'image_id': str(self.pk) })

	def __unicode__(self):
		return u'%s' % self.title
	
	def get_apod_url(self):
		return apodapi.get_apod_url(self.publish_date)

	def load_from_apod(self, force=False):
		details = apodapi.get_apod_details(self.publish_date, force)
		
		if details['title']:
			self.title = details['title']
		self.explanation = details['explanation']
		self.credits = details['credits']
		self.original_image_url = details['image_url']
		self.loaded = True
		
		self.keywords.clear()
		
		for word in details['keywords']:
			try:
				keyword = Keyword.objects.get(label__iexact=word.strip())
			except Keyword.DoesNotExist:
				keyword = Keyword.objects.create(label=word.strip())
			self.keywords.add(keyword)

		self.save()
	
	def get_image(self, force=False):
		if self.original_image_url and (force or not self.image):
			# Download the image
			# @TODO: handle errors
			try:
				f = urllib2.urlopen(self.original_image_url)
				self.image.save(self.original_image_url.split('/')[-1], ContentFile(f.read()))
			except urllib2.HTTPError as error:
				if error.code == 404:
					# Reset image URL if not found
					self.original_image_url = ''
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