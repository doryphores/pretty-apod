from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apod.models import Picture
from apod import apodapi


class Command(BaseCommand):
	args = '[year] [month]'
	help = 'Imports APOD data'

	def handle(self, *args, **options):
		# Add missing APODs
		try:
			from_date = Picture.objects.latest().publish_date
		except Picture.DoesNotExist:
			from_date = None
		
		for apod_details in apodapi.get_archive_list(from_date=from_date):
			picture = Picture(publish_date=apod_details["publish_date"], title=apod_details["title"])
			picture.save()
		
		self.stdout.write('Archive imported successfully\n')

		if len(args) == 1:
			pictures_to_load = Picture.objects.filter(publish_date__year=int(args[0]))
		elif len(args) == 2:
			pictures_to_load = Picture.objects.filter(publish_date__year=int(args[0]), publish_date__month=int(args[1]))
		else:
			pictures_to_load = Picture.objects.filter(original_image_url='')
			
		#transaction.commit_unless_managed()
		#transaction.enter_transaction_management()
		#transaction.managed(True)

		self.stdout.write('%s pictures to load\n' % pictures_to_load.count())

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
		
		#transaction.commit()
		#transaction.leave_transaction_management()

		self.stdout.write('Successfully imported %d (%d failures)\n' % (success_count, error_count))