from django.contrib import admin
from apod.models import Picture, Keyword
from sorl.thumbnail.admin import AdminImageMixin

class PictureAdmin(AdminImageMixin, admin.ModelAdmin):
	list_display = ['publish_date', 'title']
	date_hierarchy = 'publish_date'
	list_filter = ['publish_date', 'loaded']
	search_fields = ['title']

	actions = ['reload_from_apod']

	def reload_from_apod(self, request, queryset):
		rows_updated = queryset.count()
		for picture in queryset.all():
			picture.load_from_apod(True)
		if rows_updated == 1:
			message = '1 picture was'
		else:
			message = '%s pictures were' % rows_updated
		self.message_user(request, '%s successfully reloaded from APOD' % message)
	reload_from_apod.short_description = 'Reload selected pictures from APOD'

admin.site.register(Picture, PictureAdmin)

class KeywordAdmin(admin.ModelAdmin):
	search_fields = ['label']

admin.site.register(Keyword, KeywordAdmin)