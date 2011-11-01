from django.contrib import admin
from apod.models import Photo, Keyword
from sorl.thumbnail.admin import AdminImageMixin

class PhotoAdmin(AdminImageMixin, admin.ModelAdmin):
	list_display = ['publish_date', 'title']
	date_hierarchy = 'publish_date'
	list_filter = ['publish_date', 'loaded']

admin.site.register(Photo, PhotoAdmin)

class KeywordAdmin(admin.ModelAdmin):
	search_fields = ['label']

admin.site.register(Keyword, KeywordAdmin)