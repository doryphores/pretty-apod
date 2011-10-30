from django.contrib import admin
from apod.models import Photo
from sorl.thumbnail.admin import AdminImageMixin

class PhotoAdmin(AdminImageMixin, admin.ModelAdmin):
	pass

admin.site.register(Photo, PhotoAdmin)