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
from user_authentication.models import Patron
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
    patron1 = Patron.objects.create( user= user1, name="Colin Ophus", user_location="NCEM Berkeley",user_bio="A scientist")
    patron2 = Patron.objects.create( user= user2, name="David E. Skinner", user_location="NERSC Oakland",user_bio="Another scientist")
    patron3 = Patron.objects.create( user= user3, name="William Fox", user_location="NCEM Berkeley and NERSC Oakland",user_bio="The last scientist")
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
    data1 = DataSet.objects.create(name="ISOpropyl",public=True,data_path="../../../data/w",image_rep_path="www/media",
        description="Alcohol on a thin plane")
    #,owners=[user1],tags=[tag1,tag3], data_recorder=[recorder1],collections=[collection3]
    data2 = DataSet.objects.create(name="Carbon nano tubes",public=True,data_path="../../../data/x",image_rep_path="www/media",
        description="graphite induce nano tubes")
    #,owners=[user1],tags=[tag1,tag2,tag3], data_recorder=[recorder2],collections=[collection2]
    data3 = DataSet.objects.create(name="TestDataRun",public=True,data_path="../../../data/c",image_rep_path="www/media",
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