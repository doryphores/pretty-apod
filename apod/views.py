from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count

from django.http import Http404, HttpResponse

from apod.models import Picture, Keyword
from apod import apodapi

import json
import datetime
import calendar

def image(request, year=None, month=None, day=None):
	if year and month and day:
		try:
			date = datetime.date(int(year), int(month), int(day))
		except ValueError:
			raise Http404
		picture = get_object_or_404(Picture, publish_date=date)
	else:
		# Home page, so get the latest
		picture = Picture.objects.latest()
	
	return render(request, 'apod/image.html', { 'picture': picture })


def image_only(request, picture_id):
	picture = get_object_or_404(Picture, pk=picture_id)

	picture.get_image()

	data = {
		'url': picture.image.url,
		'width': picture.image.width,
		'height': picture.image.height,
		'title': picture.title
	}

	return HttpResponse(json.dumps(data), mimetype='application/json')


def archive(request, page=1):
	all_pictures  = Picture.objects.all()

	paginator = Paginator(all_pictures, 25)

	try:
		pictures = paginator.page(page)
	except (EmptyPage, InvalidPage):
		pictures = paginator.page(1)

	return render(request, 'apod/archive.html', { 'pictures': pictures })

def month(request, year, month):
	year = int(year)
	month = int(month)

	pictures = Picture.objects.filter(publish_date__month=month, publish_date__year=year)

	# If month has no pics, raise 404
	if pictures.count() == 0:
		raise Http404

	pics = dict([(p.publish_date.day, p) for p in pictures])

	cal = calendar.monthcalendar(year, month)

	picture_calendar = [[dict(day=d, picture=pics.get(d, None)) for d in w] for w in cal]

	tags = Keyword.objects.filter(pictures__publish_date__month=month, pictures__publish_date__year=year).annotate(num_pictures=Count('pictures')).order_by('label')

	view_data = {
		'month': datetime.date(year, month, 1),
		'calendar': picture_calendar,
		'tags':tags,
	}

	return render(request, 'apod/month.html', view_data)

def year(request, year):
	year = int(year)

	pictures = Picture.objects.filter(publish_date__year=year).reverse()

	# If year has no pics, raise 404
	if pictures.count() == 0:
		raise Http404

	# Build dict indexed by date
	pics = dict([(str(p.publish_date), p) for p in pictures])

	today = datetime.date.today()
	last_month = 12

	# Set last month to current month if looking at current year
	if today.year == year:
		last_month = today.month

	first_month = pictures[0].publish_date.month

	calendars = [
		{
			'label': calendar.month_name[month],
			'calendar': [
				[
					dict(day=d, picture=pics.get('%d-%#02d-%#02d' % (year, month, d), None))
					for d in w
				]
				for w in calendar.monthcalendar(year, month)
			]
		}
		for month in range(first_month, last_month+1)
	]

	view_data = {
		'year': year,
		'calendars': calendars,
		'tags':tags,
	}

	return render(request, 'apod/year.html', view_data)

def tags(request):
	tags = Keyword.objects.annotate(num_pictures=Count('pictures')).order_by('label')[:20]

	return render(request, 'apod/tags.html', { 'tags': tags })
