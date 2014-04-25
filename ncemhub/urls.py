from django.conf.urls import patterns, include, url
from django.conf.urls import *
from django.conf.urls import *
from ncemhub import views
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
admin.autodiscover()



urlpatterns = patterns('',
	url(r'^user/', include('user_authentication.urls')),
	url(r'^',include('data_manager.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^about/', views.about),
    url(r'^contact/', views.contact),
    url(r'^home_redirect',views.home),
	# Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
