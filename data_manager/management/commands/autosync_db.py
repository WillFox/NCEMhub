from django.core.management.base import BaseCommand, CommandError
import os
import time

DATA_PATH = '../../../data'
FileSep = ','
start_time=time.time()
sleepy_time=60
"""
UTILITIES
"""

def first_lib_data_run():
    f=open('data_struct.txt','w')
    f.write('{ENDLINE}')
    f.close()
    return 0


"""
SUMMARY: Goes over entire directory where data is transferred and 
makes copy to be compared to last synced view
"""
def walkPath():
    lib_data_copy = open('data_struct_copy.txt', 'w')
    for (dirpath, dirnames, filenames) in os.walk(DATA_PATH):
        for dirp in dirpath:
            lib_data_copy.write(dirp)
        lib_data_copy.write('\n')
        #print dirpath
        lib_data_copy.write('[')
        for filename in filenames:
            lib_data_copy.write(filename)
            lib_data_copy.write(FileSep)
        lib_data_copy.write(']')
        lib_data_copy.write('\n')
        #print filenames
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
    return True

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
        lib_data = open('data_struct.txt','r')
    except:
        first_lib_data_run()
        lib_data = open('data_struct.txt','r')
    lib_data_copy = open('data_struct_copy.txt', 'r')
    lib_new_data = open('data_struct_changes.txt','w')
    working = True
    dirNEW = lib_data_copy.readline()
    fileNEW = lib_data_copy.readline()
    dirOLD = lib_data.readline()
    fileOLD = lib_data.readline()
    if dirOLD == '':
        lib_data.close()
        first_lib_data_run()
        lib_data = open('data_struct.txt','r')
        dirOLD=lib_data.readline()
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
                    add_data_set(newF,dirNEW)
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
                    add_data_set(newF,dirNEW)
                    lib_new_data.write(dirNEW)
                    lib_new_data.write('\n')
                    lib_new_data.write(newF)
                    lib_new_data.write('\n')
            newFiles=True
            print 'CHANGE'

        if dirNEW==dirOLD:
            """
            Increments when directory exists in old and new structures
            """
            dirNEW = lib_data_copy.readline()
            fileNEW = lib_data_copy.readline()
            dirOLD = lib_data.readline()
            fileOLD = lib_data.readline()
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
                fileOLD = lib_data.readline()
            else:    
                """
                Increments when directory only exists in new structure
                """
                dirNEW = lib_data_copy.readline()
                fileNEW = lib_data_copy.readline()
        if dirNEW == '{ENDLINE}':
            if dirOLD == '{ENDLINE}':
                working = False
    lib_data.close()
    lib_data_copy.close()
    lib_new_data.close()
    return True
"""
SUMMARY: creates a log before over-writing the new file system mirror
as the new original system mirror, in oreder to be used for future 
updates.

"""
def LOG_copy_NEW_to_OLD():
    logFileName= 'dataTransferLog/LOG-' + str(time.time()) + ".txt"

    lib_data_log = open(logFileName, 'w')
    lib_data = open('data_struct.txt','r')
    line = ''
    while line != '{ENDLINE}':
        line = lib_data.readline()
        lib_data_log.write(line)
    lib_data.close()
    lib_data_log.close()
    lib_data = open('data_struct.txt','w')
    lib_data_copy = open('data_struct_copy.txt', 'r')
    line = ''
    while line != '{ENDLINE}':
        line = lib_data_copy.readline()
        lib_data.write(line)

    return True

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'
    filename = "hello.txt"
    fRead = open(filename,'w')
    fRead.write("this worked")
    n=0
    while True:
        walkPath()
        correlatePath()
        LOG_copy_NEW_to_OLD()
        time.sleep(sleepy_time)
        print("test ",n)
        n=n+1
    def handle(self, *args, **options):
        n=1
