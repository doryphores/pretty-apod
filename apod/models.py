from django.db import models
from django.core.files.base import ContentFile
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from sorl.thumbnail import get_thumbnail, delete as delete_image

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

TYPES = (
	('IM', 'Image'),
	('YT', 'YouTube'),
	('VI', 'Vimeo'),
	('UN', 'Unknown'),
)

class Picture(models.Model):
	publish_date = models.DateField(unique=True)
	title = models.CharField(max_length=255)
	explanation = models.TextField(max_length=4000, blank=True)
	credits = models.TextField(max_length=4000, blank=True)

	media_type = models.CharField(max_length=2, choices=TYPES, default='UN')
	
	# Image data
	original_image_url = models.URLField(blank=True)
	original_file_size = models.PositiveIntegerField(default=0)
	original_width = models.PositiveSmallIntegerField(null=True, blank=True)
	original_height = models.PositiveSmallIntegerField(null=True, blank=True)
	image = models.ImageField(upload_to=get_image_path, width_field='image_width', height_field='image_height', blank=True, null=True)
	image_width = models.PositiveSmallIntegerField(editable=False, null=True)
	image_height = models.PositiveSmallIntegerField(editable=False, null=True)

	# Video data
	video_id = models.URLField(blank=True, null=True)

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

		if details['image_url']:
			self.original_image_url = details['image_url']
			self.media_type = 'IM'
		if details['youtube_id']:
			self.video_id = details['youtube_id']
			self.media_type = 'YT'
		if details['vimeo_id']:
			self.video_id = details['vimeo_id']
			self.media_type = 'VI'
		
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

				# Save original file size for stats
				self.original_file_size = int(f.headers['Content-Length'])

				# Get filename from URL
				filename = self.original_image_url.split('/')[-1]
				
				# Download original image
				self.image.save(filename, ContentFile(f.read()))

				# Save original dimensions
				self.original_width = self.image.width
				self.original_height = self.image.height

				# Check size and resize if bigger than 1Mb
				if self.original_file_size > 1024 * 1024:
					# Create a resized version
					resized = get_thumbnail(self.image, '2000x2000', progressive=False, quality=90)
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

	@property
	def thumb(self):
		if self.image:
			im = get_thumbnail(self.image, '120x90', crop='center', quality=85)
			return im.url
		
		if self.media_type == 'YT':
			return u'http://img.youtube.com/vi/%s/2.jpg' % self.video_id
		
		return
	
	def has_image(self):
		return len(self.original_image_url) > 0

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


# Signals for file management (deleting unused images and thumbnails)

@receiver(post_delete, sender=Picture)
def post_delete_picture(sender, **kwargs):
	instance = kwargs['instance']
	if instance.image:
		delete_image(instance.image)

@receiver(pre_save, sender=Picture)
def pre_save_picture(sender, **kwargs):
	instance = kwargs['instance']
	if instance.pk:
		old_instance = Picture.objects.get(pk=instance.pk)
		if old_instance.image and old_instance.image != instance.image:
			delete_image(old_instance.image)
