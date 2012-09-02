from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Min, Max

from django.views.generic import ListView

from django.http import Http404, HttpResponse

from apod.models import Picture, Tag
from apod import apodapi

import json
import datetime
import calendar

def picture(request, year=None, month=None, day=None, tag=None):
	if tag:
		try:
			tag = Tag.objects.get_by_slug(tag)
		except Tag.DoesNotExist:
			raise Http404

	if year and month and day:
		try:
			date = datetime.date(int(year), int(month), int(day))
		except ValueError:
			raise Http404
		picture = get_object_or_404(Picture, publish_date=date)
	else:
		# Home page, so get the latest
		picture = Picture.objects.latest()

	if tag:
		picture.current_tag = tag

	return render(request, 'apod/picture.html', {
		'picture': picture,
		'tag': tag
	})


def picture_json(request, picture_id):
	picture = get_object_or_404(Picture, pk=picture_id)

	picture.get_image()

	data = {
		'url': picture.image.url,
		'width': picture.image.width,
		'height': picture.image.height,
		'title': picture.title
	}

	return HttpResponse(json.dumps(data), mimetype='application/json')

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

	next_month = datetime.date(year, month, 1) + datetime.timedelta(days=32)

	if not Picture.objects.filter(publish_date__year=next_month.year, publish_date__month=next_month.month).exists():
		next_month = False

	previous_month = datetime.date(year, month, 1) - datetime.timedelta(days=1)

	if not Picture.objects.filter(publish_date__year=previous_month.year, publish_date__month=previous_month.month).exists():
		previous_month = False

	# tags = Tag.objects.filter(pictures__publish_date__month=month, pictures__publish_date__year=year).annotate(num_pictures=Count('pictures')).order_by('label')

	view_data = {
		'year': year,
		'month': month,
		'current_month': datetime.date(year, month, 1),
		'previous_month': previous_month,
		'next_month': next_month,
		'archive_label': '%s %s Archive' % (calendar.month_name[month], year),
		'calendar': picture_calendar,
		# 'month_range': Picture.objects.filter(publish_date__year=year).dates('publish_date', 'month'),
		# 'tags': tags,
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

	calendars = [
		{
			'label': calendar.month_name[m.month],
			'calendar': [
				[
					dict(day=d, picture=pics.get('%d-%#02d-%#02d' % (year, m.month, d), None))
					for d in w
				]
				for w in calendar.monthcalendar(year, m.month)
			]
		}
		for m in pictures.reverse().dates('publish_date', 'month')
	]

	next_year = datetime.date(year, 1, 1) + datetime.timedelta(days=370)

	if not Picture.objects.filter(publish_date__year=next_year.year).exists():
		next_year = False

	previous_year = datetime.date(year, 1, 1) - datetime.timedelta(days=1)

	if not Picture.objects.filter(publish_date__year=previous_year.year).exists():
		previous_year = False

	view_data = {
		'year': year,
		'archive_label': '%s Archive' % year,
		'calendars': calendars,
		'previous_year': previous_year,
		'next_year': next_year,
		'year_range': Picture.objects.dates('publish_date', 'year'),
	}

	return render(request, 'apod/year.html', view_data)

def tags(request):
	top_tags = Tag.objects.get_top_tags(30 if request.is_ajax() else 20)

	return render(request, 'apod/tags.html', {
		'tags': top_tags['tags'],
		'min_count': top_tags['min'],
		'max_count': top_tags['max'],
	})

def tag(request, tag, month=None, year=None, page=1):
	page = int(page)

	try:
		tag = Tag.objects.get_by_slug(tag)
	except Tag.DoesNotExist:
		raise Http404

	all_pictures = Picture.objects.filter(tags=tag)

	archive_date = None

	if year:
		archive_date = year
		year = int(year)

		all_pictures = all_pictures.filter(publish_date__year=year)

		if month:
			month = int(month)
			archive_date = datetime.date(year, month, 1).strftime('%B %Y')
			all_pictures = all_pictures.filter(publish_date__month=month)

	if all_pictures.count() == 0:
		raise Http404

	paginator = Paginator(all_pictures, 35)

	try:
		pictures = paginator.page(page)
	except (EmptyPage, InvalidPage):
		pictures = paginator.page(1)

	for p in pictures.object_list:
		p.current_tag = tag

	return render(request, 'apod/tag.html', {
		'archive_date': archive_date,
		'page': page,
		'paginator': paginator,
		'tag': tag,
		'pictures': pictures,
	})