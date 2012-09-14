from django.db import models
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.db.models.signals import post_delete, pre_save, post_save
from django.db.models import Count, Min, Max
from django.db import connection
from django.dispatch import receiver

from sorl.thumbnail import get_thumbnail, delete as delete_image

import os
import urllib2
import re
import json
import Image
import datetime

from apod import apodapi


class TagFormatter(models.Model):
	label = models.CharField(max_length=400)
	pattern = models.CharField(max_length=400)
	format = models.CharField(max_length=400)

	def run(self, label_to_format):
		p = re.compile(self.pattern, re.I)
		if re.match(p, label_to_format):
			label_to_format = re.sub(p, self.format, label_to_format)
		return label_to_format

	def __unicode__(self):
		return u'%s' % self.label


class TagManager(models.Manager):
	FORMATTERS_CACHE_KEY = 'TAG_FORMATTERS'

	@property
	def formatters(self):
		"""
		Returns all TagFormatter records as queryset
		QuerySet is cached for performance
		"""
		if cache.get(self.FORMATTERS_CACHE_KEY):
			formatters = cache.get(self.FORMATTERS_CACHE_KEY)
		else:
			formatters = TagFormatter.objects.all()
			cache.set(self.FORMATTERS_CACHE_KEY, formatters)

		return formatters

	@classmethod
	def refresh_formatters(cls):
		"""
		Removes the TagFormatter QuerySet from cache
		Called via post_save and post_delete signals
		"""
		cache.delete(cls.FORMATTERS_CACHE_KEY)

	@classmethod
	def get_slug(cls, label):
		return re.sub(r'[\W^_]+', '-', label.replace('*', '-star').lower()).strip('-')

	def get_or_create_from_label(self, label):
		"""
		Runs label through tag formatters first
		and returns existing tag or creates a new one
		"""
		# Strip and collapse spaces
		label = label.strip()
		label = re.sub(r'\s{2,}', ' ', label)

		for f in self.formatters:
			label = f.run(label)

		slug = self.get_slug(label)

		try:
			existing = self.get(slug=slug)
			if existing.label > label:
				existing.label = label
				existing.save()
			return existing

		except Tag.DoesNotExist:
			return self.create(label=label, slug=slug)

	def format_labels(self):
		obsolete_count = 0
		formatted_count = 0

		for f in self.formatters:
			tags = self.filter(label__iregex=f.pattern).order_by('-label')

			# Build groups of duplicate tags
			groups = {}
			for tag in tags:
				formatted_label = re.sub(re.compile(f.pattern, re.I), f.format, tag.label)
				slug = self.get_slug(formatted_label)
				if slug in groups:
					groups[slug][1].append(tag)
				else:
					groups[slug] = (formatted_label, [tag])

			# Iterate over groups
			for slug in groups:
				formatted_label, tags = groups[slug]
				# Select one as primary
				primary = tags.pop()
				# Iterate over others
				for tag in tags:
					# Switch to primary tag
					for picture in tag.pictures.all():
						obsolete_count = obsolete_count + 1
						picture.tags.remove(tag)
						picture.tags.add(primary)
					# Delete obsolete tag
					tag.delete()
				# Update primary label to formatted version
				if primary.label != formatted_label:
					formatted_count = formatted_count + 1
					primary.label = formatted_label
					primary.save()

		return (obsolete_count, formatted_count)

	def get_top_tags(self, threshold):
		tags = self.annotate(num_pictures=Count('pictures')).filter(num_pictures__gt=threshold)

		min_max = tags.aggregate(Min('num_pictures'), Max('num_pictures'))

		return {
			'tags': tags,
			'min': min_max['num_pictures__min'],
			'max': min_max['num_pictures__max']
		}


# Clear formatter cache when formatters are updated

@receiver(post_delete, sender=TagFormatter)
@receiver(post_save, sender=TagFormatter)
def refresh_formatters(sender, **kwargs):
	TagManager.refresh_formatters()


class Tag(models.Model):
	label = models.CharField(max_length=400, unique=True)
	slug = models.CharField(max_length=400, unique=True)

	objects = TagManager()

	@models.permalink
	def get_absolute_url(self):
		return ('tag', (), {
			'tag': self.slug,
		})

	def __unicode__(self):
		return u'%s' % self.label

	class Meta:
		ordering = ['slug']


