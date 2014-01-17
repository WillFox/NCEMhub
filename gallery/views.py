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

def microscopeListView(request,microscopeName):

    ###This allows for the directory path to be navigated in stead of starting over.  There is probably a better way to do this.  
    def step_back_directory(path):
        n=0
        x=0
        while(n<3):
            if(path[-3:]== FileDelimeter):
                n=3
                path=path[:-3]
            else:
                path=path[:-1]
            x=x+1
            if(x>200):
                n=3
        return path
    #find last directory and passes the string containing its name so that the new 'current directory' can be set
    def last_current_directory(path):
        n=3
        x=0
        sample='abc'
        while(n<3):
            sample=path[-3-x:0-x]
            if(sample==FileDelimeter):
                path=path[:-x]
                n=3
            x=x+1
            if(x>200):
                n=3
        f = open('/project/projectdirs/ncemhub/workfile2.txt','w')
        f.write('Hello World!\n')
        f.write('This is a test\n')
        f.write('More tests\n')
        return path
    

    def path_unpacker(path):
        t=1
        directory_depth= [0,]
        curLength=len(path)
        n=0
        x=0
        sample='abc'
        while(n<3):
            sample=path[-3-x:0-x]
            if(sample==FileDelimeter):
                directory_depth.append(path[:-x])
                path=path[-x-3:]
                directory_depth[0]=directory_depth[0]+1
                x=0
            if(x>200):
                directory_depth.append(path)
                directory_depth[0]=directory_depth[0]+1
                n=3
            n=345
            x=x+1
        return directory_depth


    
    """File Structure Interpreter"""
    #Sets default values for variables obtained through .GET
    NoFile='None'   #Sets what a null response should be (AKA what a file and directory cannot be named)
    try:
        prefixBefore=request.GET['prefix']
    except: prefixBefore=NoFile
    try:
        currentDirectory=request.GET['currentdirectory']
    except: currentDirectory=NoFile
    try:
        currentFileName=request.GET['file']
    except: currentFileName = NoFile
     





    #except: path='Void'
    #fileStructure = path_unpacker(path)
    fileStructure='open'

    #Currently in Home Directory
    if prefixBefore == NoFile:
        #Selected a File while in the home directory
        if currentDirectory == NoFile:
            prefix = currentFileName
        #selected a directory while in the home directory
        else:
            prefix = currentDirectory
    #Currently within a directory outside of home directory
    else: 
        #chose a file in the directory that is not the home directory
        if currentDirectory == NoFile:
            prefix = prefixBefore + FileDelimeter + currentFileName
        #chose a directory that is not in the home directory
        else:
            prefix = prefixBefore + FileDelimeter + currentDirectory
    #attempt to asign a path for the previous directory path
    #may cause trouble if in home directory or only one directory down
    try:
        backone=step_back_directory(prefix)
    except: backone = NoFile
    #attempt to asign the last directory that was accessed (AKA go up one directory level)
    #may be problematic without being several layers down
    try:
        pastDirectory=last_current_directory(prefixBefore)
    except: pastDirectory='MICROSCOPE_HOME'
    ################################################################
    path = prefix
    text_length=len(path)
    
    depth=1
    v=0
    sample='abc'
    #depth holds how many levels down exist
    if(prefix==NoFile):
        depth=0
    while(v<text_length-3):
        sample=prefix[-3-v:0-v]
        if(sample==FileDelimeter):
            depth=depth+1
        v=v+1







    #Develops the file contents
    contents = ['None']
    if request.user.is_authenticated():
        user = User.objects.get(username=request.user)
        data_locator = '../../../data' + '/' + user.username[0] + '/' + user.username + '/' + microscopeName
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
        microscopeName=microscopeName,currentdirectory=currentDirectory,pastdirectory=pastDirectory,filestructure=fileStructure,depth=depth))

def create_task(request):
    f = open('/project/projectdirs/ncemhub/workfile.txt','w')
    f.write('Hello World!\n')
    f.write('This is a test\n')
    f.write('More tests\n')
    return HttpResponseRedirect('/gallery')