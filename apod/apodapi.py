import os
import urllib2
import re
from BeautifulSoup import Tag, BeautifulSoup as BSoup
from dateutil import parser as dateparser
import datetime

from django.core.files.storage import default_storage as storage
from django.core.files.base import ContentFile
from django.core.files import File
from django.conf import settings

def get_archive_list(force=False, from_date=None):
	"""
	Gets a list of APOD items from the APOD archive page
	Only downloads the file if out of date

	Returns a list of dicts with publish_date and title keys
	"""
	archive_file = 'apodcache/archive.html'
	
	# Download archive HTML if needed
	if force or not storage.exists(archive_file) or storage.modified_time(archive_file).date() < datetime.date.today():
		f = urllib2.urlopen(settings.APOD_ARCHIVE_URL)
		html = f.read()
		
		# Write it to disk
		storage.save(archive_file, ContentFile(html))
	
	# Read HTML
	with storage.open(archive_file) as f:
		html = f.read()
	
	# Parse HTML
	html_soup = BSoup(html)
	archive_links = html_soup.b.findAll("a")

	for link in archive_links:
		publish_date = dateparser.parse(link.previous.strip().strip(':')).date()
		if from_date and publish_date <= from_date:
			return
		
		yield {
			'publish_date': publish_date,
			'title': unicode(link.next),
		}

def get_apod_url(apod_date):
	"""
	Returns the URL to an individual APOD for the given date
	"""
	return u'%s/ap%s.html' % (settings.APOD_URL, apod_date.strftime('%y%m%d'))

def get_apod_details(apod_date):
	"""
	Gets details of an individual APOD for the given date

	Returns a dict with the following keys:
		title			the APOD title
		explanation		the APOD explanation in HTML
		credits			the APOD credits in HTML
		image_url		the URL of the original APOD image
	"""
	# Get APOD HTML page
	f = urllib2.urlopen(get_apod_url(apod_date))

	# Parse it with Beautiful Soup
	soup = BSoup(f.read())

	apod = {
		'title': soup.find('b').string,
		'explanation': '',
		'credits': '',
		'image_url': ''
	}

	# Get bold headings
	headings = soup.findAll('b')

	for h in headings:
		if 'Explanation' in h.next.string:
			apod['explanation'] = get_nextsiblings_content(h)
		if 'Credit' in h.next.string:
			apod['credits'] = get_nextsiblings_content(h)
	
	# Get the original image URL
	if soup.img and soup.img.parent.name == 'a':
		apod['image_url'] = settings.APOD_URL + "/" + soup.img.parent['href']
	

	# @TODO: look for videos or other media

	return apod

def get_nextsiblings_content(node):
	"""
	Gets the rendered HTML of the next siblings of a BeautifulSoup node
	"""
	container = []
	n = node
	while n.nextSibling:
		n = n.nextSibling
		container.append(unicode(n))
	return ''.join(container).strip()