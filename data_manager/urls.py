from django.conf.urls import patterns, url
#from django.conf.urls.defaults import *
from data_manager import views

urlpatterns = patterns('',
	url(r'^$', views.main, name='data_home'),
	url(r'^detail/$', views.data_set_detail, name='data_detail'),
	url(r'^initiate/$', views.initiate_database, name='initiateTest'),
	url(r'^edit/$', views.edit, name='edit_content'),
	url(r'^content/admin/$',views.admin,name='admin_content'),
	#url(r'^{id}/$', views.album, 'name = albumView'),	
	#(r'^$','')
	#url(r'^search/$',views.search, name='searchview'),
	#url(r'^collection/(?P<collection>[-\w]+)/$',views.album_content),
	#url(r'^data_set/$',views.create_task, name='fileCreate'),
	#url(r'^(?P<microscopeName>[-\w]+)/$', views.microscopeListView),
)

"""
URL's:
This respository is meant to act like a file system that is interactive.  

**********************************************************************************************
Home--Quick access to all data

Data_set--The file system path for each data set

Search--A simple ability to search all meta data relative to your work and shared work 
			(this will take awhile I feel like)

Instrument--Each instrument has its own set of details and description: all data recorded by the 
			instrument will reside within the folder of the instrument

______________________________________________________________________________________________
Collection--A collection of different data_sets that may have something to do with one another.

Repository--A collection of collections (in case separate collections deal with one experiment 
			and other collections deal with another experiment)
			**Repositories and Collections will be made as something easily skipped if not interested in use**



"""
