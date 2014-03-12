%DM3 reader for matlab that reads all of the tags and data objects.
%All data types (except packed complex) are read properly
%Output is a struct containing each object (image, spectra, SI, or data cube)
%The tags are saved in a text file with the original image name.
%
%Based on DM3_reader.java for ImageJ
%
%Version 3 Stable

%History:
%Written by Peter Ercius 2008/09/05
% - Properly retrieves the sizes, scale, and origin of SI images
% - Retrieves all data objects (i.e. multiple spectra in one DM3 file)
%
% Modified by Huolin Xin 2008/11/19 to enable auto recognization of datatype
%  - energy axis (if any) is passed out
%  - multiple lines in dm can be read
%  - corrected the global variable problem (matlab is evil in global!!!)
%  - no matter what ur file's datatype is
%  (int,uint,ushort,float,double...). The image or SI can be extracted
%  properly
%  - added pick file user interface is no filename is passed in
%  - rgb, complex8 and complex16 data are handled properly now
%  - packed complex8 is not handled yet
%
%Modified P Ercius 2008/11/20
%	- Uses struct and cell
%	- Struct output for spectra and SI have energy axis struct.en()
%	- Distinguishes image, spectra, SI, and other 3D data cubes

%%
%Main Function
function scienceData = dm3_reader3(inName)

    if nargin == 0
        inName = getfile('*.dm3');
    end
    
    %Clear globals
	clear global curGroupLevel MAXDEPTH curGroupAtLevelX curGroupNameAtLevelX;
    clear global curTagAtLevelX curTagName FIDout;
    clear global dataSize dataOffset xsize ysize zsize scale origin numObjects dataType;
	global curGroupLevel MAXDEPTH curGroupAtLevelX curGroupNameAtLevelX;
	global curTagAtLevelX curTagName FIDout;
	global dataOffset xsize ysize zsize scale origin numObjects dataType;
    
	xsize = 0;
	ysize = 0;
	zsize = 1;
	numObjects = 0;
	dataType = 0;
	
	curGroupLevel = 0; %track how deep we currently are in a group
	MAXDEPTH = 64; %maximum number of group levels allowed
	curGroupAtLevelX = zeros(1,MAXDEPTH,'int16'); %track group at current level
	%curGroupNameAtLevelX = cell(1,MAXDEPTH); %track group name at cur level
	%curGroupNameAtLevelX = '';
	
	curTagAtLevelX = zeros(1,MAXDEPTH); %track tag number at current level
	curTagName = ''; %name of the current tag data item
	
	[FID FIDmessage] = fopen(inName,'rb');
	FIDout = fopen([inName '_tags.txt'],'wt');
	
	if FID == -1
		error(FIDmessage);
	end
	
	%Check file for version and data format
	if validDM3(FID) ~= 1
		disp('This does not seem to be a DM3 file...quitting')
		return;
	end
	
	%DM3 files have an unnamed root group which contains everything in
	%the file
	curGroupNameAtLevelX = 'root'; %set the name of the root group
	
	%Read the root tag group (and all of its subgroups)
	readTagGroup(FID);
	
	%Read in the data for each object now that all of the tags and relevant
	%information has been gathered from the tags
	%The first object is not usefule so start the $for$ loop at 2
	fseek(FID,0,-1); %seek to the start of the file
	jj = 0; %counter for the useful number of objects (xsize > 0)

	%Use a struct to hold the data
	scienceData = struct([]);
	for ii = 2:numObjects
		if( (xsize(ii) > 0))
            jj = jj+1; %counter for useful objects (xsize > 0)
            fseek(FID,dataOffset(ii),-1); %seek to the start of the data
            stype = getprecisionstr(dataType(ii)); %retrieve correct data type
			if strcmp(stype,'rgb')
                temp = readData(FID,[xsize(ii)*4 ysize(ii) zsize(ii)],'uint8');
                imr = temp( 1:4:(xsize(ii)-1)*4+1,:,:); %red channels
                img = temp( (1:4:(xsize(ii)-1)*4+1)+1,:,:); %green channels
                imb = temp( (1:4:(xsize(ii)-1)*4+1)+2,:,:); %blue channels
                scienceData(jj).image = cat(3,imr,img,imb); %combine the channels into RGB image
            elseif strcmp(stype,'complex8')
                temp = readData(FID,[xsize(ii)*2 ysize(ii) zsize(ii)],'float32');
                imr = temp(1:2:(xsize(ii)-1)*2+1,:,:); %real part
                imi = temp((1:2:(xsize(ii)-1)*2+1)+1,:,:); %imaginary part
                scienceData(jj).image = imr+imi*sqrt(-1); %create complex array
            elseif strcmp(stype,'complex16')
                temp = readData(FID,[xsize(ii)*2 ysize(ii) zsize(ii)],'double');
                imr = temp(1:2:(xsize(ii)-1)*2+1,:,:);
                imi = temp((1:2:(xsize(ii)-1)*2+1)+1,:,:);
                scienceData(jj).image = imr+imi*sqrt(-1);
			else
				if ysize(ii) == 0 || ysize(ii)==1 %data is a spectra
					scienceData(jj).sig = fread(FID,[xsize(ii) 1],stype);
					scienceData(jj).en = (-origin(jj)*scale(jj) + (0:(xsize(ii)-1))*scale(jj))';
					elseif zsize == 1 %data is an image
					scienceData(jj).image = readData(FID,[xsize(ii) ysize(ii) zsize(ii)],stype);
				elseif zsize(ii)>1 && ~isempty(origin) %data is a 3D spectrum image
                    scienceData(jj).SI = readData(FID,[xsize(ii) ysize(ii) zsize(ii)],stype);
					scienceData(jj).en = (-origin(jj)*scale(jj) + (0:(zsize(ii)-1))*scale(jj))';
				else %data is a 3D array
					scienceData(jj).cube = readData(FID,[xsize(ii) ysize(ii) zsize(ii)],stype);
				end
			end
		end
	end
    
	fclose(FID);
	fclose(FIDout);

	clear global curGroupLevel MAXDEPTH curGroupAtLevelX curGroupNameAtLevelX;
    clear global curTagAtLevelX curTagName FIDout;
    clear global dataSize dataOffset xsize ysize zsize scale origin numObjects dataType;
