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
	return os.path.join('pictures', str(instance.publish_date.year), str(instance.publish_date.month), filename)

class Picture(models.Model):
	publish_date = models.DateField(unique=True)
	title = models.CharField(max_length=255)
	explanation = models.TextField(max_length=4000, blank=True)
	credits = models.TextField(max_length=4000, blank=True)
	
	original_image_url = models.URLField(blank=True)
	original_file_size = models.PositiveIntegerField(default=0)
	image = models.ImageField(upload_to=get_image_path, width_field='image_width', height_field='image_height', blank=True, null=True)
	image_width = models.PositiveSmallIntegerField(editable=False, null=True)
	image_height = models.PositiveSmallIntegerField(editable=False, null=True)

	youtube_url = models.URLField(blank=True)

	loaded = models.BooleanField(default=False, verbose_name='Loaded from APOD')

	keywords = models.ManyToManyField(Keyword, related_name='pictures')

	@models.permalink
	def get_absolute_url(self):
		return ('image', (), {
			'year': str(self.publish_date.year),
			'month': str(self.publish_date.month),
			'day': str(self.publish_date.day),
		})

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
		self.youtube_url = details['youtube_url']
		self.loaded = True
		
		self.keywords.clear()
		
		for word in details['keywords']:
			try:
				keyword = Keyword.objects.get(label__iexact=word.strip())
			except Keyword.DoesNotExist:
				keyword = Keyword.objects.create(label=word.strip())
			self.keywords.add(keyword)

		self.save()
	
	def get_image(self):
		if self.original_image_url and not self.image:
			# Download the image
			# @TODO: handle errors
			try:
				f = urllib2.urlopen(self.original_image_url)

				# Save original file size for stats
				self.original_file_size = int(f.headers['Content-Length'])

				# Get filename from URL
				filename = self.original_image_url.split('/')[-1]
				
				# Download original image
				self.image.save(filename, ContentFile(f.read()))

				# Check size and resize if bigger than 1Mb
				if self.original_file_size > 1024 * 1024:
					# Create a resized version
					resized = get_thumbnail(self.image, '2000x2000')
					# Delete the original
					self.image.delete()
					# Make jpg filename if needed
					if filename.split('.')[-1].lower() is not 'jpg':
						filename = re.sub('\.[^\.]+$', '.jpg', filename)
					# Save the resized version
					self.image.save(filename, ContentFile(resized.read()))
				
			except urllib2.HTTPError as error:
				if error.code == 404:
					# Reset image URL if not found
					self.original_image_url = ''
			
			self.save()

	def has_image(self):
		return len(self.original_image_url) > 0

	@property
	def type(self):
		if self.original_image_url:
			return 'image'
		if self.youtube_url:
			return 'youtube'
		return None

	@property
	def next(self):
		try:
			return self.get_next_by_publish_date()
		except Picture.DoesNotExist:
			return None
	
	@property
	def previous(self):
		try:
			return self.get_previous_by_publish_date()
		except Picture.DoesNotExist:
			return None
	
	class Meta:
		ordering = ['-publish_date']
		get_latest_by = 'publish_date'
