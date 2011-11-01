from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render, redirect

from django.db.models import Count

from apod.models import Photo, Keyword
from apod import apodapi

def list(request, page=1):
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

def image(request, image_id):
	photo = Photo.objects.get(pk=image_id)

	photo.get_image()
	
	return render(request, 'apod/image.html', { 'photo': photo })