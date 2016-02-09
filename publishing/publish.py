import os
import base64
import optparse
import datetime
import zipfile
import shutil
import traceback
import requests

#External Classes
from opattr import OpAttributes 
from arf import ARF
from cveASR import CVE_ASR 
from iavmASR import IAVM_ASR
from pluginASR import Plugin_ASR
from benchmarkASR import Benchmark_ASR

#database stuff
import sys
sys.path.insert(0, '/opt/mist/database')
import config
from sqlalchemy import *
import json

def getAssetList(assetDict):
    assetIDList = []
    for sc, repoDict in assetDict.iteritems():
        for repo, assetList in repoDict.iteritems():
            for asset in assetList:
                if asset not in assetIDList:
                    assetIDList.append(asset)

    return assetIDList

def getAssets(db, scRepoDict):
    #Make asset dictionary
    assetDict = {}
    for sc, repoList in scRepoDict.iteritems():
        if sc not in assetDict:
            assetDict[sc] = {}
        for repo in repoList:
            if not repo in assetDict[sc]:
                assetDict[sc][repo] = []
            assets = db.execute("SELECT assetID FROM Repos WHERE scID = '" + sc + "' and repoID = " + str(repo))
            for asset in assets:
                assetID = asset[0]
                assetDict[sc][repo].append(assetID)
    return assetDict
        

def getAccess(db, userID):
    scDict = {}
    results = db.execute("SELECT scID, repoID FROM userAccess WHERE userID = " + str(userID))
    for scRepo in results:
        if not scRepo[0] in scDict:
            scDict[scRepo[0]] = []
        scDict[scRepo[0]].append(scRepo[1])
    return scDict

def setRefNumber(db, userID):
    #Look up the user in database so we can get username
    results = db.execute("Select username FROM mistUsers WHERE id = " + str(userID))
    for result in results:
        if result:
            username = result[0]
        else:
            print "User does not exist\n"
            sys.exit(1)
    db.execute("INSERT INTO published VALUES (DEFAULT, '" + username + "', " + str(userID) + ", DEFAULT)")
    currentIDs = db.execute("Select id from published ORDER BY id DESC LIMIT 1")
    returnID = 1
    for currentID in currentIDs:
        if currentID:
            returnID = currentID[0]
    return username, returnID
    
def insertLastPublished(db, assetDict, column):
    timeFormat = '%Y-%m-%d %H:%M:%S'
    currentTime = datetime.datetime.now().strftime(timeFormat)
    for sc, repoAssetDict in assetDict.iteritems():
        for repo, assetList in repoAssetDict.iteritems():
                results = db.execute("select scID, repoID FROM repoPublishTimes where scID = '" + sc + "' and repoID = " + str(repo))
                exists = False
                for result in results:
                    if result:
                        exists = True
                if exists:
                    db.execute('update repoPublishTimes set ' + column + ' = "' + currentTime + '" where repoID = ' + str(repo) + ' and scID = "' + sc + '"')
                else:
                    db.execute('insert into repoPublishTimes (scID, repoID,' + column + ') VALUES ("' + sc + '", ' + str(repo) + ', "' + currentTime + '")')
     

def createJob(db, username):
    db.execute("INSERT INTO publishJobs (jobID, finishTime, status, userName) VALUES (DEFAULT, DEFAULT, 'running', '" + username + "')")
    results = db.execute("SELECT LAST_INSERT_ID()")
    for result in results:
        jobID = result[0]
    return jobID

def mark_assets_as_published(db, assetIDList):
    for assetID in assetIDList:
        db.execute("UPDATE Assets set state = 'P' where assetID = " + str(assetID))

def getDb():
    #create the database stuff that we need
    connect_string = 'mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST'
    ssl_args = {'ssl':{'cert':'/opt/mist/database/certificates/mist-interface.crt', 'key':'/opt/mist/database/certificates/mist-interface.key', 'ca':'/opt/mist/database/certificates/si_ca.crt'}}
    db = create_engine(connect_string, connect_args=ssl_args, echo=False)
    #db = create_engine('mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST', echo=False)
    #db.echo = True
    metadata = MetaData(db)
    return db

