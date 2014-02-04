from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.forms import ModelForm
from ncemhub.settings import MEDIA_URL
from data_manager.models import DataCharacteristic, Tag, DataRecorder, Repository, Collection, DataSet, Value
from django.template import RequestContext
from gallery.utils import generic_search as get_query
#from user_authentication.models import Patron
from django.contrib.auth.models import User
import os

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
def main(request):
    """Main listing."""
    #Develops the file contents
    contents = ['None']
    if request.user.is_authenticated():
        user = User.objects.get(username=request.user)
        """
        Find where each directory is listed, assuming that it is in a system that looks at 
        actual files:otherwise this should simply be a database search for instruments
        """
        
        data_locator = '../../../data' + '/' + user.username[0]  + '/' + user.username
        contents = os.listdir(data_locator)
    #Separate out files from directories
    #(there should not be any files anyways, but this is important)
    instruments=[]
    files=[]
    isFile=False
    for i in range(len(contents)):
        sample=contents[i]
        for n in range(len(sample)):
            if sample[n]=='.':
                isFile=True
                files.append(sample)
                break
        if isFile==False:
            instruments.append(sample)
        isFile=False
    instruments=''
    collections=''
    repositories=''
    navpanel=''
    directories=''
    if request.user.is_authenticated():
        instruments=DataRecorder.objects.all()
        collections=Collection.objects.all()
        repositories=Repository.objects.all()
    else:
        none=False
    return render_to_response("data_manager/main.html", dict(user=request.user,
        media_url=MEDIA_URL,instruments=instruments,collections=collections, 
        repositories=repositories,NavigationPanel=navpanel,directories=directories))
def data_set_detail(request):
    return render_to_response("data_manager/main.html", dict(user=request.user,
        media_url=MEDIA_URL))    
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
    
    #Patron,    user name user_location date_joined updated_at user_bio
    
    #Create characteristics
    characteristic1 = DataCharacteristic.objects.create(name="Lense")
    characteristic2 = DataCharacteristic.objects.create(name="Plane")
    characteristic3 = DataCharacteristic.objects.create(name="Thickness")
    f.write('Characteristics----Passed\n')
    tag1 = Tag.objects.create(tag="Carbon")
    tag2 = Tag.objects.create(tag="Graphite")
    tag3 = Tag.objects.create(tag="Symmetric")
    f.write('Tags----Passed\n')

    #recorder1 = DataRecorder.objects.create(name="Team I", public=True, slug="team_i", description = "A TEAM microscope", admin_owners = , users= ,tags = )
    #recorder2 = 
    #recorder3 = 
    
    # DataCharacteristic, name
    #Tag, tag
    #DataRecorder,     name public slug created_on updated_on   description  admin_owners users tags 
    #Repository,     name public created_on updated_on tags members owners
    #Collection,     name public created_on updated_on tags members owners data_recorder repositories 
    #DataSet,     name public created_on updated_on data_path image_rep_path description owners tags data_recorder collections data_char           = models.ManyToManyField(DataCharacteristic,through='Value', blank=True)
    #Value,      characteristic data_set text_value float_value         = models.FloatField()
    return HttpResponseRedirect('/data/manager/')