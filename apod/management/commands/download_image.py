from django.core.management.base import BaseCommand, CommandError

from apod.models import Picture
from apod import apodapi


class Command(BaseCommand):
	help = 'Downloads a random missing image'

	def handle(self, *args, **options):
		picture = Picture.objects.filter(image='', loaded=True, media_type='IM').order_by('?')[0]

		if picture:
			self.stdout.write('Downloading %s...\n' % picture)

			picture.get_image()

			self.stdout.write('Successfully downloaded image\n')