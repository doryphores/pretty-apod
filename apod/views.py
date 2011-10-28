from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings

from apod.models import Item


def refresh(request):
	Item.objects.import_archive()

	return HttpResponse("All done")

def list(request):
	items  = Item.objects.all()
	return render(request, 'apod/index.html', { 'items': items })