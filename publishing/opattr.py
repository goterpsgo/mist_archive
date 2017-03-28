
import socket
import base64
import os
import datetime

#from xml.etree import ElementTree as ET
from lxml import etree as ET

#database stuff
import sys
sys.path.insert(0, '/opt/mist/database')
import config
from sqlalchemy import *

#Extra Modules
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/modules")
from tzlocal import get_localzone



class OpAttributes:

    def __init__(self, file_chunk_size):

        # Set max size of xml
        self.max_size = file_chunk_size
        self.doc_count = 1
        
        #Static Name Defs
        wsnt = "http://docs.oasis-open.org/wsn/b-2"
        xsi = "http://www.w3.org/2001/XMLSchema-instance"
        tagged_value = "http://metadata.dod.mil/mdr/ns/netops/shared_data/tagged_value/0.41"
        wsa = "http://www.w3.org/2005/08/addressing"
        ar="http://metadata.dod.mil/mdr/ns/netops/shared_data/assessment_report/0.41"
        organization="http://metadata.dod.mil/mdr/ns/netops/shared_data/organization/0.41"
        person="http://metadata.dod.mil/mdr/ns/netops/shared_data/person/0.41"
        geoloc="http://metadata.dod.mil/mdr/ns/netops/shared_data/geolocation/0.41"
        opsattr="http://metadata.dod.mil/mdr/ns/netops/shared_data/ops_attributes/0.41"
        cndc="http://metadata.dod.mil/mdr/ns/netops/net_defense/cnd-core/0.41"
        device = "http://metadata.dod.mil/mdr/ns/netops/shared_data/device/0.41"

        #Converting to right namespace
        self.nsWSNT = "{%s}" % wsnt
        self.nsWSA = "{%s}" % wsa
        self.nsTaggedValue = "{%s}" % tagged_value
        self.nsAR = "{%s}" % ar
        self.nsOPTATTR = "{%s}" % opsattr
        self.nsCNDC = "{%s}" % cndc
        self.nsDevice = "{%s}" % device

        #initial namespace map
        self.nsMap = {"wsnt" : wsnt, "xsi" : xsi, "tagged_value" : tagged_value, "wsa" : wsa, "ar":ar, "organization":organization, 
                  "person":person, "geoloc":geoloc, "opsattr":opsattr, "cndc":cndc, "device":device}

        #create the database stuff that we need
        connect_string = 'mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST'
        ssl_args = {'ssl':{'cert':'/opt/mist/database/certificates/mist-interface.crt', 'key':'/opt/mist/database/certificates/mist-interface.key', 'ca':'/opt/mist/database/certificates/si_ca.crt'}}
        self.db = create_engine(connect_string, connect_args=ssl_args, echo=False)
        #db.echo = True
        self.metadata = MetaData(self.db)


    def buildStatic(self):
        #set the root
        self.root = ET.Element(self.nsWSNT + "Notify", nsmap=self.nsMap)
        #Sub Elements
        #main element
        self.notificationMessage = ET.SubElement(self.root, self.nsWSNT + "NotificationMessage")
        #Topic Always static
        ET.SubElement(self.notificationMessage, self.nsWSNT + "Topic", Dialect="docs.oasis-open.org/wsn/t-1/TopicExpression/Simple").text = "acas.opsattrs.complete"

    def buildProducerReference(self, refNumber):
        producerReference = ET.SubElement(self.notificationMessage, self.nsWSNT + "ProducerReference")
        ET.SubElement(producerReference, self.nsWSA + "Address").text = socket.gethostname()
        metadata = ET.SubElement(producerReference, self.nsWSA + "Metadata")
        ET.SubElement(metadata, self.nsWSA + "MessageID").text = socket.gethostname() + ":acas.opsattrs:local:" + str(refNumber)
        ET.SubElement(metadata, self.nsTaggedValue + "taggedString", name="MIST", value="0.1") 

    def getDefinition(self, tag):
        results = self.db.execute('SELECT name FROM tagDefinition WHERE category = "' + tag[2] + '" and rollup = "' + tag[1] + '"')
        exists = False
        definition = None
        for result in results:
            if result:
                definition = result[0]
                exists = True
        return exists, definition

    def getTagList(self, assetID):
        tags = self.db.execute("SELECT tagID, rollup, category, timestamp, status from taggedAssets WHERE assetID = " + str(assetID))
        tagList = []
        for tag in tags:
            tagList.append([tag[0], tag[1], tag[2], tag[3], tag[4]])
        return tagList

    def get_required_tags(self):
        #Pull the require tags
        req_tag_list = self.db.execute("SELECT category, rollup, defaultValue FROM tagDefinition WHERE required = 'Y'")
        required_tags = []
        for tag_required in req_tag_list:
            required_tags.append(tag_required)
        return required_tags

    def insert_required_tags(self, missing_tags, tagList):
        timestamp = datetime.datetime.now()
        for tag in missing_tags:
            tagList.append([tag[2], tag[1], tag[0], timestamp, 'True'])
        return tagList

    def add_missing_required(self, tagList, required_tags):
        #['27', 'http://owner.dod.mil', 'organization', datetime.datetime(2015, 12, 17, 17, 14, 7), 'False']
        missing_tags = []
        for required_tag in required_tags:
            tag_exists = False
            #check each valid tag to see if it contains the required tags
            for tag in tagList:
                if tag[4] == 'True':
                    cat = tag[2]
                    rollup = tag[1]
                    if cat == required_tag[0] and rollup == required_tag[1]:
                        tag_exists = True
            if not tag_exists:
                #mark tag to be added
                missing_tags.append(required_tag)

        #add the missing tags to the tagList
        if missing_tags:
            tagList = self.insert_required_tags(missing_tags, tagList)
        
        return tagList

    def get_xml_size(self):
        xmlstr = ET.tostring(self.root, encoding='utf-8', method='xml', pretty_print=True)
        if sys.getsizeof(xmlstr) > self.max_size:
            return True
        return False

    def buildReport(self, assetIDList, tempDirectory, refNumber, assessmentReport):
        #assessmentReport = ET.SubElement(self.message, self.nsAR + "AssessmentReport")
        required_tags = self.get_required_tags()
        for assetID in assetIDList:
            tagList = self.getTagList(assetID)
            #Get Missing required tags
            tagList = self.add_missing_required(tagList, required_tags)
            #build openining report opbject tags
            reportObject = ET.SubElement(assessmentReport, self.nsAR + "reportObject")
            device = ET.SubElement(reportObject, self.nsAR + "device")
            #get hostname of MIST machine
            hostname = socket.gethostname()
            #build ID reference
            deviceID = ET.SubElement(device, self.nsDevice + "device_ID")
            ET.SubElement(deviceID, self.nsCNDC + "resource").text = hostname
            ET.SubElement(deviceID, self.nsCNDC + "record_identifier").text = str(assetID)
            #set attribute ID count
            for tag in tagList:
                defExists, definition = self.getDefinition(tag)
                if defExists:
                    nameID, timestamp, tagStatus = tag[0], tag[3], tag[4]
                    tz = get_localzone()
                    tagTime = tz.localize(timestamp).strftime("%Y-%m-%dT%H:%M:%S%z")
                    tag_date = tagTime[:-2] + ":" + tagTime[-2:]
                    #build XML for the tag
                    if tagStatus == "True":
                        ET.SubElement(device, self.nsTaggedValue + "taggedString", name=definition, value=nameID, timestamp=tag_date)
                    else:
                        ET.SubElement(device, self.nsTaggedValue + "taggedString", name=definition, value=nameID, timestamp=tag_date, status=tagStatus.lower())
            print_file = self.get_xml_size()
            if print_file:
                self.write_file(tempDirectory, refNumber)
                assessmentReport = self.build_xml_header(refNumber)
                
    def build_xml_header(self, refNumber):
        #build the static portion
        self.buildStatic()

        #build the producer reference
        self.buildProducerReference(refNumber)

        #Message Tag
        self.message = ET.SubElement(self.notificationMessage, self.nsWSNT + "Message")

        assessmentReport = ET.SubElement(self.message, self.nsAR + "AssessmentReport")

        return assessmentReport

    def write_file(self, tempDirectory, refNumber):
        # Build the XML Tree
        tree = ET.ElementTree(self.root)
        tree.write(tempDirectory + "/" + str(refNumber) + ".opattrs_" + str(self.doc_count) + ".xml", xml_declaration=True,
                   encoding='utf-8', method='xml', pretty_print=True)
        self.doc_count += 1

    def buildXML(self, assetIDList, refNumber, tempDirectory):

        assessmentReport = self.build_xml_header(refNumber)

        #build the report
        self.buildReport(assetIDList, tempDirectory, refNumber, assessmentReport)

        self.write_file(tempDirectory, refNumber)


