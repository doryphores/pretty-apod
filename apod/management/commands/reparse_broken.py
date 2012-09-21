from django.core.management.base import NoArgsCommand
from django.db.models import Q
from apod.models import Picture


class Command(NoArgsCommand):
	def handle_noargs(self, **options):
		pictures = Picture.objects.filter(Q(title__icontains='credit:') | Q(title__icontains='copyright:'))
		p_count = pictures.count()

		for p in pictures.all():
			p.load_from_apod()

		self.stdout.write("Fixed %d pictures with 'Credit' in title\n" % p_count)

		pictures = Picture.objects.filter(explanation__startswith=':')
		p_count = pictures.count()

		for p in pictures.all():
			p.load_from_apod()

		self.stdout.write("Fixed %d pictures starting with ':' in explanation\n" % p_count)