end

function str = getprecisionstr(datatype)
	switch datatype
	    case 6
	        str = 'uint8';
	    case 10
	        str = 'uint16';
	    case 11
	        str = 'uint32';
	    case 9
	        str = 'int8';
	    case 1
	        str = 'int16';
	    case 7
	        str = 'int32';
	    case 2
	        str = 'float32';
	    case 12
	        str = 'double';
	    case 14
	        str = 'bit1';
	    case 23
	        str = 'rgb';
	    case 3
	        str = 'complex8';
	    case 13
	        str = 'complex16';
	    case 5
	        str = 'packedcomplex8';
	end
end

%Determine if the file is a valid DM3 file and written in
%little endian (PC) format
function output = validDM3(FID)

	output = 1; %output will stay == 1 if the file is a true DM3 file

	%The first 4 4byte integers equal the file size
	%It is written in Big-endian format.
	head = fread(FID,3,'uint32','ieee-be'); 
	%FileSize = head(2);
	
	%Gatan file version. This must == 3 to continue
	if head(1) ~= 3
		disp('File does not seem to be version DM3')
		output = 0;
	end
	
	%Test for binary endian type. PC data is written as little endian.
	if head(3) ~= 1
		disp('Data not written in little endian (PC) format.');
		output = 0;
	end
	
end

% Read in a three dimensional binary data array from a file
% Based on read3d.m
%	fid: File ID of the file to be read. Opened with ex. fopen(fname,'rb')
%	count: [m,n,p] matrix denoting the size of the matrix
%	precision: type of numbers to read from the binary data (string)
function out = readData(fid,count,precision)
	
	out = zeros(count(1),count(2),count(3));

	for ii = 1:count(3)
		temp = fread(fid, count(1:2), precision);
		if size(temp) ~= size(out(:,:,ii))
			disp('size error')
		end
		out(:,:,ii) = temp;
	end
end

