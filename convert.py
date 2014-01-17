#DM3 reader 
#VERSION:1.0.0
#By William Fox
#Creation Date: 12/1/13 12:15:00
#
#Last Edited 12/8/13 19:44:00
#By: William Fox
#


#import file
filename = "T.dm3"
file_location = ""

def DM3FileImport(filename,file_location):
	#INPUT File
	fRead = open(filename,'r')
	#Give option to write tags here if you are going to
	inNAme= filename
	writeTags = 0
	xsize = 0
	ysize = 0
	zsize = 1
	numObjects = 0
	dataType = 0
	curGroupLevel = 0 #track how deep we currently are in a group
	MAXDEPTH = 64 # maximum number of group levels allowed
####!	
	curGroupAtLevelX = zeros(1,MAXDEPTH, 'int16') #track group at current level
	curTagAtLevelX = zeros(1,MAXDEPTH);
	cureTagName = '' #name of the current tag data item
	#OUTPUT Files
	fData = open('data','w')
	if(writeTags):
		fTags = open('tags','w')
	#Think about adding an error if the file reading fails

	#Check file for file version and format
	if (validDM3(fRead) == 1):
		print("This does not appear to be a valid DM3 file--- QUITTING!")
		return
	#DM3 files have an unnamed root group which contains evertrhing in the file
	curGroupNameAtLevelX = '' #set the name of hte root group

	#read the root tag group (and all of its subgroups)
	readTagGroup(fRead)

	#read in the data for each object now that all of the tags and relevant
	#information has been gathered from the tags
	#The first object is not useful so start the for loop at 2
	fseek(fRead, 0,-1) #seek to the start of the file
	jj = 0 #coutner for the useful number of objects (xsize > 0)

	#use a struct to hold the data
	scienceData = struct('scale',{})
	for ii= 2 in numObjects:
		if(xsize(ii) > 0 ):
			jj = jj+1 #coutner for useful objects (xsize >0)
			fseek(fRead, dataOffset(ii), -1) #seek to the start of hte data


extractedFile = DM3FileImport(filenamem file_location)



