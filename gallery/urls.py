from django.conf.urls import patterns, url
from django.conf.urls.defaults import *
from gallery import views

urlpatterns = patterns('',
	url(r'^$', views.main, name='publicView'),
	#url(r'^{id}/$', views.album, 'name = albumView'),	
	#(r'^$','')
	url(r'^search/$',views.search, name='searchview'),
	url(r'^album/(?P<albumName>[-\w]+)/$',views.album_content),
	url(r'^file/$',views.create_task, name='fileCreate'),
	url(r'^(?P<microscopeName>[-\w]+)/$', views.microscopeListView),
)

#something

