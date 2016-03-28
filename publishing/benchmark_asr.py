
import socket
import base64
import datetime
import pytz
import os

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

class Benchmark_ASR:

    def __init__(self, allScan):

        #Set wether or not to include all scan data
        self.allScan = allScan

        # Set max size of xml
        self.max_size = 19922944
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
        summRes = "http://metadata.dod.mil/mdr/ns/netops/net_defense/summary_res/0.41"

        #Converting to right namespace
        self.nsWSNT = "{%s}" % wsnt
        self.nsWSA = "{%s}" % wsa
        self.nsTaggedValue = "{%s}" % tagged_value
        self.nsAR = "{%s}" % ar
        self.nsOPTATTR = "{%s}" % opsattr
        self.nsCNDC = "{%s}" % cndc
        self.nsDevice = "{%s}" % device
        self.nsCPE = "{%s}" % cpe
        self.nsSummRes = "{%s}" % summRes

        #initial namespace map
        self.nsMap = {"wsnt" : wsnt, "xsi" : xsi, "tagged_value" : tagged_value, "wsa" : wsa, "ar":ar, "organization":organization, 
                  "person":person, "geoloc":geoloc, "opsattr":opsattr, "cndc":cndc, "device":device, "cpe":cpe, "summRes":summRes}

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
        ET.SubElement(self.notificationMessage, self.nsWSNT + "Topic", Dialect="docs.oasis-open.org/wsn/t-1/TopicExpression/Simple").text = "acas.benchmark.results"

    def buildProducerReference(self, refNumber):
        producerReference = ET.SubElement(self.notificationMessage, self.nsWSNT + "ProducerReference")
        ET.SubElement(producerReference, self.nsWSA + "Address").text = socket.gethostname()
        metadata = ET.SubElement(producerReference, self.nsWSA + "Metadata")
        ET.SubElement(metadata, self.nsWSA + "MessageID").text = socket.gethostname() + ":acas.benchmark.results:local:" + str(refNumber)
        ET.SubElement(metadata, self.nsTaggedValue + "taggedString", name="MIST", value="0.1") 

    def getSCInfo(self, sc):
        results = self.db.execute('SELECT serverName FROM Repos WHERE scID = "' + sc + '"')
        server = None
        if results:
            for result in results:
                server = result[0]
        return server

    def getIPList(self, assetList):
        assetIPDict = {}
        for asset in assetList:
            ipResults = self.db.execute("SELECT ip FROM Assets WHERE assetID = " + str(asset))
            ip = None
            for result in ipResults:
                ip = result[0]
            assetIPDict[ip] = asset
        return assetIPDict

    def querySC(self, sc, assetList, data, cceDict):
        assetIPDict = self.getIPList(assetList)
        results = sc.query('vuln', 'query', data)
        if results:
            for result in results['results']:
                if result['pluginName']:
                    #split the plugin name to get benchmark details
                    benchmarkFields = result['pluginName'].split(":")
                    benchmarkKey = benchmarkFields[4] + ":" + benchmarkFields[3]
                    benchmarkValue = benchmarkFields[0] + ":" + benchmarkFields[2]

                    #figure out if its pass, fail, or mitigated
                    if data['sourceType'] == 'patched':
                        pluginResult = 'mitigated'
                    else:
                        if result['severity'] == '0':
                            pluginResult = 'pass'
                        elif result['severity'] == '2':
                            if 'NOT SELECTED' in result['pluginText']:
                                continue
                            else:
                                pluginResult = 'error'
                        else:
                            pluginResult = 'fail'
            
                    #add the plugin result to the CCEID
                    benchmarkValue = benchmarkValue + ":" + pluginResult
                    ip = result['ip']
                    if ip in assetIPDict:
                        #create and add to the main dictionary all assets that 
                        if benchmarkKey not in cceDict:
                            cceDict[benchmarkKey] = {}
                        tempDict = cceDict[benchmarkKey]
                        if benchmarkValue not in tempDict:
                            tempDict[benchmarkValue] = []
                        if not assetIPDict[ip] in tempDict[benchmarkValue]:
                            tempDict[benchmarkValue].append(assetIPDict[ip])
                        cceDict[benchmarkKey] = tempDict
            
        return cceDict
            
    def getNumDaysSincePublish(self, sc, repo):
        #Get the current time
        timeFormat = '%Y-%m-%d %H:%M:%S'
        currentTime = datetime.datetime.now()

        #Get the last publish time
        timeResults = self.db.execute('SELECT benchmarkLast FROM repoPublishTimes WHERE repoID = ' + str(repo) + ' and scID="' + sc + '"')
        lastPublished = None
        for result in timeResults:
            lastPublished = result[0]

        if lastPublished:
            timeDiff = currentTime - lastPublished
            timeDiffDays = timeDiff.days
            if timeDiffDays < 1:
                interval = 1
            else:
                timeDiffSeconds = timeDiff.seconds
                if timeDiffSeconds > 0:
                    interval = timeDiffDays + 1
        else:
            interval = "All"

        return interval

    def get_xml_size(self):
        xmlstr = ET.tostring(self.root, encoding='utf-8', method='xml', pretty_print=True)
        if sys.getsizeof(xmlstr) > self.max_size:
            return True
        return False

    def buildReport(self, assetDict, tempDirectory, refNumber, resultsPackage):
        #Gather the CVE totals and who they belong to
        cceBenchmarkDict = {}
        cceMitigatedDict = {}
        for scID, repoDict in assetDict.iteritems():
            server = self.getSCInfo(scID)
            sc = GatherSCData()
            sc.login(server)

            for repo, assetList in repoDict.iteritems():
                #Get the assets last publish date
                interval = self.getNumDaysSincePublish(scID, repo)
            
                #Gather All the failed cce's
                if self.allScan or interval == "All":
                    filters = [{'filterName': 'repositoryIDs', 'operator': '=', 'value': repo}, {'filterName': 'cceID', 'operator':'=', 'value':'CCE'}]
                else:
                    filters = [{'filterName': 'repositoryIDs', 'operator': '=', 'value': repo}, {'filterName': 'cceID', 'operator':'=', 'value':'CCE'}, {'filterName':'lastSeen', 'operator': '=', 'value': '0:' + str(interval)}]
                data = {'tool':'vulndetails', 'sourceType':'cumulative', 'startOffset':0, 'endOffset': 2147483647, 'filters': filters}
                cceBenchmarkDict = self.querySC(sc, assetList, data, cceBenchmarkDict)

                #Gather All the mitigated cve's
                data = {'tool':'vulndetails', 'sourceType':'patched', 'startOffset':0, 'endOffset': 2147483647, 'filters': filters}
                cceBenchmarkDict = self.querySC(sc, assetList, data, cceBenchmarkDict)
        
        benchmarkCount = 0
        for benchmark_sc, cceDict in cceBenchmarkDict.iteritems():
            benchmarkCount += 1
            benchmarkSplit = benchmark_sc.split(":")
            benchmarkProfile, benchmarkIdentifier = benchmarkSplit[0], benchmarkSplit[1]
            
            #Set the benchmark ID
            benchmark = self.build_xml_profile(resultsPackage, benchmarkProfile, benchmarkIdentifier)

            #Print out the cce for particular profile
            for cceRuleID, assetList in cceDict.iteritems():
                cceRuleSplit = cceRuleID.split(":")
                cceID, ruleID, result = cceRuleSplit[0], cceRuleSplit[1], cceRuleSplit[2]
                #Build the xml for each result
                ruleResult = ET.SubElement(benchmark, self.nsSummRes + "ruleResult", ruleID=ruleID)
                ET.SubElement(ruleResult, self.nsSummRes + "ident").text = cceID
                ruleComplianceItem = ET.SubElement(ruleResult, self.nsSummRes + "ruleComplianceItem", ruleResult=result)
                result = ET.SubElement(ruleComplianceItem, self.nsSummRes + "result", count=str(len(assetList)))
                for asset in assetList:
                    ET.SubElement(result, self.nsSummRes + "deviceRecord", record_identifier=str(asset))
                print_report = self.get_xml_size()
                if print_report:
                    self.write_file(tempDirectory, refNumber)
                    resultsPackage = self.build_xml_header(refNumber, assetDict)
                    benchmark = self.build_xml_profile(resultsPackage, benchmarkProfile, benchmarkIdentifier)
        return benchmarkCount

    def build_xml_profile(self, resultsPackage, benchmarkProfile, benchmarkIdentifier):
        benchmark = ET.SubElement(resultsPackage, self.nsSummRes + "benchmark", profile=benchmarkProfile)
        benchmarkID = ET.SubElement(benchmark, self.nsSummRes + "benchMarkID")
        ET.SubElement(benchmarkID, self.nsCNDC + "resource").text = socket.gethostname()
        ET.SubElement(benchmarkID, self.nsCNDC + "record_identifier").text = benchmarkIdentifier
        return benchmark

    def build_xml_header(self, refNumber, assetDict):
        #build the static portion
        self.buildStatic()

        #build the producer reference
        self.buildProducerReference(refNumber)

        #Message Tag
        self.message = ET.SubElement(self.notificationMessage, self.nsWSNT + "Message")

        resultsPackage = ET.SubElement(self.message, self.nsSummRes + "ResultsPackage")

        #Set population chiaracteritics
        assetCount = 0
        for scID, repoDict in assetDict.iteritems():
            for repo, assetList in repoDict.iteritems():
                assetCount = assetCount + len(assetList)
        popChar = ET.SubElement(resultsPackage, self.nsSummRes + "PopulationCharacteristics", populationSize=str(assetCount))
        ET.SubElement(popChar, self.nsSummRes + "resource").text = socket.gethostname()

        return resultsPackage

    def write_file(self, tempDirectory, refNumber):
        # Build the XML Tree
        tree = ET.ElementTree(self.root)
        tree.write(tempDirectory + "/" + str(refNumber) + ".benchmark.asr_" + str(self.doc_count) + ".xml",
                   xml_declaration=True, encoding='utf-8', method='xml', pretty_print=True)
        self.doc_count += 1
    
    def buildXML(self, assetDict, refNumber, tempDirectory):

        resultsPackage = self.build_xml_header(refNumber, assetDict)

        #build the report
        benchmarkCount = self.buildReport(assetDict, tempDirectory, refNumber, resultsPackage)

        #Output the tree to a file
        if benchmarkCount > 0:
            self.write_file(tempDirectory, refNumber)


