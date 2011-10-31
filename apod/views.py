from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render, redirect
from django.http import HttpResponse

from apod.models import Photo
from apod import apodapi

def list(request, page=1):
	all_photos  = Photo.objects.all()

	paginator = Paginator(all_photos, 25)

	try:
		photos = paginator.page(page)
	except (EmptyPage, InvalidPage):
		photos = paginator.page(1)

	return render(request, 'apod/index.html', { 'photos': photos })

def image(request, image_id):
	photo = Photo.objects.get(pk=image_id)

	photo.load_from_apod(True)
	
	return render(request, 'apod/image.html', { 'photo': photo })