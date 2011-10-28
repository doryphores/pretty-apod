from django.db import models
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import urllib2

from BeautifulSoup import BeautifulSoup as BSoup
from HTMLParser import HTMLParser
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

	objects = ItemManager()

	@property
	def apod_id(self):
		return self.publish_date.strftime("%y%m%d")
	
	def __unicode__(self):
		return u'%s' % self.title
	
	class Meta:
		ordering = ['publish_date']


# APOD Parsers

class ArchiveParser(HTMLParser):
	harvest = False
	new_item = False
	open_item = False
	all_done = False

	def handle_starttag(self, tag, attrs):
		# Start harvesting when B tag starts
		if not self.all_done and tag == 'b':
			self.harvest = True
			self.new_item = True
		
		# Start of A tag
		if self.harvest and tag == 'a':
			for name, value in attrs:
				if name == 'href':
					self.item.apod_id = value.strip()
			self.open_item = True
		
		# BR tag announces end of item
		if self.harvest and tag == 'br':
			self.item.save()
			
			self.new_item = True
	
	def handle_data(self, data):
		# We have a new item, use data as the date
		if self.new_item:
			self.item = Item()
			self.item.publish_date = dateparser.parse(data.replace(":", "").strip())
			self.new_item = False
		
		# We are in the A tag so set the item title
		if self.open_item:
			self.item.title = data.strip()
			self.open_item = False

	def handle_endtag(self, tag):
		# Stop harvesting when B tag stops
		if self.harvest and tag == 'b':
			self.harvest = False
			self.all_done = True
