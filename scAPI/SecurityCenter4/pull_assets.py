
import os
import base64

#databse stuff
import sys
sys.path.insert(0, '/opt/mist/database')
import config
from sqlalchemy import *

#Path for SC module
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/modules")
from securitycenter import SecurityCenter



def getUserPassword(db, server):
    connection = db.connect()
    results = connection.execute("Select username, AES_DECRYPT(password,'" + base64.b64decode(config.password) + "') FROM scUsers WHERE securityCenter = '" + server + "'").fetchone()
    connection.close()
    return results[0], results[1]


def getScInfo(directory, server, logFile, db):
    #Grab key and cert if one is missing error will be caught in connect
    cert = None
    key = None
    for file in os.listdir(directory):
        if file.endswith(".crt"):
            cert = os.path.join(directory, file)
        if file.endswith(".key"):
            key = os.path.join(directory, file)

    if not cert:    
        #Connect to security center
        sc = SecurityCenter(server, logFile)
        #Initial Connection to Security Center will contain information about Security Center using password
        username, password = getUserPassword(db, server)
        data = {'username':username, 'password':password}
        resp = sc.connect('auth', 'login', input = data)
     
        #Get the SC id in a seperate call
        sysResponse = sc.connect('system', 'init')
        resp['uuid'] = sysResponse['uuid']

    else:
        #Connect to security center
        sc = SecurityCenter(server, logFile, cert, key)

        #Initial Connection to Security Center will contain information about Security Center
        resp = sc.connect('system', 'init')

    #If the connection failed and we did not get any data back then we move on to next cert and key pair
    if resp == None:
        response = {'connected':'N'}
        return sc, response
    
    else:
        response = {'connected':'Y'}
        #Grabbing the token and sessionID for all future calls in this connection
        response['token'] = resp['token']
        response['cookie'] = resp['sessionID']

        #Getting the SC Information for assets
        response['scID'] = resp['uuid']

    return sc, response

def checkAsset(assetsTable, assetDictionary, scInfo):
    #Checking if the asset already exists by checking unique attribute in order biosGUID, netbiosName, dns, ip/mac combo 
    assetExists = False
    assetID = 0
    results = False

    #checking for biosGUID match first
    if assetDictionary['biosGUID'] and assetExists == False:
        s = assetsTable.select(assetsTable.c.biosGUID == assetDictionary['biosGUID'])
        assetExists, results = checkExists(s)

    #checking for dnsName second
    if assetDictionary['dnsName'] and assetExists == False:
        s = assetsTable.select(assetsTable.c.dnsName == assetDictionary['dnsName'])
        assetExists, results = checkExists(s)

    #checking for netbiosName third
    if assetDictionary['netbiosName'] and assetExists == False:
        s = assetsTable.select(assetsTable.c.netbiosName == assetDictionary['netbiosName'])
        assetExists, results = checkExists(s)

    #Checking for ip and mac combo last
    if assetDictionary['ip'] and assetDictionary['macAddress'] and assetExists == False:
        s = assetsTable.select(and_(assetsTable.c.ip == assetDict['ip'], 
        assetsTable.c.macAddress == assetDict['macAddress']))
        assetExists, results = checkExists(s)

    #If any of the returned true then we get that assets ID
    if results:
        for row in results:
            assetID = row[0]

    return assetExists, assetID

def checkRepo(aID, rID, sID, repoTable):
    
    #Check the repo to make sure asset has already been added to it
    s = repoTable.select(and_(repoTable.c.repoID == rID, repoTable.c.scID == sID, repoTable.c.assetID == aID))
    repoExists, results = checkExists(s)

    #Return the result of the query
    if repoExists:
        return True
    else:
        return False

def checkExists(stmt):
    #Execute SQL query
    rs =stmt.execute()
    if rs:
        #If we get results then get the resuls
        results = []
        for row in rs:
            results.append(row)

        #If we got results then return true and results, if not then return false
        if results:
            return True, results
        else:
            return False, None
    else:
        return False, None

def updateAsset(assetsTable, assetDictionary, assetID, assetInfo, scInfo):
    #Get all Values that will be updated
    values = {}
    for info in assetInfo:
        values[info] = assetDictionary[info]
    del values['repositoryID']
    
    #update values in database
    u = assetsTable.update().where(assetsTable.c.assetID == assetID).values(values)
    u.execute()

def insertAsset(db, assetsTable, assetDictionary, assetInfo, scInfo):
    #Get all the values that will be inserted
    values = {'state':'R'}
    for info in assetInfo:
        values[info] = assetDictionary[info]
    del values['repositoryID']
    
    #insert values into database
    i = assetsTable.insert()
    i.execute(values)
    results = db.execute("Select assetID from Assets ORDER BY assetID DESC LIMIT 1")
    for row in results:
        assetID = row[0]
    return assetID
    
