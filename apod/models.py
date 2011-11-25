from django.db import models
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver

from sorl.thumbnail import get_thumbnail, delete as delete_image

import os
import urllib2
import re
import json
import Image

from apod import apodapi

# Models

class KeywordFormatter(models.Model):
	label = models.CharField(max_length=400)
	pattern = models.CharField(max_length=400)
	format = models.CharField(max_length=400)

	def __unicode__(self):
		return u'%s' % self.label

class KeywordManager(models.Manager):
	FORMATTERS_CACHE_KEY = 'KEYWORD_FORMATTERS'

	@property
	def formatters(self):
		# Cache formatters for better performance
		# The cache is cleared on deletes and saves (via signals, see below)
		if cache.get(self.FORMATTERS_CACHE_KEY):
			formatters = cache.get(self.FORMATTERS_CACHE_KEY)
		else:
			formatters = KeywordFormatter.objects.all()
			cache.set(self.FORMATTERS_CACHE_KEY, formatters)
		
		return formatters

	@classmethod
	def refresh_formatters(cls):
		cache.delete(cls.FORMATTERS_CACHE_KEY)
	
	def get_or_create(self, label):
		label = label.strip()

		for f in self.formatters:
			p = re.compile(f.pattern, re.I)
			if re.match(p, label):
				label = re.sub(p, f.format, label)
				break
		
		try:
			return self.get(label__iexact=label)
		except Keyword.DoesNotExist:
			return self.create(label=label)

	def format_labels(self):
		obsolete_count = 0
		formatted_count = 0

		for f in self.formatters:
			keywords = self.filter(label__iregex=f.pattern)
			
			# Build groups of duplicate keywords
			groups = {}
			for k in keywords:
				formatted_label = re.sub(re.compile(f.pattern, re.I), f.format, k.label)
				if groups.has_key(formatted_label):
					groups[formatted_label].append(k)
				else:
					groups[formatted_label] = [k]
			
			# Iterate over groups
			for label in groups:
				# Select one as primary
				primary = groups[label].pop()
				# Iterate over others
				for k in groups[label]:
					# Switch to primary keyword
					for p in k.pictures.all():
						obsolete_count = obsolete_count + 1
						p.keywords.remove(k)
						p.keywords.add(primary)
					# Delete obsolete keyword
					k.delete()
				# Update primary label to formatted version
				if primary.label != label:
					formatted_count = formatted_count + 1
					primary.label = label
					primary.save()
		
		return (obsolete_count, formatted_count)

# Clear formatter cache when formatters are updated

@receiver(post_delete, sender=KeywordFormatter)
@receiver(post_save, sender=KeywordFormatter)
def refresh_formatters(sender, **kwargs):
	KeywordManager.refresh_formatters()


class Keyword(models.Model):
	label = models.CharField(max_length=400, unique=True)

	objects = KeywordManager()

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
			self.keywords.add(Keyword.objects.get_or_create(label=word))

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
				extension = filename.split('.')[-1].lower()

				# Read image file
				image_file = ContentFile(f.read())

				# Download and save original image
				self.image.save(filename, image_file, save=False)

				# Save original dimensions
				self.original_width = self.image.width
				self.original_height = self.image.height

				resize = True

				# Check whether image is animated GIF
				if extension == 'gif':
					gif = Image.open(self.image.file.name)
					try:
						gif.seek(1)
					except EOFError:
						pass
					else:
						# It's an animated GIF so leave as is
						resize = False

				# Check size and resize if bigger than 1Mb
				if resize and self.original_file_size > 1024 * 1024:
					# Create a resized version
					resized = get_thumbnail(self.image, '2000x2000', progressive=False, quality=90)

					# Delete original image
					self.image.delete(save=False)
					
					# Make jpg filename if needed
					if extension != 'jpg':
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
		
		if self.media_type == 'VI':
			cache_key = 'vimeo_thumb_%s' % self.video_id
			thumb_url = cache.get(cache_key)

			# Retrieve Vimeo thumb URL if not in cache
			if not thumb_url:
				try:
					# Call Vimeo API to get video info
					f = urllib2.urlopen('http://vimeo.com/api/v2/video/%s.json' % self.video_id)
				except urllib2.HTTPError:
					return None
				
				# Decode received JSON packet
				data = json.load(f)

				# Extract thumbnail URL
				thumb_url = data[0]['thumbnail_medium']

				# Store in cache for later
				cache.set(cache_key, thumb_url)
			
			return thumb_url

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