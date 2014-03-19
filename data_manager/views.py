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
        media_url=MEDIA_URL,media_root=MEDIA_ROOT, data_sets=data_chosen,collections=collection_chosen))


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
        data_chosen=data_chosen,media_url=MEDIA_URL,media_root=MEDIA_ROOT))  
"""
Displays:
#displays data and its detailed info with download button
"""
def data_detail(request):
    return HttpResponseRedirect('/')     
"""
Displays:
#form that allows base options to be edited
"""
def data_edit(request):
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
        data_chosen=data_chosen,media_url=MEDIA_URL,media_root=MEDIA_ROOT))  
"""
Displays:
#lists data sets with some info that are within a collection
"""
def collection_detail(request):
    return HttpResponseRedirect('/')     
"""
Displays:
#form for each field to edit if wanted
"""
def collection_detail_edit(request):
    return HttpResponseRedirect('/') 

"""
Displays:
#lists available instruments with directories
"""
def directories(request):
    user=request.user
    data_chosen=DataRecorder.objects.filter(users=user).distinct()
    return render_to_response("data_manager/directories.html", dict(user=request.user,
        data_chosen=data_chosen,media_url=MEDIA_URL,media_root=MEDIA_ROOT))     

"""
Displays:
#folders transferred from an instrument
"""
def directories_instrument(request):
    return HttpResponseRedirect('/')       
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
        patron=patron_info, media_url=MEDIA_URL,media_root=MEDIA_ROOT))
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


def admin(request):
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
        instruments     = DataRecorder.objects.filter(admin_owners=user).distinct()
        collections     = Collection.objects.filter(owners=user).distinct()
        repositories    = Repository.objects.filter(owners=user).distinct()
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
        chosen_data=Repository.objects.filter(id=pid).distinct()
    recent_data=[]
    if cat == "data":
        content_title='INSTRUMENT'
        chosen_data=DataSet.objects.filter(id=pid).distinct()
    #albums = Album.objects.all()
    #if not request.user.is_authenticated():
    #   albums = albums.filter(public=True)
    return render_to_response("data_manager/admin.html", dict(user=request.user,
        media_url=MEDIA_URL,instruments=instruments,collections=collections, cat=cat,
        repositories=repositories,NavigationPanel=navpanel,directories=directories,files=files,
        content_title=content_title, data_sets=data_sets,chosen_data=chosen_data,public=public,admin_true=admin_true))   
def edit(request):
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

