from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, render
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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
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


"""
Define common variables
"""
#FileDelimeter is the object used to show a new directory depth in the url.
FileDelimeter= '---'
PER_PAGE=15

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
def main(request):
    data_chosen  = DataSet.objects.filter(public=True).distinct()
    collection_chosen = Collection.objects.filter(public=True).distinct()
    paginator = Paginator(data_chosen,PER_PAGE)
    page= request.GET.get('page')
    try:
        datas = paginator.page(page)
    except PageNotAnInteger:
        datas = paginator.page(1)
    except EmptyPage:
        datas = paginator.page(paginator.num_pages)
    return render_to_response("data_manager/main.html", dict(user=request.user,
        media_url=MEDIA_URL, data_chosen=datas,paginator=paginator,collections=collection_chosen, home=" class=active"))


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
    paginator = Paginator(data_chosen,PER_PAGE)
    page= request.GET.get('page')
    try:
        datas = paginator.page(page)
    except PageNotAnInteger:
        datas= paginator.page(1)
    except EmptyPage:
        datas = paginator.page(paginator.num_pages)
    return render_to_response("data_manager/user_data.html", dict(user=request.user,
        data_chosen=datas,media_url=MEDIA_URL, paginator=paginator,data_page=" class=active"))  
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
        if not data_details.public == True:
            return HttpResponseRedirect('/')
    if data_details.public == True:
        data_details=DataSet.objects.get(id=data_set_id)
        data_chosen=DataSet.objects.filter(public=True).distinct()
    else:
        data_chosen=DataSet.objects.filter(owners=user).distinct()


    paginator = Paginator(data_chosen,PER_PAGE)
    page= request.GET.get('page')
    try:
        datas = paginator.page(page)
    except PageNotAnInteger:
        datas= paginator.page(1)
    except EmptyPage:
        datas = paginator.page(paginator.num_pages)
    return render_to_response("data_manager/data_detail.html", dict(user=request.user,
        data_chosen=datas,data_restriction=data_restriction, data_details=data_details, 
        media_url=MEDIA_URL, paginator=paginator,data_page=" class=active"))     
"""
Displays:
#all info for a single data set and links to edit data
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
        data_details=data_details, media_url=MEDIA_URL, data_page=" class=active"))     
"""
Displays:
#form that allows a specific characteristic to be edited
"""
def data_detail_characteristic(request,data_set_id,detail_id):
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
    return HttpResponseRedirect('/')
"""
Displays:
#form that allows base options to be edited
"""
def sep_posted_value(string_values):
    n=0
    real_list=[]
    for i in range(len(string_values)):
        if string_values[i]==',':

            real_list.append(string_values[n:i])
            n=i+1
            print string_values[n:i] 
    return real_list
def data_edit(request,data_set_id):
    user=request.user
    if user.is_authenticated:
        data_set=DataSet.objects.get(id=data_set_id)
        if user in data_set.owners.all():
            #allowed to edit the data_set
            error = "None"
        else:
            if data_set.public == True:
                error = "You may view this but not edit it"
            else:
                error = "You cannot view nor edit this data"
                return HttpResponseRedirect("/")
    else:
        if data_set.public == True:
            error = "You may view this but not edit it"
        else:
            error = "You cannot view nor edit this data"
            return HttpResponseRedirect("/")
    if request.method == 'POST':
        form = request.POST
        data_set.name = form['name']
        data_set.description=form['description']

        errors=[]

        owners=form['owners']
        owners=sep_posted_value(owners)
        owners_current=[]
        for i in data_set.owners.all():
            owners_current.append(i.username)
        #owner must be added to current
        for i in owners:
            if not i in owners_current:
                #owner must be added to current
                try:
                    new_owner=User.objects.get(username=i)
                    data_set.owners.add(new_owner)
                except:
                    error= "fail add", i
        #owner must be deleted from current
        for i in owners_current:
            if not i in owners:
                try:
                    new_owner=User.objects.get(username=i)
                    data_set.owners.remove(new_owner)
                except:
                    error= "fail remove", i
            
        tags=form['tags']
        tags=sep_posted_value(tags) 
        tags_current=[]
        for i in data_set.tags.all():
            tags_current.append(i.tag)
        #tag must be added to current
        for i in tags:
            if not i in tags_current:
                #tag must be added to current
                try:
                    new_tag=Tag.objects.get(tag=i)
                    data_set.tags.add(new_tag)
                except:
                    error= "fail add", i
        #tag must be deleted from current
        for i in tags_current:
            if not i in tags:
                try:
                    new_tag=Tag.objects.get(tag=i)
                    data_set.tags.remove(new_tag)
                except:
                    error= "fail remove", i
        
        recorders=form['recorders']
        recorders=sep_posted_value(recorders)
        recorders_current=data_set.data_recorder.all()
        print 'recorders',recorders
        recorders_current=[]
        for i in data_set.data_recorder.all():
            recorders_current.append(i.name)
        #recorder must be added to current
        for i in recorders:
            if not i in recorders_current:
                #recorder must be added to current
                try:
                    new_recorder=DataRecorder.objects.get(name=i)
                    data_set.data_recorder.add(new_recorder)
                except:
                    error= "fail add", i
        #recorder must be deleted from current
        for i in recorders_current:
            if not i in recorders:
                try:
                    new_recorder=DataRecorder.objects.get(name=i)
                    data_set.data_recorder.remove(new_recorder)
                except:
                    error= "fail remove", i
            
        collections=['collections']
        collections=sep_posted_value(collections)
        collections_current=[]
        for i in data_set.collections.all():
            collections_current.append(i.name)
        #owner must be added to current
        for i in collections:
            if not i in collections_current:
                #owner must be added to current
                try:
                    new_collection=Collection.objects.get(name=i)
                    data_set.collections.add(new_collection)
                except:
                    error= "fail add", i
        #owner must be deleted from current
        for i in collections_current:
            if not i in collections:
                try:
                    new_collection=Collection.objects.get(name=i)
                    data_set.collections.remove(new_collection)
                except:
                    error= "fail remove", i
            
        data_set.save()
        return HttpResponseRedirect("/data/"+str(data_set.id)+"/more")
    return render_to_response("data_manager/data_set_edit.html", dict(user=user, 
        media_url=MEDIA_URL,data_details=data_set ,data_page=" class=active"),
        context_instance=RequestContext(request))     
"""
    if request.user.is_authenticated():
        return HttpResponseRedirect('/user/profile')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user=User.objects.create_user(username=form.cleaned_data['username'],email = form.cleaned_data['email'], password = form.cleaned_data['password'])      
            user.save()
            # \/ \/ \/ MAKES USER FOLDER! \/  \/  \/
            #os.mkdir('../../../data/'+ user.slug[0] + '/' + user.slug)
            #patron = user.get_profile()
            #patron.name = form.cleaned_date['name']
            #patron.user_location = form.cleaned_data['user_location']
            #patron.save()
            patron = Patron(user=user, first_name=form.cleaned_data['first_name'],last_name=form.cleaned_data['last_name'], user_location=form.cleaned_data['user_location'])
            patron.save()
            return HttpResponseRedirect('/profile/'+str(user.id))
        else:
            return render_to_response('user_authentication/register.html',{'form':form}, context_instance=RequestContext(request))
    
    else:
        ''' user is not submitting the form, show them a blank registration form'''
        form = RegistrationForm()
        context = {'form':form}
        return render_to_response('user_authentication/register.html',context,context_instance=RequestContext(request))
