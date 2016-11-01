
import socket
import base64
import datetime
import pytz
import os
import re

#from xml.etree import ElementTree as ET
from lxml import etree as ET

#database stuff
import sys
sys.path.insert(0, '/opt/mist/database')
import config
from sqlalchemy import *

#Security Center stuff
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/modules")
from gather_sc_data import GatherSCData
from tzlocal import get_localzone

class ARF:

    def __init__(self, publishAll, file_chunk_size):

        #Set wether to publish all or to just publish assets since last publish
        self.publishAll = publishAll        

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
        cpe = "http://scap.nist.gov/schema/cpe-record/0.1"        

        #Converting to right namespace
        self.nsWSNT = "{%s}" % wsnt
        self.nsWSA = "{%s}" % wsa
        self.nsTaggedValue = "{%s}" % tagged_value
        self.nsAR = "{%s}" % ar
        self.nsOPTATTR = "{%s}" % opsattr
        self.nsCNDC = "{%s}" % cndc
        self.nsDevice = "{%s}" % device
        self.nsCPE = "{%s}" % cpe

        #initial namespace map
        self.nsMap = {"wsnt" : wsnt, "xsi" : xsi, "tagged_value" : tagged_value, "wsa" : wsa, "ar":ar, "organization":organization, 
                  "person":person, "geoloc":geoloc, "opsattr":opsattr, "cndc":cndc, "device":device, "cpe":cpe}

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
        ET.SubElement(self.notificationMessage, self.nsWSNT + "Topic", Dialect="docs.oasis-open.org/wsn/t-1/TopicExpression/Simple").text = "acas.assetdata"

    def buildProducerReference(self, refNumber):
        producerReference = ET.SubElement(self.notificationMessage, self.nsWSNT + "ProducerReference")
        ET.SubElement(producerReference, self.nsWSA + "Address").text = socket.gethostname()
        metadata = ET.SubElement(producerReference, self.nsWSA + "Metadata")
        ET.SubElement(metadata, self.nsWSA + "MessageID").text = socket.gethostname() + ":acas.assetdata:local:" + str(refNumber)
        ET.SubElement(metadata, self.nsTaggedValue + "taggedString", name="MIST", value="0.1") 

    def getFQDN(self, assetID):
        results = self.db.execute('SELECT dnsName FROM Assets WHERE assetID = ' + str(assetID))
        for result in results:
            if result:
                fqdn = result[0]
                return True, fqdn
            else:
                return False, None

    def getIPMAC(self, assetID):
        results = self.db.execute('SELECT macAddress, ip FROM Assets WHERE assetID = ' + str(assetID))
        for result in results:
            if result:
                mac, ip = result[0], result[1]
                return mac, ip
            else:
                return None, None

    def getOS(self, assetID):
        results = self.db.execute('SELECT osCPE FROM Assets WHERE assetID = ' + str(assetID))
        for result in results:
            if result:
                osCPE = result[0]
                return osCPE
            else:
                return None

    def getSCInfo(self, assetID):
        results = self.db.execute('SELECT ip FROM Assets WHERE assetID = ' + str(assetID))
        for result in results:
            if result:
                ip = result[0]
            else:
                ip = None
        results = self.db.execute('SELECT serverName, repoID FROM Repos WHERE assetID = ' + str(assetID))
        for result in results:
            if result:
                serverName, repoID = result[0], result[1]
            else:
                serverName, repoID = None, None
        return ip, serverName, repoID

    def getScanDate(self, assetID):
        results = self.db.execute("SELECT lastUnauthRun, lastAuthRun FROM Assets WHERE assetID = " + str(assetID))
        for result in results:
            if result:
                unAuthTime, authTime = result[0], result[1]
            else:
                unAuthTime, authTime = None, None
        if authTime:
            return authTime
        elif unAuthTime:
            return unAuthTime
        else:
            return None        

    def buildReportObject(self, assetID, assessmentReport):
        #build openining report opbject tags
        reportObject = ET.SubElement(assessmentReport, self.nsAR + "reportObject")
        scanDate = self.getScanDate(assetID)
        #print type(get_localzone())
        #tz = pytz.timezone(get_localzone())
        if (scanDate != None):
            formatedScanDate = datetime.datetime.fromtimestamp(scanDate, get_localzone()).strftime("%Y-%m-%dT%H:%M:%S%z")
            scan_date = formatedScanDate[:-2] + ":" + formatedScanDate[-2:]
            device = ET.SubElement(reportObject, self.nsAR + "device", timestamp=scan_date)
            #get hostname of MIST machine
            hostname = socket.gethostname()
            #build ID reference
            deviceID = ET.SubElement(device, self.nsDevice + "device_ID")
            ET.SubElement(deviceID, self.nsCNDC + "resource").text = hostname
            ET.SubElement(deviceID, self.nsCNDC + "record_identifier").text = str(assetID)
            #Device Identifiers FQDN only if it exists
            dnsExists, fqdn = self.getFQDN(assetID)
            if dnsExists and not (fqdn == ""):
                deviceIdentifier = ET.SubElement(device, self.nsDevice + "identifiers")
                deviceFQDN = ET.SubElement(deviceIdentifier, self.nsDevice + "FQDN", source="DNS")
                ET.SubElement(deviceFQDN, self.nsDevice + "realm")
                ET.SubElement(deviceFQDN, self.nsDevice + "host_name").text = fqdn
            #operational Attributes
            #deviceOpAttr = ET.SubElement(device, self.nsDevice + "operational_attributes")
            #ET.SubElement(deviceOpAttr, self.nsCNDC + "resource").text = hostname
            #ET.SubElement(deviceOpAttr, self.nsCNDC + "record_identifier").text = str(attributeSet)
            #Configuration
            deviceConfig = ET.SubElement(device, self.nsDevice + "configuration")
            #Network config
            mac, ip = self.getIPMAC(assetID)
            if ip and mac:
                deviceNetConfig = ET.SubElement(deviceConfig, self.nsDevice + "network_configuration")
                ET.SubElement(deviceNetConfig, self.nsDevice + "network_interface_ID").text = ip
                deviceHostNet = ET.SubElement(deviceNetConfig, self.nsDevice + "host_network_data")
                ET.SubElement(deviceHostNet, self.nsDevice + "connection_mac_address").text = mac
                deviceConnectionIP = ET.SubElement(deviceHostNet, self.nsDevice + "connection_ip")
                ipType = "IPv6"
                if re.match('^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})){3}$', ip):
                    ipType = "IPv4"
                ET.SubElement(deviceConnectionIP, self.nsCNDC + ipType).text = ip
            #CPE Config
            osCPE = self.getOS(assetID)
            if osCPE:
                deviceCPEInventory = ET.SubElement(deviceConfig, self.nsDevice + "cpe_inventory")
                deviceCPERecord = ET.SubElement(deviceCPEInventory, self.nsDevice + "cpe_record")
                cpePlatformName = ET.SubElement(deviceCPERecord, self.nsCPE + "platformName")
                ET.SubElement(cpePlatformName, self.nsCPE + "assessedName", name=osCPE)

            #Get values on Security Center
            ip, server, repo = self.getSCInfo(assetID)
            sc = GatherSCData()
            #Login to the SC for the asset
            sc.login(server)
            #query the SC on the asset
            data = {'ip':ip, 'repositories':[{'id':repo}]}
            results = sc.get_ip_info(data)
            sc.logout
            #Set the values from Security Center
            if results:
                scValues = results
                #retrieve the fields needed
                tagValues = {'LastCredScanPluginVers':scValues['pluginSet'], 'ScanPolicy':scValues['policyName'],
                             'LastCredScan':scValues['lastAuthRun'], 'BIOSGUID':scValues['biosGUID'],
                             'McAfeeAgentGUID':scValues['mcafeeGUID']}
                #Make the Tags if they exists
                for tag, value in tagValues.iteritems():
                    if value != "":
                        if tag == 'LastCredScan':
                            value = datetime.datetime.fromtimestamp(float(value)).strftime('%Y-%m-%dT%H:%M:%S%z')
                        ET.SubElement(device, self.nsTaggedValue + "taggedString", name=tag, value=value)
    
    def checkAsset(self, assetID, timeFormat):
        #Get the last time the asset was published
        lastPublishedResults = self.db.execute("SELECT arfLast FROM assetPublishTimes WHERE assetID = " + str(assetID))
        lastPublished = None
        for result in lastPublishedResults:
            lastPublished = result[0]
        #If asset has never been published then send back true
        if not lastPublished:
            return True
        else:
            #check asset last published vs last changed date on asset
            lastTaggedResults = self.db.execute("SELECT timestamp from taggedAssets WHERE assetID = " + str(assetID))
            newlyTagged = False
            for result in lastTaggedResults:
                taggedTimestamp = result[0]
                if lastPublished < taggedTimestamp:
                    newlyTagged = True
            return newlyTagged
                 


    def updateAssetPublishDate(self, assetID, currentTime):
        #insert or update the arf timestamp
        assetResult = self.db.execute("SELECT assetID from assetPublishTimes WHERE assetID = " + str(assetID))
        exists = False
        for result in assetResult:
            exists = True
        if not exists:
                   self.db.execute("INSERT INTO assetPublishTimes (assetID, arfLast) VALUES (" + str(assetID) + ", '" + currentTime + "')")
        else:
            self.db.execute("UPDATE assetPublishTimes Set arfLast = '" + currentTime + "' WHERE assetID = " + str(assetID))

    def get_xml_size(self):
        xmlstr = ET.tostring(self.root, encoding='utf-8', method='xml', pretty_print=True)
        if sys.getsizeof(xmlstr) > self.max_size:
            return True
        return False

    def buildReport(self, assetIDList, tempDirectory, refNumber, assessmentReport):
        # assessmentReport = ET.SubElement(self.message, self.nsAR + "AssessmentReport")
        timeFormat = '%Y-%m-%d %H:%M:%S'
        currentTime = datetime.datetime.now().strftime(timeFormat)
        assetCount = 0
        for assetID in assetIDList:
            if self.publishAll:
                assetCount += 1
                self.buildReportObject(assetID, assessmentReport)
                #update last publish date of the asset
                self.updateAssetPublishDate(assetID, currentTime)
                # Check size of self.root, then write file and move to next one
                print_file = self.get_xml_size()
                if print_file:
                    self.write_file(tempDirectory, refNumber)
                    assessmentReport = self.build_xml_header(refNumber)

            else:
                printAsset = self.checkAsset(assetID, timeFormat)
                if printAsset:
                    assetCount += 1
                    self.buildReportObject(assetID, assessmentReport)
                    #update last publish date of the asset
                    self.updateAssetPublishDate(assetID, currentTime)
                    # Check size of self.root, then write file and move to next one
                    print_file = self.get_xml_size()
                    if print_file:
                        self.write_file(tempDirectory, refNumber)
                        assessmentReport = self.build_xml_header(refNumber)

        return assetCount

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
        tree.write(tempDirectory + "/" + str(refNumber) + ".arf_" + str(self.doc_count) + ".xml", xml_declaration=True,
                   encoding='utf-8', method='xml', pretty_print=True)
        self.doc_count += 1

    def buildXML(self, assetIDList, refNumber, tempDirectory):

        #build the header info
        assessmentReport = self.build_xml_header(refNumber)

        assetCount = self.buildReport(assetIDList, tempDirectory, refNumber, assessmentReport)

        if assetCount > 0:
            self.write_file(tempDirectory, refNumber)
            return True
        else:
            return False