%%
%Tag functions
function readTagGroup(FID)
	global curGroupLevel curGroupAtLevelX curTagAtLevelX curGroupNameAtLevelX;

	curGroupLevel = curGroupLevel + 1; %go down a level; this is a new group
	curGroupAtLevelX(curGroupLevel) = curGroupAtLevelX(curGroupLevel) + 1;
	%Set the # of current tags at this level to -1 since the readTagEntry
	%routine pre-increments. ie the first tag will be labeled 0
	curTagAtLevelX(curGroupLevel) = 0;
	
	fread(FID,1,'uchar'); %isSorted
	fread(FID,1,'uchar'); %isOpen
	nTags = fread(FID,1,'uint32','ieee-be');
	
	%Iterate over the number of tag entries in this group
	oldTotalTag = curGroupNameAtLevelX;
	for ii = 1:nTags
		readTagEntry(FID);		
	end
	
	%Go back up a level now that we are finished reading this group
	curGroupLevel=1;
	curGroupNameAtLevelX = oldTotalTag;
end

function readTagEntry(FID)
	global curGroupLevel curTagAtLevelX curTagName curGroupNameAtLevelX;
	
	isData = fread(FID,1,'uchar','ieee-be'); %use big endian
	
	%Record that we have found a tag at this level
	curTagAtLevelX(curGroupLevel) = curTagAtLevelX(curGroupLevel)+1;
	
	%Get the tag if one exists
	lenTagLabel=fread(FID,1,'uint16','ieee-be');
	if lenTagLabel ~= 0
		tagLabel = fscanf(FID,'%c',lenTagLabel); %read in the string
	else
		tagLabel = num2str(curTagAtLevelX(curGroupLevel)); %unlabeled tag
	end
	
%disp(['readTagEntry, isData:' num2str(isData) ',tagLabel:' tagLabel])
	
oldGroupName = curGroupNameAtLevelX;

	if isData == 21
		%This tag entry is data
		
		%Name the piece of data
		%curTagName = [makeGroupString '.' tagLabel];
		%curGroupNameAtLevelX = [curGroupNameAtLevelX '.' tagLabel];
		curTagName = tagLabel;
		
		%Now get the tag data
		readTagType(FID);
	else
		%This tag entry is another tag group
		%Awkward that this cant be done in readTagGroup() but:
		
		%Store the name of the group at the new level
		%curGroupNameAtLevelX(curGroupLevel+1) = {tagLabel};
		curGroupNameAtLevelX = [curGroupNameAtLevelX '.' tagLabel];
		readTagGroup(FID);
	end	
	curGroupNameAtLevelX = oldGroupName;
end

function readTagType(FID)
	Delim = fscanf(FID,'%c',4); %should always be '%%%%'

	if ~strcmp(Delim,'%%%%')
		disp('Tag type delimiter is not "%%%%"')
	end
	fread(FID,1,'uint32','ieee-be'); %nInTag: unnecessary redundant info
	
	readAnyData(FID);
	
end

%%
%Higher level function which dispatches to functions handling specific data
%types
function readAnyData(FID)
	global curTagName;

	%This specifies what kind of type we are dealing with: short, long, struct, array, etc.
	%global encodedType; %by Huolin Xin
    encodedType = fread(FID,1,'uint32','ieee-be');
	
	%Find size of encoded type
	etSize = encodedTypeSize(encodedType);
	
%disp(['readAnyData, etSize:' num2str(etSize) ' ,Type:' num2str(encodedType)] )

	if etSize > 0
		%must be a regular data type, so read it and store a tag for it
		storeTag(curTagName, readNativeData(FID,encodedType));
	elseif encodedType == 18 %it is a String
		stringSize = fread(FID,1,'uint32','ieee-be');
		out = readStringData(FID,stringSize);
		storeTag(curTagName,out)
	elseif encodedType == 15 %it is a STRUCT
		%Stores fields in curly braces but does not store field names. In
		%fact the code will break for non-zero field names
		structTypes = readStructTypes(FID);
		out = readStructData(FID,structTypes);
		storeTag(curTagName,out);
	elseif encodedType == 20 %it is an ARRAY
		%Not read. Only stores a tag which it defined to indicate the size of the
		%data chunks that are skipped
		arrayTypes = readArrayTypes(FID);
		readArrayData(FID,arrayTypes);
		storeTag(curTagName,' Array data unknown');
	end
end

