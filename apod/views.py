from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import Http404, HttpResponse
from django.conf import settings
from django.views.decorators.http import last_modified

from apod.models import Picture, Tag

import json
import datetime
import calendar
import gviz_api


def server_error(request):
	return render_to_response('500.html', {
		'STATIC_URL': settings.STATIC_URL,
	})


def get_lm(request, year=None, month=None, day=None, tag=None):
	return max(Picture.objects.get_last_modified(year, month, day), settings.LAST_MODIFIED)


@last_modified(get_lm)
def picture(request, year=None, month=None, day=None, tag=None):
	if tag:
		# Part of a tag collection so retrieve the tag
		try:
			tag = Tag.objects.get(slug=tag)
		except Tag.DoesNotExist:
			raise Http404

	if year and month and day:
		try:
			picture = Picture.objects.get_by_date_parts(int(year), int(month), int(day))
		except Picture.DoesNoExist:
			# Invalid date, raise 404
			raise Http404
	else:
		# Home page, so get the latest
		picture = Picture.objects.latest()

	# Add tag to picture for collection context
	if tag:
		picture.current_tag = tag

	response = render(request, 'picture.html', {
		'picture': picture,
		'tag': tag
	})

	# Add last modified header so If-Modified-Since conditional get works
	# response['Last-Modified'] = get_last_modified(picture.updated_date)

	return response


def picture_json(request, picture_id):
	picture = get_object_or_404(Picture, pk=picture_id)

	# Download image from APOD
	picture.get_image()

	data = {
		'url': picture.image.url,
		'width': picture.image.width,
		'height': picture.image.height,
		'title': picture.title
	}

	return HttpResponse(json.dumps(data), mimetype='application/json')


@last_modified(get_lm)
def month(request, year, month):
	year = int(year)
	month = int(month)

	pictures = Picture.objects.filter(publish_date__month=month, publish_date__year=year)

	# Build dict from queryset (to build calendar)
	pics = dict([(p.publish_date.day, p) for p in pictures])
	picture_count = len(pics)

	# If month has no pics, raise 404
	if picture_count == 0:
		raise Http404

	# Build calendar of pics
	cal = calendar.monthcalendar(year, month)
	picture_calendar = [[dict(day=d, picture=pics.get(d, None)) for d in w] for w in cal]

	# Get previous and next months for navigation
	previous_month = datetime.date(year, month, 1) - datetime.timedelta(days=1)
	if not Picture.objects.filter(publish_date__year=previous_month.year, publish_date__month=previous_month.month).exists():
		previous_month = False

	next_month = datetime.date(year, month, 1) + datetime.timedelta(days=32)
	if not Picture.objects.filter(publish_date__year=next_month.year, publish_date__month=next_month.month).exists():
		next_month = False

	# tags = Tag.objects.filter(pictures__publish_date__month=month, pictures__publish_date__year=year).annotate(num_pictures=Count('pictures')).order_by('label')

	view_data = {
		'year': year,
		'month': month,
		'current_month': datetime.date(year, month, 1),
		'previous_month': previous_month,
		'next_month': next_month,
		'picture_count': picture_count,
		'calendar': picture_calendar,
	}

	return render(request, 'month.html', view_data)


@last_modified(get_lm)
def year(request, year):
	year = int(year)

	pictures = Picture.objects.filter(publish_date__year=year).reverse()

	# Build dict indexed by date (to make next step easier)
	pics = dict([(str(p.publish_date), p) for p in pictures])
	picture_count = len(pics)

	# If year has no pics, raise 404
	if picture_count == 0:
		raise Http404

	# Build calendars for the year
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

	# Get previous and next years for navigation
	previous_year = datetime.date(year, 1, 1) - datetime.timedelta(days=1)
	if not Picture.objects.filter(publish_date__year=previous_year.year).exists():
		previous_year = False

	next_year = datetime.date(year, 1, 1) + datetime.timedelta(days=370)
	if not Picture.objects.filter(publish_date__year=next_year.year).exists():
		next_year = False

	view_data = {
		'year': year,
		'picture_count': picture_count,
		'calendars': calendars,
		'previous_year': previous_year,
		'next_year': next_year,
		'year_range': Picture.objects.dates('publish_date', 'year'),
	}

	return render(request, 'year.html', view_data)


def tags(request):
	top_tags = Tag.objects.get_top_tags(30 if request.is_ajax() else 20)

	return render(request, 'tags.html', {
		'tags': top_tags['tags'],
		'min_count': top_tags['min'],
		'max_count': top_tags['max'],
	})


def archive(request, tag, month=None, year=None, page=1):
	page = int(page)

	tag = get_object_or_404(Tag, slug=tag)

	all_pictures = Picture.objects.filter(tags=tag)

	archive_date = None
	archive_type = 'tag'

	# Filter by date if provided
	if year:
		year = int(year)
		archive_date = datetime.date(year, 1, 1)
		archive_type = 'year'

		all_pictures = all_pictures.filter(publish_date__year=year)

		if month:
			month = int(month)
			archive_date = archive_date.replace(month=month)
			archive_type = 'month'
			all_pictures = all_pictures.filter(publish_date__month=month)

	# Setup pagination
	paginator = Paginator(all_pictures, 35)

	# Raise 404 if tag collection is empty
	if paginator.count == 0:
		raise Http404

	try:
		pictures = paginator.page(page)
	except (EmptyPage, InvalidPage):
		pictures = paginator.page(1)

	# Set tag context on all pictures
	for p in pictures.object_list:
		p.current_tag = tag

	return render(request, 'archive.html', {
		'archive_date': archive_date,
		'archive_type': archive_type,
		'page': page,
		'paginator': paginator,
		'tag': tag,
		'pictures': pictures,
	})


def stats(request):
	return render(request, 'stats.html')


def size_over_time(request):
	description = {"date": ("date", "Date"),
					"size": ("number", "Image size")}

	data_table = gviz_api.DataTable(description)
	data_table.LoadData(Picture.objects.get_size_over_time())

	response = data_table.ToJSon(columns_order=("date", "size"))

	return HttpResponse(response, mimetype='application/json')
