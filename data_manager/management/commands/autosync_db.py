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


DATA_PATH = '../../../data'
FileSep = ','
start_time=time.time()
sleepy_time=60


"""
UTILITIES
"""
def add_dm3_to_db(newF,dirNEW):
    print 'adding '+newF+' ::: '+ dirNEW
    noError=True
    #Find User
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
    for i in range(len(dirNEW)):
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


    data_user = dirNEW[user_start:user_end]
    data_name = newF[:-4]
    data_instrument = dirNEW[instr_start:instr_end]
    if instr_end == None:
        data_instrument = dirNEW[instr_start:]
    error=''
    error_detail=''
    """
    SUMMARY:  Error detection
    Error marking for in case the file drop location does not match
    the information found within the database
    ---add to a log file, not a print statement!
    """
    dir_path=dirNEW+'\\'+newF
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
        print '\n'
        print error_detail
    """
    SUMMARY: Create Tags/ Assign Data Characteristics/ Create image and asign path
    """
    #filename=dirNEW+'/'+newF
    #Utility_Dev.dm3reader_v072.parseDM3( filename, dump=True )

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
    noError=True
    #Find User
    user_start=0
    user_end=None
    instr_start = 0
    instr_end=None
    i=0
    find_instrument=False
    for i in range(len(dirNEW)):
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

    data_user = dirNEW[user_start:user_end]
    data_name = newF
    data_instrument = dirNEW[instr_start:instr_end]
    error=''
    error_detail=''
    """
    SUMMARY:  Error detection
    Error marking for in case the file drop location does not match
    the information found within the database
    ---add to a log file, not a print statement!
    """
    try:
        error_detail="Owner non existent"
        owner = User.objects.filter(username=data_user).distinct()
        error_detail="Instrument/Data Recorder non existent"
        data_recorder = DataRecorder.objects.filter(name=data_instrument)
        error_detail = "Data set unable to be created"
        data = DataSet.objects.create(name=data_name,public=False,data_original_path=dirNEW,data_path=dirNEW)
        data.owners.add(owner[0])
        data.data_recorder.add(data_recorder[0])
    except:
        error = "File Location not coherrent with database"
        print error
        print '\n'
        print error_detail
    return 0
def first_lib_data_run():
    f=open('data_manager/data_struct.txt','w')
    f.write('{ENDLINE}')
    f.close()
    return 0


