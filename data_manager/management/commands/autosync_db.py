from django.core.management.base import BaseCommand, CommandError
import os
import time
from ncemhub.settings import MEDIA_URL, DATA_ROOT, MEDIA_ROOT, DATA_PATH
from data_manager.models import DataCharacteristic, Tag, DataRecorder, Repository, Collection, DataSet, Value
from user_authentication.models import Patron
from django.contrib.auth.models import User
from django.db.models import Q
import Utility_Dev.dm3reader_v072
import Utility_Dev.dm3lib_v099
import numpy
import Image

FileSep = ','
start_time=time.time()
#sleepy_time=60
if os.name=='nt':
    MEDIA_ROOT = '\\project\\projectdirs\\ncemhub\\ncemhub\\bin\\ncemhub\\www\\media\\'
    THUMBNAIL_ROOT = MEDIA_ROOT+'thumbnails\\'
    FULL_IMAGE_ROOT = MEDIA_ROOT+'full_image\\'
    directory_sep='\\'
else:
    MEDIA_ROOT = '/project/projectdirs/ncemhub/ncemhub/bin/ncemhub/www/media/'
    THUMBNAIL_ROOT = MEDIA_ROOT+'thumbnails/'
    FULL_IMAGE_ROOT = MEDIA_ROOT+'full_image/'
    directory_sep = '/'
END_FILE='{ENDLINE}'
data_structure='data_manager/data_struct.txt'
data_structure_copy='data_manager/data_struct_copy.txt'
data_structure_additions='data_manager/data_struct_changes.txt'
LOG_FILES='dataTransferLog/'
"""
UTILITIES
"""
def create_image_from_list():

    return True

def extract_user_and_instrument(newF,dirNEW):
    user_start=0
    user_end=None
    instr_start = 0
    instr_end=None
    i=0
    find_instrument=False
    """
    the following is a complicated mess that defines who the user is
    and what the instrument/data_recorder is which is
    derived from the directory where the file was 
    deposited.
    """
    start_looking=False
    for i in range(len(dirNEW)):
        if dirNEW[i]=='d':
            start_looking=True
        if start_looking==True:
            if dirNEW[i]=="\\":
                if user_end == None:
                    if user_start==0:
                        user_start=i+1
                    else:
                        user_end=i
                        find_instrument = True
                if find_instrument==True:
                    if instr_start == 0:
                        instr_start=i+1
                    else:
                        if instr_end == None:
                            instr_end=i
            if dirNEW[i]=="/":
                if user_end == None:
                    if user_start==0:
                        user_start=i+1
                    else:
                        user_end=i
                        find_instrument = True
                if find_instrument==True:
                    if instr_start == 0:
                        instr_start=i+1
                    else:
                        if instr_end == None:
                            instr_end=i


    data_user = dirNEW[user_start:user_end]
    data_name = newF[:-4]
    data_instrument = dirNEW[instr_start:instr_end]
    if instr_end == None:
        data_instrument = dirNEW[instr_start:]
    file_data={"data_user":data_user,"data_instrument":data_instrument,"data_name":data_name}    
    return file_data

def create_characteristics_dm3(data,tag_list):
    tag_units=''
    tags_added=0
    for tag, tag_value in tag_list.iteritems():
        tag = unicode(tag,errors='ignore')
        tag_value = unicode(tag_value, errors='ignore')
        for i in range(len(tag)):
            if tag[i] == '.':
                tag_name = tag[i+1:]
        test_unique = DataCharacteristic.objects.filter(name_detail=tag).distinct()
        copy_now=False
        tag_units=''
        for i in range(len(tag_name)):
            if tag_name[i]==')':
                copy_now=False
            if copy_now==True:
                tag_units=tag_units+tag_name[i]
            if tag_name[i]=='(':
                copy_now=True
        if len(test_unique)>0:
            data_char = test_unique[0]
        else:
            data_char = DataCharacteristic.objects.create(name=tag_name, name_detail=tag)
        tag_is_float=False
        try:
            float(tag_value)
            tag_is_float=True
        except:
            tag_is_float=False
        if tag_is_float == False:
            tag_text = tag_value
            value_char = Value(characteristic = data_char, data_set= data, text_value= tag_text )
        else:
            tag_text = tag_units
            tag_value = float(tag_value)
            value_char = Value(characteristic = data_char, data_set= data, text_value= tag_text, float_value=tag_value )
        value_char.save()
        tags_added=tags_added+1
    print "Total tags added to ", data, ": ", tags_added
    #value1 = Value(characteristic = characteristic1, data_set = data1,
    #   text_value = "Confocal")
    #value1.save()
    return 0

