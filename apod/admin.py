from django.conf.urls.defaults import patterns
from django.http import HttpResponseRedirect
from django.db import models
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin.widgets import FilteredSelectMultiple

from apod.models import Picture, Tag, TagFormatter


class PictureAdmin(admin.ModelAdmin):
	def _get_thumb(obj):
		thumb = obj.thumb
		if thumb:
			return u'<img src="%s" width="120" height="90" />' % thumb
		else:
			return u'(No picture)'
	_get_thumb.short_description = u'thumbnail'
	_get_thumb.allow_tags = True

	list_display = [_get_thumb, 'publish_date', 'title', 'media_type']
	list_display_links = [_get_thumb, 'publish_date']
	list_per_page = 30
	date_hierarchy = 'publish_date'
	list_filter = ['publish_date', 'loaded', 'media_type']
	search_fields = ['title', 'credits', 'explanation']

	formfield_overrides = {
		models.ManyToManyField: {'widget': FilteredSelectMultiple("tags", is_stacked=False)}
	}

	actions = ['reload_from_apod', 'download_image']

	def reload_from_apod(self, request, queryset):
		rows_updated = queryset.count()
		for picture in queryset.all():
			picture.load_from_apod(True)
		if rows_updated == 1:
			message = u'1 picture was'
		else:
			message = u'%s pictures were' % rows_updated
		self.message_user(request, u'%s successfully reloaded from APOD' % message)
	reload_from_apod.short_description = u'Reload selected pictures from APOD'

	def download_image(self, request, queryset):
		rows_updated = queryset.count()
		for picture in queryset.all():
			picture.get_image(True)
		if rows_updated == 1:
			message = u'1 picture was'
		else:
			message = u'%s pictures were' % rows_updated
		self.message_user(request, u'%s successfully downloaded from APOD' % message)
	download_image.short_description = u'Download selected pictures from APOD'

admin.site.register(Picture, PictureAdmin)


@staff_member_required
def format_label_view(request, model_admin):
	result = Tag.objects.format_labels()

	model_admin.message_user(request, u'Successfully formatted keyword labels (%d obsolete keywords removed, %d keywords reformatted)' % result)

	return HttpResponseRedirect('../')


class TagAdmin(admin.ModelAdmin):
	search_fields = ['label']

	def format_labels(self, request):
		return format_label_view(request, self)

	def get_urls(self):
		urls = super(TagAdmin, self).get_urls()
		my_urls = patterns('', (r'^format/$', self.format_labels))
		return my_urls + urls

admin.site.register(Tag, TagAdmin)

admin.site.register(TagFormatter)
