bool MainWindow::loadDm3(const QString &fileName)
{
    qDebug() << "Attempting .dm3 load: " << fileName;

    QFile file(fileName);
    if(!file.open(QIODevice::ReadOnly))
    {
        qWarning() << "Failed to open dm3 file " << fileName;
        return false;
    }

    QDataStream in(&file);

    // Check that the file is valid dm3 by reading in the first 3 header bytes.
    qint32 h1, h2, h3;
    in >> h1 >> h2 >> h3;
    // First byte should be file version number (3)
    if(3 != h1)
    {
        qWarning() << "Not a valid dm3 file";
        file.close();
        return false;
    }
    // File data should be big-endian
    if(1 != h3)
    {
        qWarning() << "Not a valid dm3 file";
        file.close();
        return false;
    }

    // The next two bytes are flags for "sorted" and "open"
    qint8 fSorted, fOpen;
    in >> fSorted >> fOpen;

    // The next 4 bytes give the number of tags in the root directory
    qint32 tagCount;
    in >> tagCount;

    // Create a child node of the model root to hold the dm3 tags
    EmdNode *dm3Root = emdModel->addNode("dm3", EmdNode::GROUP);
    // TODO: shouldn't have to specify dirty here maybe?
    //dm3Root->setStatus(EmdNode::DIRTY);
    std::stack<EmdNode*> nodeStack;
    nodeStack.push(dm3Root);
    std::stack<int> tagsRemainingStack;

    bool endOfFile = false;
    bool readError = false;
    qint8 sectionType;
    quint16 tagNameLength;
    QString nameString;
    int unnamedTagCount = 1;
    std::stack<int> utcStack;
    QVariant attrValue;
    Emd::DataType emdType;
    QList<Emd::DataType> dataTypeList;
    QList<char*> dataList;
    QList<QVariant> attrList;
    char *tagName = NULL;
    int tagsRemaining = tagCount;
    // Iterate over all of the tags/tag directories
    while( !endOfFile && !readError )
    {
        // First byte is section type (tag, directory, eof)
        in >> sectionType;
        // Second byte is tag name length (can be zero)
        in >> tagNameLength;
        // Following bytes are tag name
        // If we have a tag name length, just read in the name
        if(tagNameLength > 0)
        {
            if(tagName)
                delete[] tagName;
            tagName = new char[tagNameLength + 1];
            tagName[tagNameLength] = 0;
            in.readRawData(tagName, tagNameLength);
            nameString = QString(tagName);
        }
        else
        {
            nameString = "" + QString::number(unnamedTagCount++);
        }

        if(20 == sectionType)    // tag directory
        {
            //qDebug() << "Reading directory: " << tagName;
            utcStack.push(unnamedTagCount);
            unnamedTagCount = 1;

            // The next two bytes are sorted/open flags
            in >> fSorted >> fOpen;

            // The next uint32 is the number of tags in the directory
            in >> tagCount;
            //qDebug() << "Directory has " << tagCount << " tags";
            tagsRemainingStack.push(tagsRemaining);
            tagsRemaining = tagCount;

            // Create a node for the new directory
            EmdNode *group = emdModel->addNode(nameString, EmdNode::GROUP, nodeStack.top());
            nodeStack.push(group);
        }
        else if(21 == sectionType)    // tag
        {
            //qDebug() << "Reading tag: " << tagName;
            --tagsRemaining;

            // Add a node for the tag
            EmdAttribute *attribute = static_cast<EmdAttribute*>
                (emdModel->addNode(nameString, EmdNode::ATTRIBUTE, nodeStack.top()));

            // We first expect a delimiter string '%%%%'
            char delimiter[5];
            delimiter[4] = 0;
            in.readRawData(delimiter, 4);
            if(strcmp(delimiter, "%%%%") != 0)
            {
                qWarning() << "Invalid file: missing delimiter";
                readError = true;
                continue;
            }

            // The next 4-byte integer holds the size of the info array
            qint32 infoLength;
            in >> infoLength;
            // The following 4*(infoLength) bytes hold the info array itself
            qint32 *info = new qint32[infoLength];
            for(int iii = 0; iii < infoLength; ++iii)
                in >> info[iii];

            // If the info array has size 1, it's just a single data value
            if(infoLength == 1)
            {
                // The info array contains the data type
                emdType = dm3ToEmdType(info[0]);
                if(emdType != Emd::UNKNOWN)
                {
                    attrValue = readEmdType(in, emdType);
                    attribute->setValue(attrValue);
                    attribute->setType(emdType);
                }
                else
                {
                    qWarning() << "Non-simple single value";
                    delete[] info;
                    return false;
                }
            }
            else
            {
                // The first entry of the info array describes the tag data type
                int depth, index;
                switch(info[0])
                {
                case 0x0f:        // struct
                    nameString = "";
                    attrList.clear();
                    // info[2] contains the number of members
                    for(int iii = 1; iii <= info[2]; ++iii)
                    {
                        // The following alternating entries contain the member types
                        //    (other values are empty)
                        emdType = dm3ToEmdType(info[2 + 2*iii]);
                        if(emdType != Emd::UNKNOWN)
                        {
                            if(iii > 1)
                                nameString += " ";
                            attrValue = readEmdType(in, emdType);
                            attrList.append(attrValue);
                            nameString += attrValue.toString();
                        }
                        else
                        {
                            qWarning() << "Non-simple group value";
                            delete[] info;
                            return false;
                        }    
                    }
                    // Right now we're just storing the string representation of the array.
                    //    We can use the Emd::STRUCT type later and implement it properly if
                    //    we need to actually access struct values beyond just viewing them.
                    attribute->setValue(QVariant(nameString));
                    attribute->setType(Emd::STRING);
                    break;
                case 0x014:        // array
                    // info[1] contains the array data type
                    emdType = dm3ToEmdType(info[1]);
                    // Simple data type
                    if(emdType != Emd::UNKNOWN)
                    {
                        depth = Emd::emdTypeDepth(emdType);
                        uint byteSize = depth * info[2];
                        if(strcmp(tagName, "Data") == 0)
                        {
                            char *rawData = new char[byteSize];
                            in.readRawData(rawData, byteSize);
                            dataList.append(rawData);
                            dataTypeList.append(emdType);
                        }
                        else
                        {
                            if( (emdType == Emd::USHORT) 
                                && (   strcmp(tagName, "Name") == 0
                                    || strcmp(tagName, "Units") == 0 ) )
                            {
                                // Interpret as a unicode string
                                char *rawData = new char[byteSize];
                                in.readRawData(rawData, byteSize);
                                QString nameVal((QChar*)rawData, info[2]);
                                attrValue = QVariant(nameVal);
                            }
                            else if(info[2] > 4)
                            {
                                in.skipRawData(info[2] * Emd::emdTypeDepth(emdType));
                                attrValue = QVariant(QString::number(info[2]) + " element array");
                            }
                            else
                            {
                                // info[2] contains the array size
                                attrValue = readEmdArray(in, emdType, info[2]);
                            }
                            attribute->setValue(attrValue);
                            attribute->setType(Emd::STRING);
                        }
                    }
                    // Complex type
                    else
                    {
                        switch(info[1])
                        {
                        case 0x0f:    // array of structs
                            
                            // The final value contains the array size
                            //if(strcmp(tagName, "Data") == 0)
                            //{
                            //    int channelCount = info[3];

                            //}
                            //else
                            //{
                                depth = 0;
                                // info[3] contains the number of members
                                for(index = 1; index <= info[3]; ++index)
                                {
                                    depth += dm3TypeDepth(info[3 + 2*index]);
                                }
                                in.skipRawData(depth * info[2 + 2*index]);
                            //}
                            break;
                        }
                    }
                default:        // unrecognized
                    break;
                }
            }

            delete[] info;
        }
        else if(0 == sectionType)    // eof
        {
            qDebug() << "Reached end of file";
            endOfFile = true;
        }
        else
        {
            qWarning() << "Tag type read error: " << sectionType;
            readError = true;
        }
        // Decrement tags remaining. If we're at zero, pop the stacks
        while(tagsRemaining == 0 && tagsRemainingStack.size() > 0)
        {
            // Pop the stacks until we find a directory with some tags remaining.
            //    If we are at the end of the last group, don't pop.
            nodeStack.pop();
            tagsRemaining = tagsRemainingStack.top();
            tagsRemainingStack.pop();
            --tagsRemaining;

            unnamedTagCount = utcStack.top();
            utcStack.pop();
        }
    }
    
    if(tagName)
        delete tagName;

    file.close();

    if(readError)
        return false;
    if(!endOfFile)
    {
        qWarning() << "Ran out of tags to read before end of file";
    }
    if(tagsRemaining > 0)
    {
        qWarning() << "Reached end of file with tags remaining";
    }

    // If we found the data, process it
    if(dataList.size() > 0)
    {
        // Try to find the index of the actual image
        EmdNode *refNode = emdModel->getPath("/dm3/ImageSourceList/1/ImageRef");
        if(refNode)
        {
            int imgIndex = refNode->variantRepresentation().toInt();
            EmdNode *imageDataNode = emdModel->getPath("/dm3/ImageList/" 
                                                + QString::number(imgIndex+1)
                                                + "/ImageData");
            EmdNode *dimNode = imageDataNode->child("Dimensions");
            if(dimNode)
            {
                // Create the data group
                EmdDataGroup *dataGroup = static_cast<EmdDataGroup*>
                    (emdModel->addPath("/data/dm3_file", EmdNode::DATAGROUP));

                // Get the list of dimension sizes
                QList<EmdNode*> dimList = dimNode->children();
                int *dimSizes = new int[dimList.size()];
                int dataLength = 1;
                QString dataString = "";
                for(int iii = 0; iii < dimList.count(); ++iii)
                {
                    dimSizes[iii] = dimList.at(iii)->variantRepresentation().toInt();
                    dataLength *= dimSizes[iii];

                    if(iii > 0)
                        dataString += " x ";
                    dataString += QString::number(dimSizes[iii]);
                }
                int dataDepth = Emd::emdTypeDepth(dataTypeList.at(imgIndex));

                // Init the data
                char *data = new char[dataLength * dataDepth];

                // Store the data
                char *rawData = dataList.at(imgIndex);
                memcpy(data, rawData, dataDepth * dataLength);
                EmdData *dataNode = new EmdData(dimList.count(),
                    dimSizes, dataTypeList.at(imgIndex), data, false);
                dataNode->setName("data");

                dataGroup->setData(dataNode);

                // Create dimensions
                EmdAttribute *unitNode = 0;
                EmdData *dimNode;
                QString nameStem = "dim%1";
                for(int iii = 1; iii <= dimList.count(); ++iii)
                {
                    dimNode = new EmdData(dimSizes[iii-1], Emd::UINT);
                    dimNode->setName(nameStem.arg(iii));
                    dataGroup->addDim(dimNode);
                    dimNode->setParentNode(dataGroup);
                    
                    EmdAttribute *destNode = new EmdAttribute(dimNode);
                    destNode->setName("units");
                    dimNode->addChild(destNode);

                    unitNode = static_cast<EmdAttribute*>
                        (imageDataNode->childAtPath("Calibrations/Dimension/"
                                                            + QString::number(iii)
                                                            + "/Units"));
                    if(unitNode)
                        destNode->setValue(unitNode->value());
                    else
                        destNode->setValue(QVariant("[px]"));

                    destNode = new EmdAttribute(dimNode);
                    destNode->setName("name");
                    destNode->setValue(QVariant(nameStem.arg(iii)));
                    dimNode->addChild(destNode);
                }
                emdModel->setCurrentDataGroup(dataGroup);
            }
        }
    }

    foreach(char *data, dataList)
        delete[] data;

    return true;
}

