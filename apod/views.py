from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count

from django.http import Http404, HttpResponse

from apod.models import Picture, Keyword
from apod import apodapi

import json
import datetime

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

	return render(request, 'apod/index.html', { 'pictures': pictures })


def tags(request):
	tags = Keyword.objects.annotate(num_pictures=Count('pictures')).order_by('-num_pictures')[:20]

	return render(request, 'apod/tags.html', { 'tags': tags })
