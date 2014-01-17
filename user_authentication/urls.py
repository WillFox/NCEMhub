from django.conf.urls import patterns, url
#from django.conf.urls.defaults import *
from user_authentication import views
from django.contrib import admin
from django.contrib.auth.views import password_reset_done, password_reset, password_reset_confirm,password_reset_complete
urlpatterns = patterns('',
	url(r'^register/$',views.PatronRegistration, name='PatronRegistration'),
	url(r'^login/$', views.LoginRequest, name='PatronLogin'),
	url(r'^profile/$', views.Profile, name='PatronProfile'),
	url(r'^logout/$', views.LogoutRequest, name='PatronLogout'),
	url(r'^resetpassword/passwordsent/$',password_reset_done,name='passResetDone'),
	url(r'^resetpassword/$',password_reset,name='passReset'),
	url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',password_reset_confirm,name='resetConfirm'),
	url(r'^reset/done/$',password_reset_complete,name='passResetComplete'),
	#url(r'^profile$', views.PatronProfile, name='PatronProfile'),

)