def add_dm3_to_db(newF,dirNEW):
    print 'adding '+newF+' ::: '+ dirNEW
    noError=True
    #Find User
    dict_ui=extract_user_and_instrument(newF,dirNEW)
    data_user=dict_ui['data_user']
    data_instrument=dict_ui['data_instrument']
    data_name=dict_ui['data_name']
    error=''
    error_detail=''
    """
    SUMMARY:  Error detection
    Error marking for in case the file drop location does not match
    the information found within the database
    ---add to a log file, not a print statement!
    """
    dir_path=dirNEW+directory_sep+newF
    try:
        error_detail="Owner non existent"
        owner = User.objects.filter(username=data_user).distinct()
        error_detail="Instrument/Data Recorder non existent"
        data_recorder = DataRecorder.objects.filter(slug=data_instrument).distinct()
        error_detail = "Data set unable to be created"
        data = DataSet.objects.create(name=data_name,public=False,data_original_path=dirNEW,
            data_path=dir_path,image_rep_path='/',description=' ')
        data.owners.add(owner[0])
        data.data_recorder.add(data_recorder[0])
    except:
        print data_user
        print data_instrument
        error = "File Location is not coherrent with database:"
        print error
        print error_detail
    """
    SUMMARY: Create Tags/ Assign Data Characteristics/ Create image and asign path
    """

    filename=dirNEW+directory_sep+newF
    tag_list=Utility_Dev.dm3reader_v072.parseDM3( filename, dump=False )
    
    if tag_list==0:
        print "Tags not recovered"
    else:
        print "Writing tags to data sets..."
        create_characteristics_dm3(data,tag_list)
    #create thumbnail for DM3    
    tn_file=THUMBNAIL_ROOT+ str(data.id) +'.jpg'
    Utility_Dev.dm3reader_v072.thumbnail_dm3(filename,tn_file)
    data.image_rep_path = tn_file
    data.save()
    """
    Adds the actual image
    ***(should be incorporated within a separate function later)
    """
    data=Utility_Dev.dm3lib_v099.DM3(filename) 
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
    for i in range(im_height):
        for ii in range(im_width):
            scaled=float(all_data[i*im_width+ii])
            std_i = (scaled-average)/standard_deviation
            color = (std_i+3.0)*(255.0/6.0)
            if color > 255:
                color = 255
            if color < 0:
                color = 0
            all_data[i*im_width+ii]=int(color)
    im2=Image.new(im.mode, im.size)
    im2.putdata(all_data)
    #list_of_pixels = list(im.getdata())
    # Do something to the pixels...
    #im2 = Image.new(im.mode, im.size)
    #im2.putdata(list_of_pixels)

    #import Utility_Dev.dm3lib_v099 as d
    #data = d.DM3(filename)
    #im = data.getImage
    #all_data=list(im.getdata())

    #data1 = DataSet.objects.create(name=newF[:-4],public=False,data_original_path=dirNEW,data_path=dirNEW,image_rep_path=MEDIA_URL+"data/2.jpg",
    #    description="None")   
    #data1.owners.add(user1)
    #data1.tags.add(tag)
    #data1.data_recorder.add(recorder1)
    #data1.collections.add(collection3) 
    return True

"""
SUMMARY: Creates data repository that is not data specific
"""
def add_undefined_file(newF,dirNEW):
    print 'adding '+newF+' ::: '+ dirNEW
    print 'adding '+newF+' ::: '+ dirNEW
    noError=True
    #Find User
    dict_ui=extract_user_and_instrument(newF,dirNEW)
    data_user=dict_ui['data_user']
    data_instrument=dict_ui['data_instrument']
    data_name=dict_ui['data_name']
    error=''
    error_detail=''
    """
    SUMMARY:  Error detection
    Error marking for in case the file drop location does not match
    the information found within the database
    ---add to a log file, not a print statement!
    """
    dir_path=dirNEW+directory_sep+newF
    try:
        error_detail="Owner non existent"
        owner = User.objects.filter(username=data_user).distinct()
        error_detail="Instrument/Data Recorder non existent"
        data_recorder = DataRecorder.objects.filter(slug=data_instrument).distinct()
        error_detail = "Data set unable to be created"
        data = DataSet.objects.create(name=data_name,public=False,data_original_path=dirNEW,
            data_path=dir_path,image_rep_path='/',description=' ')
        data.owners.add(owner[0])
        data.data_recorder.add(data_recorder[0])
    except:
        print data_user
        print data_instrument
        error = "File Location is not coherrent with database:"
        print error
        print error_detail
    return 0
def first_lib_data_run():
    f=open(data_structure,'w')
    f.write(END_FILE)
    f.close()
    return 0


"""
SUMMARY: Goes over entire directory where data is transferred and 
makes copy to be compared to last synced view
"""
def walkPath():
    data_struct_copy = open(data_struct_copy, 'w')
    for (dirpath, dirnames, filenames) in os.walk(DATA_PATH):
        data_struct_copy.write(dirpath)
        data_struct_copy.write('\n')
        for filename in filenames:
            data_struct_copy.write(filename)
            data_struct_copy.write('\n')
    data_struct_copy.write(END_FILE)
    data_struct_copy.close()
    return True

