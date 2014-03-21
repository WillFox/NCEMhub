from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.forms import ModelForm
from ncemhub.settings import MEDIA_URL, DATA_ROOT, MEDIA_ROOT
from data_manager.models import DataCharacteristic, Tag, DataRecorder, Repository, Collection, DataSet, Value
from django.template import RequestContext
from user_authentication.models import Patron
from django.contrib.auth.models import User
import os
from django.db.models import Q
from django.core.files import File
from django.views.static import serve
#FileDelimeter is the object used to show a new directory depth in the url.
FileDelimeter= '---'

"""
FUNCTION SUMMARY: 
This is the first place seen once an individual logs in.  
Allows quick access to all data (no fluff [jiggly puff] please)

Required:
-Recently added/utilized section 
-Display possible instruments
-Display possible collections
-Display possible Repositories
-NavigationPanel dependent on current contents (directories)
-Contents section
"""
"""
https://www.ncemhub.gov/                                            #home
https://www.ncemhub.gov/gallery                                     #public data sets
https://www.ncemhub.gov/data                                        #recent data view (edited/viewed)
https://www.ncemhub.gov/data/<data_set_id>                          #detail image view
https://www.ncemhub.gov/data/<data_set_id>/edit                     #edit specific image 
https://www.ncemhub.gov/data/<data_set_id>/edit/<data_set_detail>   #edit specific image detail
https://www.ncemhub.gov/collection/<collection_id>                  #
https://www.ncemhub.gov/collection/<collection_id>/edit             #
https://www.ncemhub.gov/profile/<user_id>                           #view the profile of a user
https://www.ncemhub.gov/
"""
"""
Displays:
#Recently added folder
#Recently altered data
#Recently Viewed data
"""
def main(request):
    data_chosen  = DataSet.objects.filter(public=True).distinct()
    collection_chosen = Collection.objects.filter(public=True).distinct()
    return render_to_response("data_manager/main.html", dict(user=request.user,
        media_url=MEDIA_URL,media_root=MEDIA_ROOT, data_sets=data_chosen,collections=collection_chosen, home=" class=active"))


"""
Displays:
#displays a public listing of data and info
"""
def gallery(request):
    return HttpResponseRedirect('/')     
"""
Displays:
#a list of all data taken by user
"""
def user_data(request):    
    user=request.user
    data_chosen=DataSet.objects.filter(owners=user).distinct()
    return render_to_response("data_manager/user_data.html", dict(user=request.user,
        data_chosen=data_chosen,media_url=MEDIA_URL,media_root=MEDIA_ROOT, data_page=" class=active"))  
"""
Displays:
#displays data and its detailed info with download button
"""
def data_detail(request,data_set_id):
    user=request.user
    data_restriction=''
    data_details=DataSet.objects.get(id=data_set_id)
    if not user in data_details.owners.all():
        data_restriction="Access Denied"
    if data_details.public == True:
        data_details=DataSet.objects.get(id=data_set_id)
        data_chosen=DataSet.objects.filter(public=True).distinct()
    else:
        data_chosen=DataSet.objects.filter(owners=user).distinct()
    return render_to_response("data_manager/data_detail.html", dict(user=request.user,
        data_chosen=data_chosen,data_restriction=data_restriction, data_details=data_details, 
        media_url=MEDIA_URL,media_root=MEDIA_ROOT, data_page=" class=active"))     
"""
Displays:
#form that allows base options to be edited
"""
def data_detail_more(request,data_set_id):
    user=request.user
    data_restriction=''
    data_details=DataSet.objects.get(id=data_set_id)
    
    if not user in data_details.owners.all():
        data_restriction="Access Denied"
    if data_details.public == True:
        data_details=DataSet.objects.get(id=data_set_id)
        data_chosen=DataSet.objects.filter(public=True).distinct()
    else:
        data_chosen=DataSet.objects.filter(owners=user).distinct()
    return render_to_response("data_manager/data_detail_more.html", dict(user=request.user, 
        data_details=data_details, media_url=MEDIA_URL,media_root=MEDIA_ROOT, data_page=" class=active"))     
"""
Displays:
#form that allows base options to be edited
"""
def data_edit(request,data_set_id):
    return HttpResponseRedirect('/')     
"""
Displays:
#form to edit a specific detail/ or add one
"""
def data_detail_edit(request):
    return HttpResponseRedirect('/')