%Match the encodedtype to the Gatan type and get its size.
%Returns the size in bytes of the data type
function width = encodedTypeSize(encodedType)
	%Setup constants for the different encoded *data* types used in DM3 files
	%Structs, arrays, Strings, etc are handled elsewhere
% 	VAL_SHORT   = 2;
% 	VAL_LONG    = 3;
% 	VAL_USHORT  = 4;
% 	VAL_ULONG   = 5;
% 	VAL_FLOAT   = 6;
% 	VAL_DOUBLE  = 7;
% 	VAL_BOOLEAN = 8;
% 	VAL_CHAR    = 9;
% 	VAL_OCTET   = 10;

	%-1 will signal an unlisted type
	%width = -1;
	
	switch encodedType
		case {0} %just in case...
			width = 0;
		case {8, 9, 10}		%{VAL_BOOLEAN, VAL_CHAR, VAL_OCTET}
			width = 1; %data is 1 byte each
		case {2, 4}			%{VAL_SHORT, VAL_USHORT}
			width = 2;
		case {3, 5, 6}		%{VAL_LONG, VAL_ULONG, VAL_FLOAT}
			width = 4;
		case {7} %{VAL_DOUBLE}
			width = 8;
		otherwise
			%disp('Type Unknown')
			width=-1;
	end
end

function rString = readStringData(FID, stringSize)
	
	%reads string data
 	if ( stringSize <= 0 )
		rString = '';
	else	
		
		rString = readString(FID, stringSize);
		% !!! *Unicode* string... convert to latin-1 string
		%Not sure is this is necessary???
		%rString = unicode(rString, 'utf_16_le').encode('latin1', 'replace');
	end
end

%Function to read ordinary data types
function val = readNativeData(FID,encodedType)

	%reads ordinary data types
	VAL_SHORT   = 2;
	VAL_LONG    = 3;
	VAL_USHORT  = 4;
	VAL_ULONG   = 5;
	VAL_FLOAT   = 6;
	VAL_DOUBLE  = 7;
	VAL_BOOLEAN = 8;
	VAL_CHAR    = 9;
	VAL_OCTET   = 10;
	
	%These need to be read as little endian!
	if ( encodedType == VAL_SHORT )
		val = fread(FID,1,'short');
	elseif ( encodedType == VAL_LONG )
		val = fread(FID,1,'int32');
	elseif ( encodedType == VAL_USHORT )
		val = fread(FID,1,'uint16');
	elseif ( encodedType == VAL_ULONG )
		val = fread(FID,1,'uint32');
	elseif ( encodedType == VAL_FLOAT )
		val = fread(FID,1,'float');
	elseif ( encodedType == VAL_DOUBLE )
		val = fread(FID,1,'double');
	elseif ( encodedType == VAL_BOOLEAN )
		val = fread(FID,1,'uchar');
	elseif ( encodedType == VAL_CHAR )
		val = fscanf(FID,'%c',1);
	elseif ( encodedType == VAL_OCTET)
		val = fscanf(FID,'%c',1);   % difference with char???
	else
		error(['Unknown data type ' num2str(encodedType)])
	end

end

%%
%STRUCT and ARRAY Functions

%Analyzes the data types in a struct
function fieldTypes = readStructTypes(FID)

	fread(FID,1,'uint32','ieee-be'); %structNameLength
	nFields = fread(FID,1,'uint32','ieee-be');

	if ( nFields > 100 )
		error('Too many fields');
	end
		
	fieldTypes = zeros(1,nFields);
	for i=1:nFields
		fread(FID,1,'uint32','ieee-be'); %nameLength
		fieldType = fread(FID,1,'uint32','ieee-be');
		fieldTypes(i) = fieldType;
	end

end

%Reads struct data based on type info in structType
function struct = readStructData(FID,structTypes)

	struct = zeros(1,length(structTypes));

	for i=1:length(structTypes)
		encodedType = structTypes(i);
		etSize = encodedTypeSize(encodedType);

		%disp(['Tag Type = ' num2str(encodedType) ', Tag Size = ' num2str(etSize)])

		%get data
		struct(i) = readNativeData(FID, encodedType);
	end
end