def initiate_database(request):
    f = open('/project/projectdirs/ncemhub/ncemhub/bin/LOGncemhubDBcreation.txt','w')
    f.write('This is a test\n')
    #Create Users
    user1 = User.objects.create_user(username="cophus",password="123123")
    user2 = User.objects.create_user(username="deskinner", password = "123123")
    user3 = User.objects.create_user(username="wsfox", password = "123123")
    f.write('Users Created----Passed\n')
    #Fill in Patron info (Broad name of users)
    patron1 = Patron.objects.create( user= user1, first_name="Colin", last_name="Ophus", user_location="NCEM Berkeley",user_bio="A scientist")
    patron2 = Patron.objects.create( user= user2, first_name="David", last_name="Skinner",user_location="NERSC Oakland",user_bio="Another scientist")
    patron3 = Patron.objects.create( user= user3, first_name="William", last_name="Fox",user_location="NCEM Berkeley and NERSC Oakland",user_bio="The last scientist")
    f.write('Patrons Created from Users----Passed\n')
    #Patron,    user name user_location date_joined updated_at user_bio
    #Create characteristics
    characteristic1 = DataCharacteristic.objects.create(name="Lense")
    characteristic2 = DataCharacteristic.objects.create(name="Plane")
    characteristic3 = DataCharacteristic.objects.create(name="Thickness")
    f.write('Characteristics----Passed\n')
    # DataCharacteristic, name

    #Create Tags
    tag1 = Tag.objects.create(tag="Carbon")
    tag2 = Tag.objects.create(tag="Graphite")
    tag3 = Tag.objects.create(tag="Symmetric")
    f.write('Tags----Passed\n')
    #Tag, tag
    
    #Create Recorders
    recorder1 = DataRecorder.objects.create(name="TEAM I", public=True, slug="team_i", 
        description = "A TEAM microscope")
    #, admin_owners = user1, users= [user1,user2,user3],tags = [tag1]
    recorder2 = DataRecorder.objects.create(name="TEAM 0.5", public=True, slug="team_0.5", 
        description = "Another team microscope")
    #, admin_owners = user2, users= [user1,user3] ,tags = [tag1,tag2]
    recorder3 = DataRecorder.objects.create(name="LIBRA", public=True, slug="libra", 
        description = "A libra microscope")
    #, admin_owners = user1, users= [user1],tags = [tag1]
    f.write('Recording Instruments Create----Passed\n')
    recorder1.admin_owners.add(user1)
    recorder1.users.add(user1,user2,user3)
    recorder1.tags.add(tag1)

    recorder2.admin_owners.add(user2)
    recorder2.users.add(user1,user3)
    recorder2.tags.add(tag1,tag2)

    recorder3.admin_owners.add(user1)
    recorder3.users.add(user1)
    recorder3.tags.add(tag1)
    f.write('Recording Instruments Modified----Passed\n')
    #DataRecorder,     name public slug created_on updated_on   description  admin_owners users tags 
    
    #Create Repositories
    repository1 = Repository.objects.create(name="Biophysics",public=False)
    #, tags=[tag1],members=[user1,user2,user3],owners=[user1]
    repository2 = Repository.objects.create(name="Genome",public=True)
    #, tags=[tag1,tag3], members=[user1],owners=[user1]
    repository3 = Repository.objects.create(name="Materials Science Divission",public=False)
    #, tags=[tag1,tag2,tag3],members=[user3],owners=[user1]
    f.write('Repositories Created----Passed\n')
    repository1.tags.add(tag1)
    repository1.members.add(user1,user2,user3)
    repository1.owners.add(user1)

    repository2.tags.add(tag1,tag3)
    repository2.members.add(user1)
    repository2.owners.add(user1)

    repository3.tags.add(tag1,tag2,tag3)
    repository3.members.add(user3)
    repository3.owners.add(user1)
    f.write('Repositories Modified----Passed\n')    
    #Repository,     name public created_on updated_on tags members owners

    #Create Collections
    collection1 = Collection.objects.create(name = "NCEM", public=False)
    #, tags=[tag1,tag3], members=[user1],owners=[user2],data_recorder=[recorder1],repositories=[repository1]
    collection2 = Collection.objects.create(name = "NERSC", public=False)
    #, tags=[tag1,tag3], members=[user2],owners=[user2],data_recorder=[recorder1],repositories=[repository2,repository3]
    collection3 = Collection.objects.create(name = "ALL", public=True)
    #, tags=[tag1,tag2,tag3], members=[user1],owners=[user2],data_recorder=[repository2,repository3],repositories=[repository1,repository2]
    f.write('Collections Created----Passed\n')
    collection1.tags.add(tag1,tag3)
    collection1.members.add(user1)
    collection1.owners.add(user2)
    collection1.data_recorder.add(recorder1)
    collection1.repositories.add(repository1)

    collection2.tags.add(tag1,tag3)
    collection2.members.add(user2)
    collection2.owners.add(user2)
    collection2.data_recorder.add(recorder1)
    collection2.repositories.add(repository2,repository3)

    collection3.tags.add(tag1,tag2,tag3)
    collection3.members.add(user1)
    collection3.owners.add(user2)
    collection3.data_recorder.add(recorder2,recorder3)
    collection3.repositories.add(repository1,repository2)
    f.write('Collections Modified----Passed\n')
    #Collection,     name public created_on updated_on tags members owners data_recorder repositories 

    #Create Data Sets
    data1 = DataSet.objects.create(name="ISOpropyl",public=True,data_original_path="",data_path=MEDIA_URL+"data/",image_rep_path=MEDIA_URL+"data/2.jpg",
        description="Alcohol on a thin plane")
    #,owners=[user1],tags=[tag1,tag3], data_recorder=[recorder1],collections=[collection3]
    data2 = DataSet.objects.create(name="Carbon nano tubes",public=True,data_original_path="",data_path=MEDIA_URL+"data/",image_rep_path=MEDIA_URL+"data/3.jpg",
        description="graphite induce nano tubes")
    #,owners=[user1],tags=[tag1,tag2,tag3], data_recorder=[recorder2],collections=[collection2]
    data3 = DataSet.objects.create(name="TestDataRun",public=True,data_original_path="",data_path=MEDIA_URL+"data/",image_rep_path=MEDIA_URL+"data/4.jpg",
        description="this is a test")
    #,owners=[user2],tags=[tag1,tag2], data_recorder=[recorder3],collections=[collection1]
    f.write('Data Set Creation----Passed\n')
    data1.owners.add(user1)
    data1.tags.add(tag1,tag3)
    data1.data_recorder.add(recorder1)
    data1.collections.add(collection3)

    data2.owners.add(user1)
    data2.tags.add(tag1,tag2,tag3)
    data2.data_recorder.add(recorder2)
    data2.collections.add(collection2)

    data3.owners.add(user2)
    data3.tags.add(tag1,tag2)
    data3.data_recorder.add(recorder3)
    data3.collections.add(collection1)
    f.write('Data Set Modification----Passed\n')
    #DataSet,     name public created_on updated_on data_path image_rep_path description owners tags data_recorder collections data_char
    value1 = Value(characteristic = characteristic1, data_set = data1,
        text_value = "Confocal")
    value1.save()
    #characteristic = characteristic1, data_set = data1,
    value2 = Value(characteristic = characteristic2, data_set = data1,
        text_value = "X",)
    value2.save()
    #characteristic = characteristic2, data_set = data1,
    value3 = Value(characteristic = characteristic3, data_set = data1,
        float_value = "0.03")
    value3.save()
    #characteristic = characteristic3, data_set = data1,
    #**********************************
    value4 = Value(characteristic = characteristic1, data_set = data2,
        text_value = "Elliptic")
    value4.save()
    #characteristic = characteristic1, data_set = data1,
    value5 = Value(characteristic = characteristic2, data_set = data2,
        text_value = "Y")
    value5.save()
    #characteristic = characteristic2, data_set = data1,
    value6 = Value(characteristic = characteristic3, data_set = data2,
        float_value = "0.08")
    value6.save()
    #characteristic = characteristic3, data_set = data1,
    #***********************************
    value7 = Value(characteristic = characteristic1, data_set = data3,
        text_value = "Spherical")
    value7.save()
    #characteristic = characteristic1, data_set = data1,
    value8 = Value(characteristic = characteristic2, data_set = data3,
        text_value = "Y")
    value8.save()
    #characteristic = characteristic2, data_set = data1,
    value9 = Value(characteristic = characteristic3, data_set = data3,
        float_value = "1.09")
    value9.save()
    #characteristic = characteristic3, data_set = data1,
    #chars:::lens,plane,thickness
    #Create Values for the chars... somehow
    f.write('Values----Passed\n')
    #Value,      characteristic data_set text_value float_value         = models.FloatField()
    return HttpResponseRedirect('/')