"""
Displays:
#lists data sets with some info that are within a collection
"""
def collections(request):
    user=request.user
    data_chosen=Collection.objects.filter(owners=user).distinct()
    return render_to_response("data_manager/collections.html", dict(user=request.user,
        data_chosen=data_chosen,media_url=MEDIA_URL,media_root=MEDIA_ROOT, data_page=" class=active"))  
"""
Displays:
#lists data sets with some info that are within a collection
"""
def collection_detail(request,collection_id):
    user=request.user
    collection_chosen=Collection.objects.get(id=collection_id)
    return render_to_response("data_manager/collections.html", dict(user=request.user,
        collection_chosen=collection_chosen,media_url=MEDIA_URL,media_root=MEDIA_ROOT, data_page=" class=active"))      
"""
Displays:
#form for each field to edit if wanted
"""
def collection_detail_edit(request,collection_id):
    return HttpResponseRedirect('/') 

"""
Displays:
#lists available instruments with directories
"""
def directories(request):
    user=request.user
    data_chosen=DataRecorder.objects.filter(users=user).distinct()
    return render_to_response("data_manager/directories.html", dict(user=request.user,
        data_chosen=data_chosen,media_url=MEDIA_URL,media_root=MEDIA_ROOT, data_page=" class=active"))     

"""
Displays:
#folders transferred from an instrument
"""
def directories_instrument(request,instrument_slug):
    instrument = DataRecorder.objects.get(slug=instrument_slug)
    user = request.user
    data_path=DATA_ROOT+'/'+user.username+'/'+instrument.slug+'/'
    data_path2=DATA_ROOT+'\\'+user.username+'\\'+instrument.slug+'\\'
    directories=[]
    data_files=[]
    for dir_file in os.listdir(data_path):
        if os.path.isfile(data_path+dir_file):
            try:
                data_files.append(DataSet.objects.get(data_path=data_path+dir_file))
            except:
                data_files.append(DataSet.objects.get(data_path=data_path2+dir_file))
            #data_files.append(DataSet.objects.filter(Q(name=dir_file)|Q(data_original_path=data_path)))
        else:
            directories.append(dir_file)
    return render_to_response("data_manager/directories_instruments.html", dict(user=request.user,
        data_files=data_files,directories=directories, instrument=instrument_slug,
        media_url=MEDIA_URL,media_root=MEDIA_ROOT, data_page=" class=active"))           
"""
Displays:
#profile with the given user id
"""
def user_profile(request,user_id):
    user=request.user
    pro_user=User.objects.filter(id=user_id).distinct()
    pro_user=pro_user[0]
    patron_info = Patron.objects.get(user=pro_user)
    pub_data_chosen=DataSet.objects.filter(Q(owners=pro_user)|Q(public=True))
    shared_data_chosen=DataSet.objects.filter(Q(owners=user)|Q(owners=pro_user))
    return render_to_response("data_manager/user_profile.html", dict(user=request.user,
        pro_view_user=pro_user, pub_data=pub_data_chosen, shared_data=shared_data_chosen,
        patron=patron_info, media_url=MEDIA_URL,media_root=MEDIA_ROOT, profile =" class=active"))
"""
Displays:
#form for each field to edit if wanted
"""
def user_profile_edit(request):
    return HttpResponseRedirect('/')     
