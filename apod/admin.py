from django.contrib import admin
from apod.models import Photo, Keyword
from sorl.thumbnail.admin import AdminImageMixin

class PhotoAdmin(AdminImageMixin, admin.ModelAdmin):
	list_display = ['publish_date', 'title']
	date_hierarchy = 'publish_date'
	list_filter = ['publish_date', 'loaded']

	actions = ['reload_from_apod']

	def reload_from_apod(self, request, queryset):
		rows_updated = queryset.count()
		for photo in queryset.all():
			photo.load_from_apod(True)
		if rows_updated == 1:
			message = '1 photo was'
		else:
			message = '%s photos were' % rows_updated
		self.message_user(request, '%s successfully reloaded from APOD' % message)
	reload_from_apod.short_description = 'Reload selected photos from APOD'

admin.site.register(Photo, PhotoAdmin)

class KeywordAdmin(admin.ModelAdmin):
	search_fields = ['label']

admin.site.register(Keyword, KeywordAdmin)