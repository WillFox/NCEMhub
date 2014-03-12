import os
import time
import h5py

DATA_PATH = '../../../data'
FileSep = ','
start_time=time.time()



"""
SUMMARY: Goes over entire directory where data is transferred and 
makes copy to be compared to last synced view
"""
def walkPath():
	lib_data_copy = open('data_struct_copy.txt', 'w')
	for (dirpath, dirnames,filenames) in os.walk(DATA_PATH):
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

def separateFiles(mergedFiles):
	n=1
	separated_files=[]
	for i in range(len(mergedFiles)):
		if mergedFiles[i]==FileSep:
			separated_files.append(mergedFiles[n:i])
			n=i+1
		return separated_files

def differenceFinder(separate_NEW, separate_OLD):
	return separate_NEW

def add_data_set(newF,dirNEW):
	return newF
"""
SUMMARY: Takes the copy of the file system from one folder and compares
it with the old file system build and adds each of the files that have 
been added:

---not sure where the meta data will be kept at the moment
---if a directory exists in the old directory copy that does not exist 
in the new directory, then a never ending loop will occur
"""
def correlatePath():
	lib_data = open('data_struct.txt','r')
	lib_data_copy = open('data_struct_copy.txt', 'r')
	lib_new_data = open('data_struct_changes.txt','w')
	working = True
	dirNEW = lib_data_copy.readline()
	fileNEW = lib_data_copy.readline()
	dirOLD = lib_data.readline()
	fileOLD = lib_data.readline()

	while working:
		if fileNEW != fileOLD :
			"""
			Add new data sets
			"""
			if(dirOLD==dirNEW):
				"""
				Add the difference of fileOLD and fileNEW
				"""
				separate_OLD = separateFiles(fileOLD)
				separate_NEW = separateFiles(fileNEW)
				newToAdd = differenceFinder(separate_NEW,separate_OLD)
				for newF in newToAdd:
					add_data_set(newF,dirNEW)
					lib_new_data.write(dirNEW)
					lib_new_data.write(newF)
			else:
				"""
				Add all file from fileNEW
				"""
				separate_NEW = separateFiles(fileNEW)
				for newF in newToAdd:
					add_data_set(newF)
					lib_new_data.write(dirNEW)
					lib_new_data.write(newF)
			newFiles=True
			print 'CHANGE'

		if dirNEW==dirOLD:
			dirNEW = lib_data_copy.readline()
			fileNEW = lib_data_copy.readline()
			dirOLD = lib_data.readline()
			fileOLD = lib_data.readline()
		else:
			dirNEW = lib_data_copy.readline()
			fileNEW = lib_data_copy.readline()
		if dirNEW == '{ENDLINE}':
			if dirOLD == '{ENDLINE}':
				working = False
	lib_data.close()
	lib_data_copy.close()
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

"""
while True:
	walkPath()
	correlatePath()
	LOG_copy_NEW_to_OLD()
	time.sleep(600)
"""

print walkPath()
print correlatePath()
print time.time() - start_time, " seconds"
print LOG_copy_NEW_to_OLD()