"""
###################################################
###################################################
#######################ALL BELOW###################
###################TO BE DEPRECATED################
###################################################
"""
def home(request):    
    chosen=''
    instruments=''
    collections=''
    repositories=''
    navpanel=''
    directories=''
    data_sets=''
     #Sets default values for variables obtained through .GET
    NoFile=''   #Sets what a null response should be (AKA what a file and directory cannot be named)
    try:
        cat=request.GET['cat']
    except: cat=NoFile
    try:
        pid=request.GET['id']
    except: pid=NoFile
    admin_true=False
    if request.user.is_authenticated():
        admin_true=True
    if request.user.is_authenticated():
        user = User.objects.get(username=request.user)
        instruments     = DataRecorder.objects.filter(Q(users=user) | Q(admin_owners=user)).distinct()
        collections     = Collection.objects.filter(Q(members=user) | Q(owners=user)).distinct()
        repositories    = Repository.objects.filter(Q(members=user) | Q(owners=user)).distinct()
        data_sets       = DataSet.objects.filter(owners=user)
    else:
        instruments     = DataRecorder.objects.filter(public=True).distinct()
        collections     = Collection.objects.filter(public=True).distinct()
        repositories    = Repository.objects.filter(public=True).distinct()
        data_sets       = DataSet.objects.filter(public=True)

    #Allows users to view what the puclic observes without cluttering their personal repositories
    public=''
    try: 
        public_true=request.GET['public']
        public='public=True&'
        instruments     = DataRecorder.objects.filter(public=True).distinct()
        collections     = Collection.objects.filter(public=True).distinct()
        repositories    = Repository.objects.filter(public=True).distinct()
        data_sets       = DataSet.objects.filter(public=True)
    except:
        pass


    pathDeconstruct = []
    pathDeconstruct.append(0)
    
    directories=[]
    files=[]
    content_title=''
    #The following directs to a view representative of the object chosen
    recorder=''
    if cat == "inst":
        content_title='DIRECTORY'
        recorder=DataRecorder.objects.filter(id=pid).distinct()
        recorder_slug=recorder[0].slug
        """
        SECTION SUMMARY: Build the contents of the data tree directly from existing directories
        .....suggested_improvements.....
        -create a different view for the observation of the data if a file is chosen
        -find a way to not reference the data directly.  This will put a heavy load on the storage directory
        """
        contents = ['None']
        if request.user.is_authenticated():
            user = User.objects.get(username=request.user)
            #The following is a hardcoded location of the data
            data_locator = DATA_ROOT + '/' + user.username + '/' + recorder_slug
            for i in range(0,pathDeconstruct[0]):
                data_locator = data_locator + '/' + pathDeconstruct[i+1]
            contents = os.listdir(data_locator)
        """
        SECTION SUMMARY: Differentiates between files and directories
        ......suggested_improvements.....
        -find a better way to identify a file (seeing a dot in the name does not mean its necessarily a file)
        """
        isFile=False
        for i in range(len(contents)):
            sample=contents[i]
            for n in range(len(sample)):
                if sample[n]=='.':
                    isFile=True
                    files.append(sample)
                    break
            if isFile==False:
                directories.append(sample)
            isFile=False
    chosen_data=[]
    if cat == "coll":
        content_title='REPOSITORY'
        chosen=Collection.objects.filter(id=pid).distinct()
        chosen_data=DataSet.objects.filter(collections=chosen).distinct()
        print chosen_data
    repository_data=[]
    if cat == "repo":
        content_title='COLLECTION'
        chosen=Repository.objects.filter(id=pid).distinct()
        chosen_data=Collection.objects.filter(repositories=chosen).distinct()
    recent_data=[]
    if cat == "data":
        content_title='INSTRUMENT'
        chosen_data=DataSet.objects.filter(id=pid).distinct()
    #albums = Album.objects.all()
    #if not request.user.is_authenticated():
    #   albums = albums.filter(public=True)
    try:
        chosen = chosen[0]
    except:
        chosen=chosen
    return render_to_response("data_manager/main.html", dict(user=request.user,
        media_url=MEDIA_URL,media_root=MEDIA_ROOT,instruments=instruments,collections=collections, cat=cat,
        repositories=repositories,NavigationPanel=navpanel,directories=directories,files=files,
        content_title=content_title, data_sets=data_sets,chosen_data=chosen_data,chosen=chosen,public=public,admin_true=admin_true))
def download(request):
    error=[]
    try:
        cat=request.GET['cat']
        error.append("Data category not declared")
    except: 
        cat=None
        error.append("No file at the location")
    pid=request.GET['id']
    data=DataSet.objects.filter(id=pid).distinct()
    data_set=''
    try:
        data_set=data[0]
    except:
        error.append("Data set not unique or not found within DB")
    for i in range(len(error)):
        print error[i]
    #response = HttpResponse.write(data_set.data_path)
    #response['Content-Disposition'] = 'attachment; filename="'+data_set.data_path+'"'
    #response['Content-Disposition'] = 'attachment; filename="2.jpg"'
    filepath =data_set.data_path
    print filepath
    if os.path.isfile(filepath):
        return serve(request, os.path.basename(filepath), os.path.dirname(filepath))
    else:
        return HttpResponseRedirect('/')

def search(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        entry_query = get_query(request, Image, ['title',])
        found_entries = Image.objects.filter(entry_query).order_by('created')
        attributes = Image._meta.get_all_field_names()
        #found_entries = ['NO MATCHES']
    return render_to_response('gallery/search_results.html',
                          dict( query_string =query_string, found_entries= found_entries,media_url=MEDIA_URL,numEntries=len(found_entries),attrib=attributes),
                          context_instance=RequestContext(request))

