import os
import imghdr
from optparse import make_option

from django.core.management.base import NoArgsCommand
from django.core.files.storage import default_storage as storage
from django.conf import settings

from apod.models import Picture
from apod.utils.minimal_exif_writer import MinimalExifWriter


class Command(NoArgsCommand):
	help = 'Removes orphaned media files'
	option_list = NoArgsCommand.option_list + (
		make_option('--info',
			action='store_true',
			default=False,
			help='Display list of orphaned files only (dry run)'),
		make_option('--strip',
			action='store_true',
			default=False,
			help='Strip all EXIF data from pictures'),
		)

	def handle_noargs(self, **options):
		info = options.get('info')
		strip = options.get('strip')
		del_count = 0
		strip_count = 0

		for (path, dirs, files) in os.walk(storage.path('pictures')):
			rel_path = os.path.relpath(path, settings.MEDIA_ROOT)
			for f in files:
				f_path = os.path.join(rel_path, f)
				extension = f.split('.')[-1].lower()
				format = imghdr.what(os.path.join(path, f))

				if not format:
					self.stdout.write("Unknown format: %s\n" % f_path)

				if not Picture.objects.filter(image=f_path).exists():
					if info:
						self.stdout.write("Detected orphaned media file '%s'\n" % f_path)
					else:
						self.stdout.write("Deleting orphaned media file '%s'\n" % f_path)
						storage.delete(f_path)
					del_count = del_count + 1
				else:
					# Detect PNG images saved as JPG
					if format == 'png' and extension == 'jpg':
						p = Picture.objects.get(image=f_path)
						self.stdout.write("Renaming %s image\n" % p)
						p.image.save(f.replace('.jpg', '.png'), p.image)
					elif strip and extension in ['jpg', 'jpeg']:
						try:
							# Process EXIF data (strip all except copyright if present)
							exif_writer = MinimalExifWriter(storage.path(f_path))
							exif_writer.removeExif()
							exif_writer.process()
							strip_count = strip_count + 1
						except Exception as e:
							self.stdout.write("Unable to strip EXIF data from '%s': %s\n" % (f_path, str(e)))

		if info:
			self.stdout.write("Detected %d orphaned media files\n" % del_count)
		else:
			self.stdout.write("Deleted %d orphaned media files\n" % del_count)

		if strip:
			self.stdout.write("Stripped EXIF data from %d pictures\n" % strip_count)
