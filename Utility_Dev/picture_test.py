import Image
import numpy
import dm3reader_v072
import os, struct
#Image.open(file, mode) 
#pixel = value * scale + offset
#im.putdata(data, scale, offset)

#im.save(outfile, format, options...)
#im.thumbnail(size, filter)
#im.getdata() 

#########################################


def thumbnail_dm3(dm3_file,tn_file):
	#dm3_file='T.dm3' 
	makeJPEG=True
	#tn_file='dm3tn_temp.'

	'''Extracts useful experiment info from DM3 file and 
	exports thumbnail to a PGM file if 'makeJPEG' set to 'True'.'''
		
	# define useful information
	info_keys = {
		'descrip': 'root.ImageList.1.Description',
		'acq_date': 'root.ImageList.1.ImageTags.DataBar.Acquisition Date',
		'acq_time': 'root.ImageList.1.ImageTags.DataBar.Acquisition Time',
		'name': 'root.ImageList.1.ImageTags.Microscope Info.Name',
		'micro': 'root.ImageList.1.ImageTags.Microscope Info.Microscope',
		'hv': 'root.ImageList.1.ImageTags.Microscope Info.Voltage',
		'mag': 'root.ImageList.1.ImageTags.Microscope Info.Indicated Magnification',
		'mode': 'root.ImageList.1.ImageTags.Microscope Info.Operation Mode',
		'operator': 'root.ImageList.1.ImageTags.Microscope Info.Operator',
		'specimen': 'root.ImageList.1.ImageTags.Microscope Info.Specimen',
	#	'image_notes': 'root.DocumentObjectList.10.Text' # = Image Notes 		
		}
			
	# parse DM3 file
	tags = dm3reader_v072.parseDM3( dm3_file, dump=False )

	# if OK, extract Tags [and thumbnail]
	if tags:
		if makeJPEG:
			# get thumbnail
			tn_size = int( tags[ 'root.ImageList.0.ImageData.Data.Size' ] )
			tn_offset = int( tags[ 'root.ImageList.0.ImageData.Data.Offset' ] )
			tn_width = int( tags[ 'root.ImageList.0.ImageData.Dimensions.0' ] )
			tn_height = int( tags[ 'root.ImageList.0.ImageData.Dimensions.1' ] )
			
			if ( (tn_width*tn_height*4) != tn_size ):
				print "Error: cannot extract thumbnail from", dm3_file
				sys.exit()
				
			# access DM3 file
			try:
				dm3 = open( dm3_file, 'rb' )
			except:
				print "Error accessing DM3 file"
				sys.exit()
			
			# read tn image data
			dm3.seek( tn_offset )
			pgmlist=[]
			for i in range( tn_height ):
				startlist=True
				for ii in range( tn_width ):
					data_bytes = dm3.read(4)
					pgm_data = struct.unpack('<L', data_bytes)[0]
					pgm_data = int( pgm_data )
					if startlist==True:
						pgmlist.append([pgm_data])
						startlist=False
					else:
						pgmlist[i].append(pgm_data)

			#statistical extraction from data
			#allows for good grayscale
			sum_data=0.0
			N=0.0
			#find sum
			for i in range(tn_height):
				for ii in range(tn_width):
					scaled=float(pgmlist[i][ii])
					sum_data=scaled+sum_data
					N=1+N
			average=sum_data/N
			#find variance and standard deviation
			sum_squared=0.0
			for i in range(tn_height):
				for ii in range(tn_width):
					scaled=float(pgmlist[i][ii])-average
					scaled=scaled*scaled
					sum_squared=sum_squared+scaled
			variance = sum_squared/N
			standard_deviation = numpy.sqrt([variance])
			standard_deviation=standard_deviation[0]
			#find color for each pixel based on standard deviation
			for i in range(tn_height):
				for ii in range(tn_width):
					scaled=float(pgmlist[i][ii])
					std_i = (scaled-average)/standard_deviation
					color = (std_i+3.0)*(255.0/6.0)
					if color > 255:
						color = 255
					if color < 0:
						color = 0
					pgmlist[i][ii]=int(color)
			#create thumbnail
			im=Image.new("RGB",(tn_width,tn_height))#black and white option is L
			im.putpixel((50,50),(255,0,0))
			for i in range(tn_height):
				for ii in range(tn_width):
					scaled=int(pgmlist[i][ii])
					im.putpixel((i,ii),(scaled,scaled,scaled))
			#im.putdata(pgmlist_all,scale=1.0,offset=0)
			im.save(tn_file)
			pgm_file.close()
			dm3.close()
		return True
	# else, return false value
	else:
		return False
dm3_file='T.dm3'
tn_file
thumbnail_dm3(dm3_file,tn_file)

def page_lists(datas,page):
	pages = datas
	#show 3 options before and 3 options after
	page_options=[]
	pages_passed=[]
	girth_pages=3
	for i in range(pages):
		page_options.append(i+1-page)
	for i in range(len(page_options)):
		if abs(page_options[i])<girth_pages+1:
			pages_passed.append(i+1)
	for i in range(1):
		this_thing=1

	if pages_passed[0]==1:
		pages_passed.insert(0,1)
	if pages_passed[-1]==pages:
		pages_passed.append(pages)
	pages_short=girth_pages*2+1-len(pages_passed)
	if pages<girth_pages*2+1:
		pages_short=0
		while pages_short>0:#Less than expected pages
			if pages_passed[0]==1:
				pages_passed.append(pages_passed[-1]+1)
			if pages_passed[-1]==pages:
				pages_passed.insert(0,pages_passed[0]-1)
				pages_short=girth_pages*2+1-len(pages_passed)

	print page, pages_passed
	#make sure enough arguments are passed
	return page_options

#page_lists(5,1)
#page_lists(5,2)
#page_lists(5,3)
#page_lists(5,4)
#page_lists(5,5)
#print "=============="
#page_lists(8,1)
#page_lists(8,2)
#page_lists(8,3)
#page_lists(8,4)
#page_lists(8,5)
#page_lists(8,6)
#page_lists(8,7)
#page_lists(8,8)
#print "=============="
#page_lists(4,1)
#page_lists(4,2)
#page_lists(4,3)
#page_lists(4,4)
