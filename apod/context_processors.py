from django.conf import settings


def timestamp(request):
	return {'TIMESTAMP': settings.TIMESTAMP}