"""
SUMMARY: Goes over entire directory where data is transferred and 
makes copy to be compared to last synced view
"""
def walkPath():
    lib_data_copy = open('data_manager/data_struct_copy.txt', 'w')
    for (dirpath, dirnames, filenames) in os.walk(DATA_PATH):
        for dirp in dirpath:
            lib_data_copy.write(dirp)
        lib_data_copy.write('\n')
        lib_data_copy.write('[')
        for filename in filenames:
            lib_data_copy.write(filename)
            lib_data_copy.write(FileSep)
        lib_data_copy.write(']')
        lib_data_copy.write('\n')
    lib_data_copy.write('{ENDLINE}')
    lib_data_copy.close()
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
        lib_data = open('data_manager/data_struct.txt','r')
    except:
        first_lib_data_run()
        lib_data = open('data_manager/data_struct.txt','r')
    lib_data_copy = open('data_manager/data_struct_copy.txt', 'r')
    lib_new_data = open('data_manager/data_struct_changes.txt','w')
    working = True
    dirNEW = lib_data_copy.readline()
    dirNEW = dirNEW.rstrip('\n')
    fileNEW = lib_data_copy.readline()
    fileNEW = fileNEW.rstrip('\n')
    dirOLD = lib_data.readline()
    dirOLD = dirOLD.rstrip('\n')
    fileOLD = lib_data.readline()
    fileOLD = fileOLD.rstrip('\n')
    if dirOLD == '':
        lib_data.close()
        first_lib_data_run()
        lib_data = open('data_manager/data_struct.txt','r')
        dirOLD=lib_data.readline()
        dirOLD = dirOLD.rstrip('\n')
    newToAdd=''
    if dirNEW == '{ENDLINE}':
        if dirOLD == '{ENDLINE}':
            working = False
    while working:
        if fileNEW != fileOLD :
            """
            Add new data sets
            """
            if(dirOLD==dirNEW):
                """
                Add the difference of fileOLD and fileNEW
                """
                separate_OLD=[]
                separate_NEW=[]
                separating=True
                fileOLDtemp=fileOLD[1:-1]
                fileNEWtemp=fileNEW[1:-1]
                n=0
                """
                Create set of arrays that have the files' names indexed
                """
                for i in range(len(fileOLDtemp)):
                    if fileOLDtemp[i]==FileSep:
                        separate_OLD.append(fileOLDtemp[n:i])
                        n=i+1
                n=0
                for i in range(len(fileNEWtemp)):
                    if fileNEWtemp[i]==FileSep:
                        separate_NEW.append(fileNEWtemp[n:i])
                        n=i+1
                """
                Removes files that match from each list
                -(i.e. files that match are already synced with database)
                """
                discard=[]
                skip=False
                for i in range(len(separate_NEW)):
                    for n in range(len(separate_OLD)):
                        if separate_NEW[i] == separate_OLD[n]:
                            #Discard
                            discard.append([i,n])
                for z in range(len(discard)):
                    i=discard[len(discard)-z-1][0]
                    n=discard[len(discard)-z-1][1]
                    del separate_NEW[i]
                    del separate_OLD[n]
                """
                Only worry about new files
                ---old files that are no longer present can be ignored for now
                """
                #separate_NEW is what holds all new files
                for newF in separate_NEW:
                    add_data_set(newF,dirNEW)####
                    lib_new_data.write(dirNEW)
                    lib_new_data.write('\n')
                    lib_new_data.write(newF)
                    lib_new_data.write('\n')

            else:
                """
                Add all file from fileNEW
                """
                separate_OLD=[]
                separate_NEW=[]
                separating=True
                fileOLDtemp=fileOLD[1:-1]
                fileNEWtemp=fileNEW[1:-1]
                n=0
                for i in range(len(fileNEWtemp)):
                    if fileNEWtemp[i]==FileSep:
                        separate_NEW.append(fileNEWtemp[n:i])
                        n=i+1
                for newF in separate_NEW:
                    add_data_set(newF,dirNEW)####
                    lib_new_data.write(dirNEW)
                    lib_new_data.write('\n')
                    lib_new_data.write(newF)
                    lib_new_data.write('\n')
            newFiles=True

        if dirNEW==dirOLD:
            """
            Increments when directory exists in old and new structures
            """
            dirNEW = lib_data_copy.readline()
            dirNEW = dirNEW.rstrip('\n')
            fileNEW = lib_data_copy.readline()
            fileNEW = fileNEW.rstrip('\n')
            dirOLD = lib_data.readline()
            dirOLD = dirOLD.rstrip('\n')
            fileOLD = lib_data.readline()
            fileOLD = fileOLD.rstrip('\n')
        else:
            directoryDELETED=True
            #find out if directory was deleted
            #If directory cannot be matched, then directory was deleted
            for (dirpath, dirnames, filenames) in os.walk(DATA_PATH):
                if dirpath == dirOLD:
                    directoryDELETED=False
            if dirOLD == '{ENDLINE}':
                directoryDELETED=False
            if directoryDELETED:
                """
                Incremeents when directory only exists in old structure
                """
                dirOLD = lib_data.readline()
                dirOLD = dirOLD.rstrip('\n')
                fileOLD = lib_data.readline()
                fileOLD = fileOLD.rstrip('\n')
            else:    
                """
                Increments when directory only exists in new structure
                """
                dirNEW = lib_data_copy.readline()
                dirNEW = dirNEW.rstrip('\n')
                fileNEW = lib_data_copy.readline()
                fileNEW = fileNEW.rstrip('\n')
        if dirNEW == '{ENDLINE}':
            if dirOLD == '{ENDLINE}':
                working = False
    lib_data.close()
    lib_data_copy.close()
    lib_new_data.close()
    return True
"""
SUMMARY: creates a log before over-writing the new file system mirror
as the new original system mirror, in order to be used for error tracking.

"""
def LOG_copy_NEW_to_OLD():
    logFileName= 'dataTransferLog/LOG-' + str(time.time()) + ".txt"

    lib_data_log = open(logFileName, 'w')
    lib_data = open('data_manager/data_struct.txt','r')
    line = ''
    while line != '{ENDLINE}':
        line = lib_data.readline()
        lib_data_log.write(line)
    lib_data.close()
    lib_data_log.close()
    lib_data = open('data_manager/data_struct.txt','w')
    lib_data_copy = open('data_manager/data_struct_copy.txt', 'r')
    line = ''
    while line != '{ENDLINE}':
        line = lib_data_copy.readline()
        lib_data.write(line)

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
