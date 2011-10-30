from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^api/', include('apod.urls')),
	
	url(r'^admin/', include(admin.site.urls)),
)