"""
SUMMARY: A function that runs each time a new data set/ data file is added 
to the repository.  This may include any of the following:
--Analysis of specific data types
--Production of thumbnails
--Addition to database
--Pull of tags and adding to database
--Automatic ser association with folder
--Automatic microscope/instrument association to transfer folder
"""
#Currently gives no file input
#Each action should be a separate function found in the UTILITIES above
#       representing all file types and potential analysis options
def add_data_set(newF,dirNEW):
    file_added=False
    if newF[-4:]=='.dm3':
        print "This is a DM3"
        add_dm3_to_db(newF,dirNEW)
        file_added=True
    if newF[-4:]=='.DM3':
        print "This is a DM3"
        add_dm3_to_db(newF,dirNEW)
        file_added=True
    if file_added==False:
        add_undefined_file(newF,dirNEW)
        print "This file type is not recognized, but has been added to the database"
        file_added=True
    return file_added

"""
SUMMARY: Takes the copy of the file system from one folder and compares
it with the old file system build and adds each of the files that have 
been added:

---not sure where the meta data will be kept at the moment
---if a directory exists in the old directory copy that does not exist 
in the new directory, then a never ending loop will occur
"""
def correlatePath():
    try: 
        data_struct = open(data_structure,'r')
    except:
        first_lib_data_run()
        data_struct = open(data_structure,'r')
    data_struct_copy = open(data_struct_copy, 'r')
    lib_new_data = open(data_struct_changes,'w')
    working = True
    dirNEW = data_struct_copy.readline()
    dirNEW = dirNEW.rstrip('\n')
    dirOLD = data_struct.readline()
    dirOLD = dirOLD.rstrip('\n')
    while working:
        fileOLD_list=[]
        fileNEW_list=[]
        fileOLD=''
        fileNEW=''
        #The following creates a list of files 
        #in the directories old and new
        adding_files=True
        while adding_files:
            fileNEW = data_struct_copy.readline()
            fileNEW = fileNEW.rstrip('\n')
            if fileNEW[:len(DATA_ROOT)]==DATA_ROOT:
                adding_files=False
            else:
                if fileNEW==END_FILE:
                    adding_files=False
                else:
                    fileNEW_list.append(fileNEW)
        adding_files=True
        while adding_files:
            fileOLD = data_struct.readline()
            fileOLD = fileOLD.rstrip('\n')
            if fileOLD[:len(DATA_ROOT)]==DATA_ROOT:
                adding_files=False
            else:
                if fileOLD==END_FILE:
                    adding_files=False
                else:
                    fileOLD_list.append(fileNEW)
        if dirNEW == dirOLD:






                    add_data_set(newF,dirNEW)####
                    lib_new_data.write(dirNEW)
                    lib_new_data.write('\n')
                    lib_new_data.write(newF)
                    lib_new_data.write('\n')

        if dirNEW == END_FILE:
            if dirOLD == END_FILE:
                working = False
    data_struct.close()
    data_struct_copy.close()
    lib_new_data.close()
    return True
"""
SUMMARY: creates a log before over-writing the new file system mirror
as the new original system mirror, in order to be used for error tracking.

"""
def LOG_copy_NEW_to_OLD():
    logFileName= LOG_FILES+'LOG-' + str(time.time()) + ".txt"

    lib_data_log = open(logFileName, 'w')
    data_struct = open(data_structure,'r')
    line = ''
    while line != END_FILE:
        line = data_struct.readline()
        data_struct_log.write(line)
    data_struct.close()
    lib_data_log.close()
    data_struct = open(data_structure,'w')
    data_struct_copy = open(data_structure_copy, 'r')
    line = ''
    while line != END_FILE:
        line = data_struct_copy.readline()
        data_struct.write(line)

    return True
"""
SUMMARY: The class that is initiated by the following Command
* * * * * * 
python manage.py autosync_db
* * * * * * 
This command will run through the entire database looking for 
new files.  Once a new file is found it will perform an 
operation based on the file extension or other to be 
determined factors.
"""
class Command(BaseCommand):
    filename = "data_manager/sync_instruction.txt"
    fRead = open(filename,'w')
    fRead.write("sync")
    fRead.close()
    n=0
    sync=True
    while sync:
        walkPath()
        correlatePath()
        LOG_copy_NEW_to_OLD()
        t=time.localtime()
        """
        calculates time until midnight in which data will be synced (local time)
        """
        sleepy_time=(24*60*60)-(t[3]*60*60+t[4]*60+t[5])
        print "Sleepy_time=",sleepy_time
        time.sleep(sleepy_time)
        print "sync cycle: ",n
        #The following looks for a change in a text
        #file in order to determine if it should keep 
        #running
        f= open(filename,'r')
        instruction_line=f.readline()
        f.close()
        if not instruction_line == 'sync':
            sync=False
        n=n+1
    def handle(self, *args, **options):
        n=1