class PictureManager(models.Manager):
	@classmethod
	def dictfetchall(cls, cursor):
		"Returns all rows from a cursor as a dict"
		desc = cursor.description
		return [
			dict(zip([col[0] for col in desc], row))
			for row in cursor.fetchall()
		]

	def get_by_apodurl(self, apodurl):
		"""
		Returns Picture matching the APOD url (apYYMMDD.html)
		"""
		try:
			date = datetime.datetime.strptime(apodurl, 'ap%y%m%d.html')
		except ValueError:
			raise Picture.DoesNotExist

		return self.get(publish_date=date)

	def get_size_over_time(self):
		cursor = connection.cursor()

		cursor.execute("""
			SELECT	DATE (date_part('year', publish_date) || '-' || date_part('month', publish_date) || '-1'),
					ROUND(AVG(original_width::integer * original_height::integer) / 1000000, 2)::float AS size
			FROM	apod_picture
			WHERE	media_type = 'IM'
			GROUP BY date_part('year', publish_date), date_part('month', publish_date)
			ORDER BY date_part('year', publish_date), date_part('month', publish_date)
		""")

		return self.dictfetchall(cursor)


# Dynamic path for image storage
def get_image_path(instance, filename):
	return os.path.join('pictures',
						str(instance.publish_date.year),
						str(instance.publish_date.month),
						filename)


# Media types
MEDIA_TYPES = (
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

	media_type = models.CharField(max_length=2, choices=MEDIA_TYPES, default='UN')

	# Image data
	original_image_url = models.URLField(blank=True)
	original_file_size = models.PositiveIntegerField(default=0)
	original_width = models.PositiveSmallIntegerField(null=True, blank=True)
	original_height = models.PositiveSmallIntegerField(null=True, blank=True)
	image = models.ImageField(
		upload_to=get_image_path,
		width_field='image_width',
		height_field='image_height',
		blank=True,
		null=True)
	image_width = models.PositiveSmallIntegerField(editable=False, null=True)
	image_height = models.PositiveSmallIntegerField(editable=False, null=True)

	# Video data
	video_id = models.URLField(blank=True, null=True)

	loaded = models.BooleanField(default=False, verbose_name='Loaded from APOD')

	tags = models.ManyToManyField(Tag, related_name='pictures')

	objects = PictureManager()

	_current_tag = None

	@models.permalink
	def get_absolute_url(self):
		params = {
			'year': str(self.publish_date.year),
			'month': str(self.publish_date.month),
			'day': str(self.publish_date.day),
		}
		url = 'picture'
		if self.current_tag:
			params['tag'] = self.current_tag.slug
			url = 'tag_picture'

		return (url, (), params)

	@models.permalink
	def get_json_url(self):
		return ('picture_json', (), {
			'picture_id': self.pk
		})

	@models.permalink
	def get_month_url(self):
		params = {
			'year': str(self.publish_date.year),
			'month': str(self.publish_date.month),
		}
		url = 'month'
		if self.current_tag:
			params['tag'] = self.current_tag.slug
			url = 'tag_month'

		return (url, (), params)

	@models.permalink
	def get_year_url(self):
		params = {
			'year': str(self.publish_date.year),
		}
		url = 'year'
		if self.current_tag:
			params['tag'] = self.current_tag.slug
			url = 'tag_year'

		return (url, (), params)

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

		self.tags.clear()

		for word in details['keywords']:
			self.tags.add(Tag.objects.get_or_create_from_label(label=word))

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
					resized = get_thumbnail(self.image,
											'2000x2000',
											progressive=False,
											quality=90)

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
					f = urllib2.urlopen('http://vimeo.com/api/v2/video/%s.json'
										% self.video_id)
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

	def is_video(self):
		return self.media_type in ['YT', 'VI']

	@property
	def month(self):
		return self.publish_date.replace(day=1)

	@property
	def next(self):
		try:
			if self.current_tag:
				next = self.get_next_by_publish_date(tags=self.current_tag)
				next.current_tag = self.current_tag
				return next
			else:
				return self.get_next_by_publish_date()
		except Picture.DoesNotExist:
			return None

	@property
	def previous(self):
		try:
			if self.current_tag:
				previous = self.get_previous_by_publish_date(tags=self.current_tag)
				previous.current_tag = self.current_tag
				return previous
			else:
				return self.get_previous_by_publish_date()
		except Picture.DoesNotExist:
			return None

	def current_tag():
		def fget(self):
			return self._current_tag

		def fset(self, value):
			self._current_tag = value

		def fdel(self):
			del self._current_tag
		return locals()
	current_tag = property(**current_tag())

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