def insertRepo(repoID, scID, repoName, serverName, assetID, repoTable):
    #get the values needed to insert an asset into repo table
    values = {'repoID':repoID, 'scID':scID, 'repoName':repoName, 'serverName':serverName, 'assetID':assetID}

    #insert the asset
    i = repoTable.insert()
    i.execute(values)

def getDbTables(assetTableName, repoTableName):
    #create the database stuff that we need
    connection_string = 'mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST'
    ssl_args = {'ssl':{'cert':'/opt/mist/database/certificates/mist-interface.crt', 'key':'/opt/mist/database/certificates/mist-interface.key', 'ca':'/opt/mist/database/certificates/si_ca.crt'}}
    db = create_engine(connection_string, connect_args=ssl_args, echo=False)
    #db.echo = True
    metadata = MetaData(db)
    assetsTable = Table(assetTableName, metadata, autoload=True)
    repoTable = Table(repoTableName, metadata, autoload=True)
    return db, assetsTable, repoTable

if __name__ == "__main__":

    #Create log directory if it does not exist
    if not os.path.exists('/var/log/MIST'):
        os.makedirs('/var/log/MIST')
    logFile = '/var/log/MIST/assetGathering.log'
    
    #create the database stuff that we need
    db, assetsTable, repoTable = getDbTables('Assets', 'Repos')

    #get directories for all SC's to pull from
    masterDirectory = os.path.dirname(os.path.realpath(__file__)) + '/SecurityCenters'
    serverFileName = 'securitycenter.txt'    
    directories = os.listdir(masterDirectory)

    for directory in directories:
        securityCenter = os.path.join(masterDirectory, directory)
        if os.path.isdir(securityCenter):
            if os.path.isfile(os.path.join(securityCenter, serverFileName)):
                #get the SC to try and log into
                serverFile = open(os.path.join(securityCenter, serverFileName), 'r')
                for line in serverFile:
                    line = line.rstrip()
                    if line.startswith('server='):
                        server = line.split('=')[1]
                serverFile.close()
    
                #Logging into SC and getting info needed    
                sc, response = getScInfo(securityCenter, server, logFile, db)
    
                if response['connected'] == 'Y':

                    #Getting the securitycenter id
                    scID = response['scID']

                    #Getting all the repos names
                    repoDict = {}
                    repos = sc.connect('group', 'init', response['token'], response['cookie'])
                    for repo in repos['repositories']:
                        repoDict[repo['id']] = repo['name']

                    #Creating dictionary for query agains SC to get all available assets in an organization
                    data = {'tool': 'sumip','sourceType': 'cumulative', 'startOffset': 0, 'endOffset': 2147483647}
                    #Make another call to get assets with connection already established
                    assets = sc.connect('vuln', 'query', response['token'], response['cookie'], data)
                    #Parsing assets receive, will have to chose which information we want to keep and database it in this loop
                    assetInfo = ['repositoryID', 'biosGUID', 'macAddress', 'ip', 'dnsName', 'lastAuthRun', 'lastUnauthRun', 'netbiosName', 'osCPE', 'mcafeeGUID']
         
                    for asset in assets['results']:
                        #Get the info asset info we want
                        assetDict = {}
                        for info in assetInfo:
                            assetDict[info] = asset[info]
         
                        #If there is not unauth or auth run value changing to 0 since type is integer    
                        if assetDict['lastAuthRun'] == '':
                            assetDict['lastAuthRun'] = 0
                        if assetDict['lastUnauthRun'] == '':
                            assetDict['lastUnauthRun'] = 0
          
                        #Check the asset to see if it already exists
                        assetExists, assetID = checkAsset(assetsTable, assetDict, response) 
    
                        #If it exists update the info, if not create eh new asset
                        if assetExists:
                            updateAsset(assetsTable, assetDict, assetID, assetInfo, response)
                            #check repo and insert new ones if none are there
                            repoExists = checkRepo(assetID, assetDict['repositoryID'], scID, repoTable)
                            if not repoExists:
                                insertRepo(assetDict['repositoryID'], scID, repoDict[assetDict['repositoryID']], server, int(assetID), repoTable)
                        else:
                            assetID = insertAsset(db, assetsTable, assetDict, assetInfo, response)
                            insertRepo(assetDict['repositoryID'], scID, repoDict[assetDict['repositoryID']], server, int(assetID), repoTable)    