Emd::DataType MainWindow::dm3ToEmdType(const int &type)
{
    Emd::DataType emdType = Emd::UNKNOWN;
    switch(type)
    {
    case 8:        // bool
        emdType = Emd::BOOL;
        break;
    case 9:        // char
        emdType = Emd::BYTE;
        break;
    case 10:    // octet
        emdType = Emd::BYTE;
        break;
    case 2:        // short
        emdType = Emd::SHORT;
        break;
    case 4:        // ushort
        emdType = Emd::USHORT;
        break;
    case 3:        // long
        emdType = Emd::INT;
        break;
    case 5:        // ulong
        emdType = Emd::UINT;
        break;
    case 6:        // float
        emdType = Emd::FLOAT;
        break;
    case 7:        // double
        emdType = Emd::DOUBLE;
        break;
    default:
        break;
    }
    return emdType;
}

int MainWindow::dm3TypeDepth(const int &type) const
{
    // Returns the size in bytes of the dm3 data type
    int depth = -1;
    switch(type)
    {
    case 8:        // bool
    case 9:        // char
    case 10:    // octet
        depth = 1;
        break;
    case 2:        // short
    case 4:        // ushort
        depth = 2;
        break;
    case 3:        // long
    case 5:        // ulong
    case 6:        // float
        depth = 4;
        break;
    case 7:        // double
        depth = 8;
        break;
    default:
        break;
    }
    return depth;
}
