from django.core.management.base import BaseCommand
from apod.models import Picture


class Command(BaseCommand):
	help = 'Downloads a random missing image'

	def handle(self, *args, **options):
		try:
			picture = Picture.objects.filter(image='', media_type='IM').order_by('?')[0:1].get()
		except Picture.DoesNotExist:
			self.stdout.write('No images to download\n')
			return

		if picture:
			self.stdout.write('Downloading %s...\n' % picture)

			picture.get_image()

			self.stdout.write('Successfully downloaded image\n')
