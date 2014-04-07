from django.conf.urls import patterns, url
#from django.conf.urls.defaults import *
from data_manager import views

urlpatterns = patterns('',
	url(r'^$', views.main, name='data_home'),
	#url(r'^detail/$', views.data_set_detail, name='data_detail'),
	url(r'^download/(?P<data_set_id>[-\w]+)$',views.download,name='file_download'),
	url(r'^gallery$',views.gallery,name='gallery_public'),

	url(r'^data$',views.user_data,name='summary_recent_data'),
	url(r'^data/(?P<data_set_id>[-\w]+)$',views.data_detail,name='detail_of_data'),
	url(r'^data/(?P<data_set_id>[-\w]+)/more$',views.data_detail_more,name='all_info_data'),
	url(r'^data/(?P<data_set_id>[-\w]+)/more/(?P<detail_id>[-\w]+)$',views.data_detail_characteristic,name='detail_characteristic'),
	url(r'^data/(?P<data_set_id>[-\w]+)/edit$',views.data_edit,name='edit_single_dataset'),
	url(r'^data/(?P<data_set_id>[-\w]+)/edit/(?P<detail_id>[-\w]+)$',views.data_detail_edit,name='edit_detail_of_dataset'),

	url(r'^collection$',views.collections,name='view_all_collections'),
	url(r'^collection/(?P<collection_id>[-\w]+)$',views.collection_detail,name='view_collection'),
	url(r'^collection/(?P<collection_id>[-\w]+)/edit$',views.collection_detail_edit,name='edit_collection'),

	url(r'^profile/(?P<user_id>[-\w]+)$',views.user_profile,name='view_profile'),
	url(r'^profile/(?P<user_id>[-\w]+)/edit$',views.user_profile_edit,name='edit_profile'),

	url(r'^directories$',views.directories, name='directories'),
	url(r'^directories/(?P<instrument_slug>[-\w]+)$',views.directories_instrument, name='instrument_directory'),
	#url(r'^{id}/$', views.album, 'name = albumView'),	
	#(r'^$','')
	#url(r'^search/$',views.search, name='searchview'),
	#url(r'^collection/(?P<collection>[-\w]+)/$',views.album_content),
	#url(r'^data_set/$',views.create_task, name='fileCreate'),
	#url(r'^(?P<microscopeName>[-\w]+)/$', views.microscopeListView),
)
"""
https://www.ncemhub.gov/											#home
https://www.ncemhub.gov/gallery										#public data sets
https://www.ncemhub.gov/data										#recent data view (edited/viewed)
https://www.ncemhub.gov/data/<data_set_id>							#detail image view
https://www.ncemhub.gov/data/<data_set_id>/more						#shows all characteristics
https://www.ncemhub.gov/data/<data_set_id>/edit 				 	#edit specific image 
https://www.ncemhub.gov/data/<data_set_id>/edit/<data_set_detail> 	#edit specific image detail
https://www.ncemhub.gov/collection/<collection_id>					#
https://www.ncemhub.gov/collection/<collection_id>/edit 			#
https://www.ncemhub.gov/profile/<user_id>							#view the profile of a user
https://www.ncemhub.gov/directories 								#Shows available instrument directories and recently added
https://www.ncemhub.gov/directories/<instrument_name> 				#Shows files in instrument
"""

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
