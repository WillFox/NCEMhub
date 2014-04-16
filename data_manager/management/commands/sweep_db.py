from django.core.management.base import BaseCommand, CommandError
import os
import time
from ncemhub.settings import MEDIA_URL, DATA_ROOT, MEDIA_ROOT
from data_manager.models import DataCharacteristic, Tag, DataRecorder, Repository, Collection, DataSet, Value
from user_authentication.models import Patron
from django.contrib.auth.models import User
from django.db.models import Q
import Utility_Dev.dm3reader_v072
import Utility_Dev.dm3lib_v099
import numpy
import Image
#This list will contain all extensions to be analyzed in the database
EXTENTION_TARGETS=[
    '.dm3',
    '.DM3']

if os.name=='nt':
    DATA_PATH = '..\\..\\..\\data'
    MEDIA_ROOT = '\\project\\projectdirs\\ncemhub\\ncemhub\\bin\\ncemhub\\www\\media\\'
    THUMBNAIL_ROOT = MEDIA_ROOT+'thumbnails\\'
    FULL_IMAGE_ROOT = MEDIA_ROOT+'full_image\\'
    directory_sep='\\'
else:
    DATA_PATH = '../../../data'
    MEDIA_ROOT = '/project/projectdirs/ncemhub/ncemhub/bin/ncemhub/www/media/'
    THUMBNAIL_ROOT = MEDIA_ROOT+'thumbnails/'
    FULL_IMAGE_ROOT = MEDIA_ROOT+'full_image/'
    directory_sep = '/'
"""
UTILITIES
"""
#test operation
"""
SUMMARY: Prints the name of the file currently being analyzed 
before all other functions are analyzed 
"""
def testOperation(dirpath,filename):
    test=True
    print str(dirpath+directory_sep+filename)
    return test

def file_filter(filename):
    correct_file=False
    base_file, file_extention = os.path.splitext(filename)
    for extension_target in EXTENTION_TARGETS:
        if file_extention == extension_target:
            correct_file=True
    return correct_file

def create_large_image(dirpath,filename):
    """
    Adds the actual image
    ***(should be incorporated within a separate function later)
    """
    data=Utility_Dev.dm3lib_v099.DM3(dirpath+directory_sep+filename) 
    im= data.getImage()
    all_data=list(im.getdata())
    im_size=im.size
    im_height=im_size[0]
    im_width=im_size[1]
    sum_data=0.0
    N=0.0
    #find sum
    for i in range(im_height):
        for ii in range(im_width):
            scaled=float(all_data[i*im_width+ii])
            sum_data=scaled+sum_data
            N=1+N
    average=sum_data/N
    #find variance and standard deviation
    sum_squared=0.0
    for i in range(im_height):
        for ii in range(im_width):
            scaled=float(all_data[i*im_width+ii])-average
            scaled=scaled*scaled
            sum_squared=sum_squared+scaled
    variance = sum_squared/N
    standard_deviation = numpy.sqrt([variance])
    standard_deviation=standard_deviation[0]
    #find color for each pixel based on standard deviation
    im2=Image.new('RGB', im.size)
    for i in range(im_height):
        for ii in range(im_width):
            scaled=float(all_data[i*im_width+ii])
            std_i = (scaled-average)/standard_deviation
            color = (std_i+3.0)*(255.0/6.0)
            if color > 255:
                color = 255
            if color < 0:
                color = 0
            color=int(color)
            im2.putpixel((i,ii),(color,color,color))

    data=DataSet.objects.filter(data_path=dirpath+directory_sep+filename)[0]
    full_file=FULL_IMAGE_ROOT+ str(data.id) +'.jpg'
    im2.save(full_file)
    return True

def create_thumbnails_from_dataset(dirpath,filename):
    """
    Adds the actual image
    ***(should be incorporated within a separate function later)
    """
    data=Utility_Dev.dm3lib_v099.DM3(dirpath+directory_sep+filename) 
    im= data.getImage()
    all_data=list(im.getdata())
    im_size=im.size
    im_height=im_size[0]
    im_width=im_size[1]
    sum_data=0.0
    N=0.0
    #find sum
    for i in range(im_height):
        for ii in range(im_width):
            scaled=float(all_data[i*im_width+ii])
            sum_data=scaled+sum_data
            N=1+N
    average=sum_data/N
    #find variance and standard deviation
    sum_squared=0.0
    for i in range(im_height):
        for ii in range(im_width):
            scaled=float(all_data[i*im_width+ii])-average
            scaled=scaled*scaled
            sum_squared=sum_squared+scaled
    variance = sum_squared/N
    standard_deviation = numpy.sqrt([variance])
    standard_deviation=standard_deviation[0]
    #find color for each pixel based on standard deviation
    im2=Image.new('RGB', im.size)
    for i in range(im_height):
        for ii in range(im_width):
            scaled=float(all_data[i*im_width+ii])
            std_i = (scaled-average)/standard_deviation
            color = (std_i+3.0)*(255.0/6.0)
            if color > 255:
                color = 255
            if color < 0:
                color = 0
            color=int(color)
            im2.putpixel((i,ii),(color,color,color))

    data=DataSet.objects.filter(data_path=dirpath+directory_sep+filename)[0]
    full_file=THUMBNAIL_ROOT+ str(data.id) +'.jpg'
    size=128,128
    im2.thumbnail(size,Image.ANTIALIAS)
    im2.save(full_file)
    return True
"""
SUMMARY: Each function within operationList() is a function that
is performed on each and every file that walkPath hits
"""
def operationList(dirpath,filename):
    #perform the following on the passed file
    """
    Test operation prints the name of each file analyzed.  
    Useful in finding which file breaks your code
    -uncomment it for low level tracking of bugs
    """
    #testOperation(dirpath,filename)
    if file_filter(filename):
        perform=True
        #perform operation if of the expected file type
        create_large_image(dirpath,filename)
        create_thumbnails_from_dataset(dirpath,filename)

    return True
"""
SUMMARY: Goes over entire directory where data is transferred and 
makes copy to be compared to last synced view
"""
def walkPath():
    for (dirpath, dirnames, filenames) in os.walk(DATA_PATH):
        for filename in filenames:
            operationList(dirpath,filename)
    return True

"""
SUMMARY: The class that is initiated by the following Command
* * * * * * 
python manage.py sweep_db
* * * * * * 
This command will run through the entire database.
It will perform an operation based the functions 
specified here.
"""
class Command(BaseCommand):
    #walkPath() hits every file and performs operationList() on each file
    walkPath()
    def handle(self, *args, **options):
        n=1
