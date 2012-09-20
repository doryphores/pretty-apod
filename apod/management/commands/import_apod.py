from django.core.management.base import BaseCommand, CommandError

from apod.models import Picture
from apod import apodapi


class Command(BaseCommand):
	args = '[year] [month]'
	help = 'Imports APOD data'

	def handle(self, *args, **options):
		# Add missing APODs

		existing_apods = Picture.objects.values_list('publish_date', flat=True)

		counter = 0

		for apod_details in apodapi.get_archive_list():
			if apod_details["publish_date"] not in existing_apods:
				picture = Picture(publish_date=apod_details["publish_date"], title=apod_details["title"])
				picture.save()
				counter = counter + 1

		if counter:
			self.stdout.write('Archive imported successfully (%d APODs added)\n' % counter)

		if len(args) == 1:
			pictures_to_load = Picture.objects.filter(publish_date__year=int(args[0]))
		elif len(args) == 2:
			pictures_to_load = Picture.objects.filter(publish_date__year=int(args[0]), publish_date__month=int(args[1]))
		else:
			pictures_to_load = Picture.objects.all()

		pictures_to_load = pictures_to_load.filter(loaded=False)

		self.stdout.write('%s pictures to load\n' % pictures_to_load.count())

		if pictures_to_load:
			success_count = 0
			error_count = 0

			for picture in pictures_to_load:
				try:
					picture.load_from_apod()
					success_count = success_count + 1
					self.stdout.write('%s imported\n' % picture.publish_date)
				except:
					raise
					error_count = error_count + 1

			self.stdout.write('Successfully imported %d (%d failures)\n' % (success_count, error_count))