%Determines the data types in an array data type
function itemTypes = readArrayTypes(FID)
	
	arrayType = fread(FID,1,'uint32','ieee-be');
	
	itemTypes=[];
	
	if ( arrayType == 15 ) %STRUCT
		itemTypes = readStructTypes(FID);
	elseif ( arrayType == 20 ) %ARRAYS
		itemTypes = readArrayTypes(FID);
	else
		s = length(itemTypes);
		itemTypes(s+1) = arrayType;
	end

end

%Reads array data
function aa=readArrayData(FID,arrayTypes)
	
	global curTagName scale origin scale_temp origin_temp numObjects;

	arraySize = fread(FID,1,'uint32','ieee-be');

	itemSize = 0;
	encodedType = 0;
	
	for i=1:length(arrayTypes)
		encodedType = arrayTypes(i);
		etSize = encodedTypeSize(encodedType);
		itemSize = itemSize + etSize;
	end

	bufSize = arraySize * itemSize;
	loc = ftell(FID);
	
	if ( ~isempty(strfind(curTagName,'ImageData.Data'))) && ( length(arrayTypes) == 1 ) && ( encodedType == 4 ) && ( arraySize < 256 )
		% treat as string
		readStringData( FID, bufSize ); %val
	else
		%treat as binary data
		% - store data size and offset as tags
		storeTag([ curTagName '.Size'], bufSize);
		storeTag([ curTagName '.Offset'], loc);
		
		if(strfind(curTagName,'Units') & (bufSize > 0))
			unitsName = fscanf(FID,'%c',bufSize);
			%Change the zeros in the character string to spaces
			unitsName = unitsName + 32*(unitsName == 0);
			if (strfind(unitsName,'e V'))
				storeTag([curTagName 'Name'], 'eV');
				scale(numObjects) = scale_temp;
				origin(numObjects) = origin_temp;
			end
		else
			% - skip data w/o reading
			fseek(FID, bufSize, 0);
		end
		
	end
	
	aa = 1; %return 1
end

%%
%Function to write out the tags to a TXT file and find interesting tags
%(Data size, offset, etc.)

function storeTag(curTagName,curTagValue)
	global FIDout dataSize dataOffset curGroupNameAtLevelX numObjects;
	global xsize ysize zsize dataType scale_temp origin_temp;
	
	if ischar(curTagValue)
		totalTag = [curGroupNameAtLevelX '.' curTagName '=' curTagValue];
	else
		totalTag = [curGroupNameAtLevelX '.' curTagName ' = ' num2str(curTagValue)];
	end

	if strfind(curTagName,'Data.Size')
		numObjects = numObjects + 1; %add 1 to the number of objects
		dataSize(numObjects) = curTagValue;
	elseif strfind(curTagName,'Data.Offset')
		dataOffset(numObjects) = curTagValue;
	elseif strfind(curTagName,'DataType')
		dataType(numObjects) = curTagValue;
	elseif strfind(totalTag,'Dimensions.1')
		xsize(numObjects) = curTagValue;
        ysize(numObjects) = 1;
		zsize(numObjects) = 1;
	elseif strfind(totalTag,'Dimensions.2')
		ysize(numObjects) = curTagValue;
	elseif strfind(totalTag,'Dimensions.3')
		zsize(numObjects) = curTagValue;
	elseif (strfind(totalTag,'Dimension.') & strfind(totalTag,'.Scale'))
		scale_temp = curTagValue;
	elseif (strfind(totalTag,'Dimension.') & strfind(totalTag,'.Origin'))
		origin_temp = curTagValue;
	end
	
	fwrite(FIDout,totalTag);
	fprintf(FIDout,'\n');

end

function [filename name dirname] = getfile(varargin)
%[filename name dirname] = getfile(varargin)
%by Huolin Xin

if isempty(varargin)
    str_type = '*.*';
elseif ~ischar(varargin{1})
    str_type = '*.*';
else
    str_type = varargin{1};
end

fp = fopen(fullfile(matlabroot,'dir.txt'),'r');
if fp~=-1
    dedir = fgetl(fp);
    fclose(fp);
    dedir = strrep(dedir,'\','\\');
    [name dirname] = uigetfile([dedir,'\\',str_type]);
else
    [name dirname] = uigetfile(str_type);
end

filename = fullfile(dirname,name);
fp = fopen(fullfile(matlabroot,'dir.txt'),'w');
fprintf(fp,'%s',dirname);
fclose(fp);
end


