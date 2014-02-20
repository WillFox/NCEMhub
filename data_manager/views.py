from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.forms import ModelForm
from ncemhub.settings import MEDIA_URL, DATA_ROOT, MEDIA_ROOT
from data_manager.models import DataCharacteristic, Tag, DataRecorder, Repository, Collection, DataSet, Value
from django.template import RequestContext
from gallery.utils import generic_search as get_query
from user_authentication.models import Patron
from django.contrib.auth.models import User
import os
from django.db.models import Q
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

def instrumentDirectoryView(request,microscopeName,cat):
   
    """
    File Structure Interpreter
    """
    #Sets default values for variables obtained through .GET
    NoFile=''   #Sets what a null response should be (AKA what a file and directory cannot be named)
    try:
        prefixBefore=request.GET['prefix']
    except: prefixBefore=NoFile
    try:
        currentDirectory=request.GET['currentdirectory']
    except: currentDirectory=NoFile
    try:
        currentFileName=request.GET['file']
    except: currentFileName = NoFile
    """
    SECTION SUMMARY: (read note on side)
    """
    if len(prefixBefore)<1:
        prefixBeforeExist=False
    else:
        prefixBeforeExist=True
    if len(currentDirectory)<1:
        currentDirectoryExist=False         ####VERIFIES WHAT WAS PASSED IN URL####
    else:
        currentDirectoryExist=True
    if len(currentFileName)<1:
        currentFileNameExist=False
    else:
        currentFileNameExist=True
    return 0
    ##################################
    #I will have to code for the case of 4 or 5 dashes in a row if we keep the FileDelimeter.... gah stupid user
    #deconstruct file structure into list
    """
    SECTION SUMMARY: Builds pathDeconstructor
    this list will hold the number of directory levels accessed in the tree such as
      1     2     3         4       <--Level accessed
    users/data/microscope/info/
    
    First item in list is the number of "Levels" accessed, followed by each level's name as an appended item
    .....suggested_improvements.....
    This could have been substituted with len(list) and skipped the first item of the list,
    but i already did it this way
    """
"""
    pathDeconstruct = []
    pathDeconstruct.append(0)
    if prefixBeforeExist==True:
        sample = 'abc'
        i=0
        n=0
        while i < len(prefixBefore):
            sample=prefixBefore[i:i+3]
            if sample==FileDelimeter:
                pathDeconstruct[0]=pathDeconstruct[0]+1
                pathDeconstruct.append(prefixBefore[n:i])
                n=i+3
            i= i+1
        if pathDeconstruct[0]>0:
            pathDeconstruct.append(prefixBefore[n:i])
        if pathDeconstruct[0]<1:
            pathDeconstruct.append(prefixBefore)
        pathDeconstruct[0]=pathDeconstruct[0]+1
    if currentDirectoryExist == True:
        pathDeconstruct.append(currentDirectory)
        pathDeconstruct[0]=pathDeconstruct[0]+1
    prefix=''   #Initializing to blank strings so that they do not show up when not initialized
    backone=''  #Which is sometimes the case
    pastDirectory=''
    if currentDirectoryExist==True:
        if prefixBeforeExist == True:
            prefix=prefixBefore+FileDelimeter+currentDirectory
        else:
            prefix=currentDirectory
    if prefixBeforeExist==True:
        pastDirectory=pathDeconstruct[pathDeconstruct[0]-1]
        if pathDeconstruct[0]>1:
            for i in range(pathDeconstruct[0]-2):
                backone=backone+pathDeconstruct[i+1]
                if i<pathDeconstruct[0]-3:
                    backone=backone+FileDelimeter
    if currentFileNameExist==True:
        prefix=prefixBefore
"""



def main(request):
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
            data_locator = DATA_ROOT + '/' + user.username[0] + '/' + user.username + '/' + recorder_slug
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
    return render_to_response("data_manager/main.html", dict(user=request.user,
        media_url=MEDIA_URL,media_root=MEDIA_ROOT,instruments=instruments,collections=collections, cat=cat,
        repositories=repositories,NavigationPanel=navpanel,directories=directories,files=files,
        content_title=content_title, data_sets=data_sets,chosen_data=chosen_data,public=public,admin_true=admin_true))
def download(request):
    response = HttpResponse(MEDIA_ROOT+'2.jpg')
    response['Content-Disposition'] = 'attachment; filename="2.jpg"'
    return response
    """
    Thanks Florian, but I am still confused about what's happening. Below 
    is the concept of my codes and perhaps you can help: 

    from django.core.files import File  

    some_file  = open('bla/bla/bla/', "rw") 
    django_file = File(some_file) 

    t = loader.get_gemplate('somewhere/temp.html') 
    c = Context({'file':django_file}) 
    return HttpResponse(t.render(c)) 


    ### in the template #### 
    <a href="file:///{{ django_file.url }}>download</a> 


    This may actually work but i would rather not have it work like this :/... drool
    """
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
            data_locator = DATA_ROOT + '/' + user.username[0] + '/' + user.username + '/' + recorder_slug
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
    return HttpResponseRedirect('/data/manager/')     
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
    return HttpResponseRedirect('/data/manager/')