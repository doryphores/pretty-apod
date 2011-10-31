from django.shortcuts import render, redirect
from django.http import HttpResponse

from apod.models import Photo
from apod import apodapi

def refresh(request):
	try:
		from_date = Photo.objects.latest().publish_date
	except:
		from_date = None
	for apod_details in apodapi.get_archive_list(from_date=from_date):
		photo = Photo(publish_date=apod_details["publish_date"], title=apod_details["title"])
		photo.save()
	
	return redirect('list_view')

def list(request):
	photos  = Photo.objects.filter(publish_date__year=1997, publish_date__month=9)
	return render(request, 'apod/index.html', { 'photos': photos })

def image(request, image_id):
	photo = Photo.objects.get(pk=image_id)

	photo.load_from_apod(False)
	
	return render(request, 'apod/image.html', { 'photo': photo })