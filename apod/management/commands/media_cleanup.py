import os
from optparse import make_option

from django.core.management.base import BaseCommand
from apod.models import Picture
from django.core.files.storage import default_storage as storage
from django.conf import settings


class Command(BaseCommand):
	help = 'Removes orphaned media files'
	option_list = BaseCommand.option_list + (
		make_option('--info',
			action='store_true',
			default=False,
			help='Display list of orphaned files only (dry run)'),
		)

	def handle(self, *args, **options):
		info = options.get('info')
		count = 0

		for (path, dirs, files) in os.walk(storage.path('pictures')):
			rel_path = os.path.relpath(path, settings.MEDIA_ROOT)
			for f in files:
				f_path = os.path.join(rel_path, f)
				if not Picture.objects.filter(image=f_path).exists():
					if info:
						self.stdout.write("Detected orphaned media file '%s'\n" % f_path)
					else:
						self.stdout.write("Deleting orphaned media file '%s'\n" % f_path)
						storage.delete(f_path)
					count = count + 1

		if info:
			self.stdout.write("Detected %d orphaned media files\n" % count)
		else:
			self.stdout.write("Deleted %d orphaned media files\n" % count)
