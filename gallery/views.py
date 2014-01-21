from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.forms import ModelForm
from ncemhub.settings import MEDIA_URL
from gallery.models import Album, Tag, Image
from django.template import RequestContext
from gallery.utils import generic_search as get_query
from user_authentication.models import Patron
from django.contrib.auth.models import User
import os

FileDelimeter= '---'

def main(request):
    """Main listing."""
    #Develops the file contents
    contents = ['None']
    if request.user.is_authenticated():
        user = User.objects.get(username=request.user)
        data_locator = '../../../data' + '/' + user.username[0]  + '/' + user.username
        contents = os.listdir(data_locator)

    albums = Album.objects.all()
    if not request.user.is_authenticated():
        albums = albums.filter(public=True)

    paginator = Paginator(albums, 10)
    try: page = int(request.GET.get("page", '1'))
    except ValueError: page = 1


    try:
        albums = paginator.page(page)
    except (InvalidPage, EmptyPage):
        albums = paginator.page(paginator.num_pages)

    for album in albums.object_list:
        album.images = album.image_set.all()[:4]

    return render_to_response("gallery/list.html", dict(albums=albums, user=request.user,
        media_url=MEDIA_URL,contents=contents))

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

def album_content(request, albumName):
    """View the contents of an album/collection"""
    album = Album.objects.get(title=albumName)
    
    if not request.user.is_authenticated():
        if not album.public:
            album = Album.objects.all().filter(public= True)
    album.images = album.image_set.all()
    attrib = album.image_set.values().field_names
    if request.user.is_authenticated():
        img = album.image_set.all().filter(user=request.user)
    contents = ['',]
    #file contents of user
    
    return render_to_response("gallery/image_list.html", dict(album=album, user=request.user,
        media_url=MEDIA_URL))
#Provides a view of all albums and microscopes once 
def fileStructureView(request):
    """View the content of the file in a list"""
    user= User.objects.get(slug=userslug)
    data_locator= '../../../data/' + user.slug[0] +'/'+ user.slug
    #microscope_list=user.micros_used.all().values('slug')
    microscope_list = os.listdir(data_locator)#lists folder present for each                        #microscope used by user
    microscopes = user.micros_used.all()
    #microscopes = user.micros_used.all().values('name')
    #passed_list = [microscopes, microscope_list]
    context ={
            'user':user,
            #'microscope':passed_list
            #'microscopes':microscopes,
            'microscope':microscopes,
            'microscope_slug':microscope_list
            
        }
    #return render_to_response('directory_list/user_info.html',context,context_instance=RequestContext(request))

    """View the contents of an album/collection"""
    album = Album.objects.get(title=albumName)
    
    if not request.user.is_authenticated():
        if not album.public:
            album = Album.objects.all().filter(public= True)
    album.images = album.image_set.all()
    attrib = album.image_set.values().field_names
    if request.user.is_authenticated():
        img = album.image_set.all().filter(user=request.user)
    return render_to_response("gallery/image_list.html", dict(album=album, user=request.user,
        media_url=MEDIA_URL))
    return HttpResponseRedirect('/gallery')

#SUMMARY: Provides a view so that the user can look through there microscopy directories from other microscopes
#.....suggested_improvements.....
#
#
def microscopeListView(request,microscopeName):
   
    """File Structure Interpreter"""
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
    
    #SUMMARY: (read note on side)
    #################################
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
    ##################################
    #I will have to code for the case of 4 or 5 dashes in a row if we keep the FileDelimeter.... gah stupid user
    #deconstruct file structure into list
    def deconstruct(pathDeconstruct, prefixBefore):
        sample = 'abc'
        i=0
        n=0
        while i < len(prefixBefore):
            sample=prefixBefore[i:i+2]
            if sample==FileDelimeter:
                pathDeconstruct[0]=pathDeconstruct[0]+1
                pathDeconstruct.append(prefixBefore[n:i])
                n=i+2
            i= i+1
        return pathDeconstruct
    #SECTION SUMMARY: Builds pathDeconstructor
    #this list will hold the number of directory levels accessed in the tree such as
    #  1     2     3         4       <--Level accessed
    #users/data/microscope/info/
    #
    #First item in list is the number of "Levels" accessed, followed by each level's name as an appended item
    #.....suggested_improvements.....
    #This could have been substituted with len(list) and skipped the first item of the list,
    #but i already did it this way
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


    #SECTION SUMMARY: Build the contents of the data tree directly from existing directories
    #.....suggested_improvements.....
    #-separate the files from directories and utilize the separate passed variables for this
    #-create a different view for the observation of the data if a file is chosen
    #-find a way to not reference the data directly.  This will put a heavy load on the storage directory
    contents = ['None']
    if request.user.is_authenticated():
        user = User.objects.get(username=request.user)
        #The following is a hardcoded location of the data
        data_locator = '../../../data' + '/' + user.username[0] + '/' + user.username + '/' + microscopeName
        for i in range(0,pathDeconstruct[0]):
            data_locator = data_locator + '/' + pathDeconstruct[i+1]
        contents = os.listdir(data_locator)

    albums = Album.objects.all()
    if not request.user.is_authenticated():
        albums = albums.filter(public=True)

    paginator = Paginator(albums, 10)
    try: page = int(request.GET.get("page", '1'))
    except ValueError: page = 1


    try:
        albums = paginator.page(page)
    except (InvalidPage, EmptyPage):
        albums = paginator.page(paginator.num_pages)

    for album in albums.object_list:
        album.images = album.image_set.all()[:4]
    microscopeName=microscopeName

    return render_to_response("gallery/microscopeContents.html", dict(albums=albums, user=request.user,
        media_url=MEDIA_URL,directories=contents,files=contents,prefix=prefix,backone=backone,
        microscopeName=microscopeName,currentdirectory=currentDirectory,pastdirectory=pastDirectory))

def create_task(request):
    f = open('/project/projectdirs/ncemhub/workfile.txt','w')
    f.write('Hello World!\n')
    f.write('This is a test\n')
    f.write('More tests\n')
    return HttpResponseRedirect('/gallery')