#login required
"""

"""
Displays:
#form to edit a specific detail/ or add one
"""
def data_detail_edit(request,data_set_id):
    user=request.user
    if user.is_authenticated:
        data_set=DataSet.objects.get(id=data_set_id)
        if user in data_set.owners.all():
            #allowed to edit the data_set
            error = "None"
        else:
            if data_set.public == True:
                error = "You may view this but not edit it"
            else:
                error = "You cannot view nor edit this data"
                return HttpResponseRedirect("/")
    else:
        if data_set.public == True:
            error = "You may view this but not edit it"
        else:
            error = "You cannot view nor edit this data"
            return HttpResponseRedirect("/")
    if request.method == 'POST':
        form = request.POST
        data_set.name = form['name']
        data_set.save()
        return HttpResponseRedirect("/")
    return render_to_response("data_manager/data_set_edit.html", dict(user=user, 
        media_url=MEDIA_URL,data_details=data_set ,data_page=" class=active"),
        context_instance=RequestContext(request))
"""
Displays:
#lists data sets with some info that are within a collection
"""
def collections(request):
    user=request.user
    data_chosen=Collection.objects.filter(owners=user).distinct()
    return render_to_response("data_manager/collections.html", dict(user=request.user,
        data_chosen=data_chosen,media_url=MEDIA_URL, data_page=" class=active"))  
"""
Displays:
#lists data sets with some info that are within a collection
"""
def collection_detail(request,collection_id):
    user=request.user
    collection_chosen=Collection.objects.get(id=collection_id)
    return render_to_response("data_manager/collections.html", dict(user=request.user,
        collection_chosen=collection_chosen,media_url=MEDIA_URL, data_page=" class=active"))      
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
        data_chosen=data_chosen,media_url=MEDIA_URL, data_page=" class=active"))     

"""
Displays:
#folders transferred from an instrument
"""
def directories_instrument(request,instrument_slug):
    instrument = DataRecorder.objects.get(slug=instrument_slug)
    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect('/')
    if os.name == 'nt':
        path_sep='\\'
    else:
        path_sep='/'
    data_path=DATA_ROOT+path_sep+user.username+path_sep+instrument.slug+path_sep
    
    try:
        path=request.GET['path']
    except:
        path=''
    path_current=path
    try: 
        directory=request.GET['directory']
    except:
        directory=''
    directory_current=directory
    try:
        year_passed=int(request.GET['year'])
    except:
        year_passed=''
    try:
        month_passed=int(request.GET['month'])
    except:
        month_passed=''
    
    if path == '':
        if directory=='':
            data_path=data_path
        else:    
            data_path=data_path+directory+path_sep
            path=directory
    else:
        data_path=data_path+path+path_sep+directory+path_sep
        path=path+path_sep+directory
    directories=[]
    data_files=[]
    for dir_file in os.listdir(data_path):
        if os.path.isfile(data_path+dir_file):
            try:
                data_files.append(DataSet.objects.get(data_path=data_path+dir_file))
            except:
                error = dir_file," is not coherrent with db: data_manager.views.directories_instrument"
            #data_files.append(DataSet.objects.filter(Q(name=dir_file)|Q(data_original_path=data_path)))
        else:
            directories.append(dir_file)
    class Years():
        year=2000
        month_name={
            1:'JAN',
            2:'FEB',
            3:'MAR',
            4:'APR',
            5:'MAY',
            6:'JUN',
            7:'JUL',
            8:'AUG',
            9:'SEP',
            10:'OCT',
            11:'NOV',
            12:'DEC',
        }
        def __unicode__(self):
            self.year
        def __init__(self):
            self.months = []
    year_list=[]
    years_list=[]
    for i in data_files:
        if not i.created_on.year in year_list:
            year_now=Years()
            year_now.year=i.created_on.year
            years_list.append(year_now)
            year_list.append(i.created_on.year)
        for n in years_list:
            if i.created_on.year==n.year:
                if not i.created_on.month in n.months:
                    n.months.append(i.created_on.month)
    print data_files
    if not year_passed=='':
        for d_file in reversed(data_files):
            print d_file
            if not d_file.created_on.year==year_passed:
                data_files.remove(d_file)
    if not month_passed=='':
        for d_file in reversed(data_files):
            if not d_file.created_on.month==month_passed:
                data_files.remove(d_file)
    paginator = Paginator(data_files,PER_PAGE)
    page= request.GET.get('page')
    try:
        data_files = paginator.page(page)
    except PageNotAnInteger:
        data_files= paginator.page(1)
    except EmptyPage:
        data_files = paginator.page(paginator.num_pages)
    class bread_crumbs():
        path = ''
        dir_name = ''
        directory= ''
        def __unicode__(self):
            return self.dir_name

    """
    Bread CRUMBS
    -develops a class of the following
    bread_crumb[i] = name of back track
    bread_crumb[i].link = link to back track
    """
    n=0
    bread_crumb_list=[]
    for i in range(len(path)):
        if path[i] == path_sep:
            new_crumb=bread_crumbs()
            if n==0:
                new_crumb.path=path[:n]
            else:        
                new_crumb.path=path[:n-1]
            new_crumb.dir_name=path[n:i]
            bread_crumb_list.append(new_crumb)
            n=i+1

    year_list=[]

    if directories==[]:
        directories=''
    return render_to_response("data_manager/directories_instruments.html", dict(user=request.user,
        data_chosen=data_files,directories=directories, instrument=DataRecorder.objects.get(slug=instrument_slug),
        media_url=MEDIA_URL,paginator=paginator,bread_crumbs=bread_crumb_list,directory=directory,
        media_root=MEDIA_ROOT, data_page=" class=active", path=path,years=years_list,
        path_current=path_current,directory_current=directory_current))           
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

    paginator = Paginator(shared_data_chosen,PER_PAGE)
    page= request.GET.get('page')
    try:
        datas = paginator.page(page)
    except PageNotAnInteger:
        datas= paginator.page(1)
    except EmptyPage:
        datas = paginator.page(paginator.num_pages)
    return render_to_response("data_manager/user_profile.html", dict(user=request.user,
        pro_view_user=pro_user, #pub_data=pub_data_chosen, 
        data_chosen=datas, paginator=paginator,
        patron=patron_info, media_url=MEDIA_URL, profile =" class=active"))
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
        media_url=MEDIA_URL,instruments=instruments,collections=collections, cat=cat,
        repositories=repositories,NavigationPanel=navpanel,directories=directories,files=files,
        content_title=content_title, data_sets=data_sets,chosen_data=chosen_data,chosen=chosen,
        public=public,admin_true=admin_true))
def download(request,data_set_id):
    error=[]
    pid=data_set_id
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
    filepath = data_set.data_path
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
                          dict( query_string =query_string, found_entries= found_entries,media_url=MEDIA_URL,
                            numEntries=len(found_entries),attrib=attributes),
                          context_instance=RequestContext(request))

