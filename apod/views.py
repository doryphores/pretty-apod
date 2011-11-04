from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404

from django.db.models import Count

from django.http import Http404

from apod.models import Photo, Keyword
from apod import apodapi

import datetime

def image(request, year=None, month=None, day=None):
	if year and month and day:
		try:
			date = datetime.date(int(year), int(month), int(day))
		except ValueError:
			raise Http404
		photo = get_object_or_404(Photo, publish_date=date)
	else:
		photo = Photo.objects.latest()
	
	return render(request, 'apod/image.html', { 'photo': photo })

def archive(request, page=1):
	all_photos  = Photo.objects.all()

	paginator = Paginator(all_photos, 25)

	try:
		photos = paginator.page(page)
	except (EmptyPage, InvalidPage):
		photos = paginator.page(1)

	return render(request, 'apod/index.html', { 'photos': photos })

def tags(request):
	tags = Keyword.objects.annotate(num_photos=Count('photos')).order_by('-num_photos')[:20]

	return render(request, 'apod/tags.html', { 'tags': tags })
