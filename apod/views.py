from django.shortcuts import render, redirect
from django.http import HttpResponse

from apod.models import Photo


def refresh(request):
	Photo.objects.import_archive()

	return HttpResponse("All done")

def list(request):
	photos  = Photo.objects.all()[0:50]
	return render(request, 'apod/index.html', { 'photos': photos })

def image(request, image_id):
	photo = Photo.objects.get(pk=image_id)

	photo.load_from_apod()
	
	return render(request, 'apod/image.html', { 'photo': photo })