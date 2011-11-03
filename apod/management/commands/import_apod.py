from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apod.models import Photo
from apod import apodapi


class Command(BaseCommand):
	args = '[year] [month]'
	help = 'Imports APOD data'

	def handle(self, *args, **options):
		# Add missing APODs
		try:
			from_date = Photo.objects.latest().publish_date
		except Photo.DoesNotExist:
			from_date = None
		
		for apod_details in apodapi.get_archive_list(from_date=from_date):
			photo = Photo(publish_date=apod_details["publish_date"], title=apod_details["title"])
			photo.save()
		
		self.stdout.write('Archive imported successfully\n')

		if len(args) == 1:
			photos_to_load = Photo.objects.filter(publish_date__year=int(args[0]))
		elif len(args) == 2:
			photos_to_load = Photo.objects.filter(publish_date__year=int(args[0]), publish_date__month=int(args[1]))
		else:
			photos_to_load = Photo.objects.filter(loaded=False)
			
		#transaction.commit_unless_managed()
		#transaction.enter_transaction_management()
		#transaction.managed(True)

		self.stdout.write('%s photos to load\n' % photos_to_load.count())

		success_count = 0
		error_count = 0

		for photo in photos_to_load:
			try:
				photo.load_from_apod()
				success_count = success_count + 1
				self.stdout.write('%s imported\n' % photo.publish_date)
			except:
				raise
				error_count = error_count + 1
		
		#transaction.commit()
		#transaction.leave_transaction_management()

		self.stdout.write('Successfully imported %d (%d failures)\n' % (success_count, error_count))