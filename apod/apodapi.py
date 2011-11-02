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

CACHE_FOLDER = 'apod_cache'

def get_archive_list(force=False, from_date=None):
	"""
	Gets a list of APOD items from the APOD archive page
	Only downloads the file if out of date

	Returns a list of dicts with publish_date and title keys
	"""
	archive_file = '%s/archive.html' % CACHE_FOLDER
	
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

def get_apod_details(apod_date, force=False):
	"""
	Gets details of an individual APOD for the given date

	Returns a dict with the following keys:
		title			the APOD title
		explanation		the APOD explanation in HTML
		credits			the APOD credits in HTML
		image_url		the URL of the original APOD image
	"""
	apod_url = get_apod_url(apod_date)
	cache_file = os.path.join(CACHE_FOLDER, os.path.basename(apod_url))

	if force and storage.exists(cache_file):
		storage.delete(cache_file)
	
	# Download archive HTML if needed
	if not storage.exists(cache_file):
		f = urllib2.urlopen(apod_url)
		html = f.read()
		
		# Write it to disk
		storage.save(cache_file, ContentFile(html))
	
	# Read HTML
	with storage.open(cache_file) as f:
		html = f.read()
	
	html = html.strip()

	old_keywords = None

	# Handle weird keywords comment
	if '<!- ' in html:
		# Extract the keywords
		pat = re.compile('<!- KEYWORDS: (.+?)>', re.I)
		keyword_search = re.search(pat, html)
		if keyword_search:
			old_keywords = keyword_search.group(1)

		# Remove the 'tag' because it breaks parsing
		html = re.sub(pat, '', html)

	# Parse it with Beautiful Soup
	soup = BSoup(html)

	details = {
		'title': '',
		'explanation': '',
		'credits': '',
		'image_url': '',
		'keywords': [],
	}

	# Parse keywords
	if old_keywords:
		details['keywords'] = filter(len, old_keywords.split(','))
	else:
		meta_keywords = soup.find('meta', attrs={'name':'keywords'})
		if meta_keywords:
			details['keywords'] = filter(len, meta_keywords['content'].split(','))
	
	# Get info from HTML if we can read B tags at all
	# If we can't, the page is too screwed even for Beautiful Soup
	if soup.find('b'):
		details['title'] = re.sub('<.*?>', '', soup.find('b').renderContents()).strip()
		details['explanation'] = get_section(soup, 'explanation')
		details['credits'] = get_section(soup, 'credit')

	# Get the original hi-res image URL
	if soup.img and soup.img.parent.name == 'a':
		href = soup.img.parent['href'].strip()
		# Make sure URL is to a valid image type
		if href and href.split('/')[-1].split('.')[-1].lower() in ['jpg', 'jpeg', 'gif', 'png']:
			details['image_url'] = settings.APOD_URL + "/" + href
	
	# @TODO: look for videos or other media

	return details

def get_section(soup, heading):
	b_tags = soup.findAll('b')

	for b in b_tags:
		if heading in b.renderContents().lower():
			container = []
			n = b.nextSibling
			while n:
				if isinstance(n, Tag):
					# Stop when we hit a paragraph tag
					if n.name == 'p':
						break
				container.append(unicode(n))
				n = n.nextSibling
			return ''.join(container).strip()
	
	return ''