from django.db import models
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files import File
from django.conf import settings

import os
import urllib2
import re

from BeautifulSoup import BeautifulSoup as BSoup
from dateutil import parser as dateparser


# Managers

class ItemManager(models.Manager):
	def import_archive(self, force_download=False):
		cache_fn = 'cache/archive.html'
		
		# Download archive HTML if needed
		if force_download or not default_storage.exists(cache_fn):
			f = urllib2.urlopen(settings.APOD_ARCHIVE_URL)
			html = f.read()
			
			# Write HTML to disk
			default_storage.save(cache_fn, ContentFile(html))
		
		# Read HTML
		with default_storage.open(cache_fn) as f:
			html = f.read()
		
		html_soup = BSoup(html)
		archive_links = html_soup.b.findAll("a")

		# Wrap the whole thing in a transaction to speed things up

		transaction.commit_unless_managed()
		transaction.enter_transaction_management()
		transaction.managed(True)

		try:
			for link in archive_links:
				item = Item()
				item.publish_date = dateparser.parse(link.previous.strip().strip(":"))
				item.title = unicode(link.next)
				item.save()
		except:
			transaction.rollback()
			transaction.leave_transaction_management()
			raise
		
		transaction.commit()
		transaction.leave_transaction_management()


# Models

class Item(models.Model):
	publish_date = models.DateField(unique=True)

	title = models.CharField(max_length=255)
	description = models.CharField(max_length=4000, blank=True)
	credit = models.CharField(max_length=255, blank=True)
	image = models.ImageField(upload_to='images', blank=True, null=True)

	objects = ItemManager()

	@models.permalink
	def get_absolute_url(self):
		return ('image_view', (), { 'image_id': str(self.pk) })

	def __unicode__(self):
		return u'%s' % self.title
	
	def get_apod_url(self):
		return u'%s/ap%s.html' % (settings.APOD_URL, self.publish_date.strftime('%y%m%d'))

	def load_from_apod(self, force=False):
		# Get APOD HTML page
		f = urllib2.urlopen(self.get_apod_url())

		# Parse it with Beautiful Soup
		soup = BSoup(f.read())

		headings = soup.findAll('b')

		for h in headings:
			if 'Explanation' in h.next.string:
				explanation = h.parent
				explanation.find('b').extract()

				self.description = explanation.renderContents()
			if 'Credit' in h.next.string:
				credits = ''
				c = h
				while c.nextSibling:
					c = c.nextSibling
					credits = credits + str(c)
				self.credits = credits
		

		if force or not self.image:
			# Get the original image URL
			if soup.img:
				img_url = settings.APOD_URL + "/" + soup.img.parent["href"]

				# Download the image
				f = urllib2.urlopen(img_url)
				self.image.save(os.path.basename(img_url), ContentFile(f.read()))

			self.save()

	@property
	def next(self):
		try:
			return self.get_next_by_publish_date()
		except Item.DoesNotExist:
			return None
	
	@property
	def previous(self):
		try:
			return self.get_previous_by_publish_date()
		except Item.DoesNotExist:
			return None
	
	class Meta:
		ordering = ['-publish_date']