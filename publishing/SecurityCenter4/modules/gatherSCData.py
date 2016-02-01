
import os
from securitycenter import SecurityCenter
import base64

#databse stuff
import sys
sys.path.insert(0, '/opt/mist/database')
import config
from sqlalchemy import *

class GatherSCData():

    def __init__(self):
        self.masterDirectory = "/opt/mist/scAPI/SecurityCenter4/SecurityCenters"
        self.serverFileName = "securitycenter.txt"
        self.db = create_engine('mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST', echo=False)
        self.metadata = MetaData(self.db)
        if not os.path.exists('/var/log/MIST'):
            os.makedirs('var/log/MIST')
        self.logFile = "/var/log/MIST/publishing_errors.log"

    def getUserPassword(self, server):
        connection = self.db.connect()
        results = connection.execute("Select username, AES_DECRYPT(password,'" + base64.b64decode(config.password) + "') FROM scUsers WHERE securityCenter = '" + server + "'").fetchone()
        connection.close()
        return results[0], results[1]

    def login(self, server):
        cert = None
        key = None
        scDirectory = None    
    
        #figure out the directories
        directories = os.listdir(self.masterDirectory)
        for directory in directories:
            scDir = os.path.join(self.masterDirectory, directory)
            if os.path.isdir(scDir):
                if os.path.isfile(os.path.join(scDir, self.serverFileName)):
                    serverFile = open(os.path.join(scDir, self.serverFileName), 'r')
                    for line in serverFile:
                        line = line.rstrip()
                        if line.startswith('server='):
                            fileServer = line.split('=')[1]
                            if fileServer == server:
                                scDirectory = directory
                                break
                    serverFile.close()
            if scDirectory:
                scFullPath = os.path.join(self.masterDirectory, scDirectory)
                break

        if scDirectory:
            for file in os.listdir(scFullPath):
                if file.endswith(".crt"):
                    cert= os.path.join(scFullPath, file)
                if file.endswith(".key"):
                    key = os.path.join(scFullPath, file)

            if not cert:
                sc = SecurityCenter(server, self.logFile)
                #Login to the sc with username and password
                username, password = self.getUserPassword(server)
                data = {'username':username, 'password':password}
                resp = sc.connect('auth', 'login', input=data)
            else:
                sc = SecurityCenter(server, self.logFile, cert, key)
                #Log into SC with cert and key
                resp = sc.connect('system', 'init')

            if resp:
                self.sc = sc
                self.token = resp['token']
                self.cookie = resp['sessionID']
    
    def query(self, module, action, data):
        results = self.sc.connect(module, action, self.token, self.cookie, data)
        return results
    
            
