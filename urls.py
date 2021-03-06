from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^', include('apod.urls')),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^grappelli/', include('grappelli.urls')),
)

# Serve static and media files in DEBUG mode
# In production, these files will be served by the web server
if settings.DEBUG:
	urlpatterns += staticfiles_urlpatterns()
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	# Dummy 500 for debugging
	urlpatterns += patterns('apod.views', (r'^500/$', 'server_error'))

handler500 = 'apod.views.server_error'
