from django.core.management.base import NoArgsCommand
from PIL import ImageFile as PILImageFile
from PIL import Image
import exiftool


class Command(NoArgsCommand):
	help = 'Sandbox for testing'

	def handle_noargs(self, **options):
		# with exiftool.ExifTool() as et:
		# 	print et.get_tag('copyright', '/Users/martinlaine/django/pretty-apod/public/media/pictures/2011/4/RhoOph_wise.jpg')
		# i = Image.open('/Users/martinlaine/django/pretty-apod/public/media/pictures/2011/4/RhoOph_wise.jpg')
		# print i.size
		with open('/Users/martinlaine/django/pretty-apod/public/media/pictures/2011/4/NGC2438_IAC80_DLopez.jpg', 'rb') as f:
			data = f.read()
			p = PILImageFile.Parser()
			p.feed(data)

			print p.image.size

		# self.stdout.write("Stripped EXIF data from %d pictures\n" % strip_count)