def publish_error(db, error_message, job_id):
    #Remove the tmp folder
    shutil.rmtree('/opt/mist/publishing/tmp')
    db.execute("UPDATE publishJobs set finishTime = DEFAULT, status = 'Error', filename = '" + error_message + "' WHERE jobID = " + str(jobID))
    sys.exit(1)

if __name__ == "__main__":
    
    #Set parser options
    parser = optparse.OptionParser()
    parser.add_option('--user', action='store', dest="userID", type="int", help="sets which assets to put in XMLs by user access")
    parser.add_option('--assets', action='store_true', dest='arf', default=False, help="use this option to generate arf and opattr files")
    parser.add_option('--cve', action='store_true', dest='cve', default=False, help="use this option to generate CVE ASR")
    parser.add_option('--iavm', action='store_true', dest='iavm', default=False, help="use this option to generate IAVM ASR")
    parser.add_option('--plugin', action='store_true', dest='plugin', default=False, help="use this option to generate Plugin ID ASR")
    parser.add_option('--benchmark', action='store_true', dest='benchmark', default=False, help="use this option to generate Benchmark ASR")
    parser.add_option('--all_asset', action='store_true', dest='allAsset', default=False, help="use this option to publish all assets for a user instead of just changed or new ones")
    parser.add_option('--all_scan', action='store_true', dest='allScan', default=False, help="use this option to publish all scan data per asset instead of just newly discovered data since last published")
    parser.add_option('--site', action='store', dest="site", type="string", default=None, help="sets the cmrs site to publish to, if this option is not selected it will save locally")
    options, remainder = parser.parse_args()

    #if they did not use program right print help and exit
    if not options.userID:
        print "A user ID id required!\n"
        parser.print_help()
        sys.exit(1)
    if not options.site:
        print "A publishing site is required (enter 'localhost' if you want to save locally)"
        parser.print_help()
        sys.exit(1)
    else:
        userID = options.userID
        site = options.site

    try:
        #Initialize jobID
        jobID = None        

        #create database instance
        db = getDb()

        #Keep track of who published which XML
        username, refNumber = setRefNumber(db, userID)

        #Create New entry for job and get that jobs ID
        jobID = createJob(db, username)

        #Build the temp folder to hold building of XML
        tempDirectory = '/opt/mist/publishing/tmp/' + str(refNumber)
        if not os.path.exists(tempDirectory):
            os.makedirs(tempDirectory)    

        #Get Security Center and Repos associated with user
        repoSCDict = getAccess(db, userID)
    
        #Get assets for each security center in a dict by security center and repo
        assetDict = getAssets(db, repoSCDict)

        #Get just the asset ids to build the arf and opattr files
        assetIDList = getAssetList(assetDict)        

        #Build the ARF
        arf = ARF(options.allAsset)
        buildAttr = arf.buildXML(assetIDList, refNumber, tempDirectory)

        if buildAttr:
            #Build the Operational Attributes
            attr = OpAttributes()
            attr.buildXML(assetIDList, refNumber, tempDirectory)

        #Build CVE ASR
        if options.cve:
            cveASR = CVE_ASR(options.allScan)
            cveASR.buildXML(assetDict, refNumber, tempDirectory)
            insertLastPublished(db, assetDict, 'cveLast')

        #Build IAVM ASR
        if options.iavm:
            iavmASR  = IAVM_ASR(options.allScan)
            iavmASR.buildXML(assetDict, refNumber, tempDirectory)
            insertLastPublished(db, assetDict, 'iavmLast')

        #Build the PLugin ASR
        if options.plugin:
            pluginASR = Plugin_ASR(options.allScan)
            pluginASR.buildXML(assetDict, refNumber, tempDirectory)
            insertLastPublished(db, assetDict, 'pluginLast')

        #Build the Benchmark ASR
        if options.benchmark:
            benchmarkASR = Benchmark_ASR(options.allScan)
            benchmarkASR.buildXML(assetDict, refNumber, tempDirectory)
            insertLastPublished(db, assetDict, 'benchmarkLast')

        #Write Zip
        files = [f for f in os.listdir(tempDirectory) if os.path.isfile(os.path.join(tempDirectory, f))]
        if files:
            if site == 'localhost':
                directory = '/opt/mist/frontend/app/MIST/Users/' + username
                if not os.path.exists(directory):
                    os.makedirs(directory)
                zipFileName = 'MIST_' + str(refNumber) + '_' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.zip'
                zipFile = directory + '/' + zipFileName
                zf = zipfile.ZipFile(zipFile, 'w')
                for mistFile in files:
                    zf.write(tempDirectory + '/' + mistFile, mistFile)
                    if "arf" in mistFile:
                        mark_assets_as_published(db, assetIDList)
                zf.close()
                
                #Mark the job as complete and give the name of file
                db.execute("UPDATE publishJobs set finishTime = DEFAULT, status = 'Completed', filename = '" + zipFileName + "' WHERE jobID = " + str(jobID))

            else:
                url = site
                headers = {'Accept': 'application/soap+xml', 'Content-Type': 'text/xml', 'SOAPAction': '"http://tempuri.org/ws/Notify"'}
                for mist_file in files:
                    #Injecting the needed SOAP envolope
                    with open(tempDirectory + '/' + mist_file, 'r') as original_file:
                            data = original_file.readlines();
                    new_file = open(tempDirectory + '/' + mist_file, 'w')
                    new_file.write(data[:1][0])
                    new_file.write('<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">\n')
                    new_file.write('<S:Body>\n')
                    for line in data[1:]:
                        new_file.write(line)
                    new_file.write('</S:Body>\n')
                    new_file.write('</S:Envelope>')
                    new_file.close()

                    #xml_file = {mist_file: open(tempDirecrtory + '/' + mistFile, 'rb')}
                    #cmrs_auth = ('administrator', '@dm1n@dm1n')
                    cert_directory = '/opt/mist/publishing/SecurityCenter4/certificates'
                    for file in os.listdir(cert_directory):
                        if file.endswith(".crt"):
                            cert= os.path.join(cert_directory, file)
                        if file.endswith(".key"):
                            key = os.path.join(cert_directory, file)
                        if file.endswith(".ca"):
                            ca = os.path.join(cert_directory, file)
                    cert_and_key = (cert, key)
                    with open(tempDirectory + '/' + mist_file) as payload:
                        requests.packages.urllib3.disable_warnings()

                        #Try connection and catch responses
                        try:
                            resp = requests.post(url, cert=cert_and_key, data=payload, headers=headers, verify=ca)
                        except requests.exceptions.SSLError as e:
                            publish_error(db, "SSL Error: " + str(e).split("SSL routines:", 1)[1], jobID)
                        except requests.exceptions.ConnectTimeout as e:
                            publish_error(db, "Connection Timeout", jobID)
                        except requests.exceptions.ConnectionError as e:
                            publish_error(db, "Could Not Connet: " + str(e), jobID)
                        
                        #Handle errors sent via the web
                        try:
                            resp.raise_for_status()
                        except requests.exceptions.HTTPError as e:
                            publish_error(db, "Web Error: " + str(e), jobID)

                    #Mark all the assets just published as 'P' in the Assets table
                    if "arf" in mist_file:
                        mark_assets_as_published(db, assetIDList)

                #Mark the job as complete and give the name of file
                db.execute("UPDATE publishJobs set finishTime = DEFAULT, status = 'Completed', filename = 'published to " + url + "' WHERE jobID = " + str(jobID))

            #Mark who published it    
            db.execute("UPDATE published set timestamp = DEFAULT WHERE id = " + str(refNumber))

        else:
            #Mark the job as complete and leave filename field as null
            db.execute("UPDATE publishJobs set finishTime = DEFAULT, status = 'Completed' WHERE jobID = " + str(jobID))
    
        #Remove the tmp folder
        shutil.rmtree('/opt/mist/publishing/tmp')
    
    except Exception as e:
        print e
        print traceback.print_exc()
        #Remove the tmp folder
        shutil.rmtree('/opt/mist/publishing/tmp')
        if jobID:
            error_string = "Error no publication generated"
            publish_error(db, error_string, jobID)
