from django.conf.urls import patterns, include, url
from django.conf.urls import *
from django.conf.urls import *
from ncemhub.views import microscopes, users, dates
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
admin.autodiscover()



urlpatterns = patterns('',
	url(r'^$','ncemhub.views.home', name = 'home'),
	url(r'^users/$', 'ncemhub.views.users', name = 'users'),
	url(r'^users/(?P<user_id>\+d)$', 'ncemhub.views.microscopes', name = 'microscopes'),
	url(r'^users/(?P<user_id>\+d)/(?P<microscope_id>\+d)$', 'ncemhub.views.dates', name = 'dates'),
	url(r'^user/', include('user_authentication.urls')),
	url(r'^data/manager/',include('data_manager.urls')),
	# Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^gallery/',include('gallery.urls')),
	
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
