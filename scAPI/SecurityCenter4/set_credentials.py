
#databse stuff
from sqlalchemy import *
import sys
sys.path.insert(0, '/opt/mist/database')
import config

import base64
import os
import getpass

def checkExists(server, user, connection):
    # check if there is already an entry
    results = connection.execute("SELECT id FROM scUsers WHERE securityCenter = '" + server + "' and username = '" + user + "'").fetchone()
    if results:
        return True, results[0]
    else:
        return False, 0
    
def checkServer(server, connection):
    #check if there is already an entry for that security center
    results = connection.execute("SELECT id, username FROM scUsers WHERE securityCenter = '" + server + "'").fetchall()
    return results

def insertUser(connection):
    #Ask For the Creds
    username = raw_input("Enter the MIST username for Security Center '" + server + "': ")
    password = getpass.getpass("Enter the MIST password for Security Center '" + server + "': ")

    #Insert User and Pass
    connection.execute("INSERT INTO scUsers (securityCenter, username, password)" \
               "VALUES ('" + server + "', '" + username + "', AES_ENCRYPT('" + password + "', '" + enc_pass + "'))")

def updateUser(connection, results):
     #Check if they want to update or remove user
     userDict = {'id' : results[0][0], 'username' : results[0][1]}
     while True:
        answer = raw_input("User '" + userDict['username'] + "' already exists for '" + server + "' would "\
                   "you like to replace password for '" + userDict['username'] + "' or remove '" + userDict['username'] +
                   "' (replace/remove): ").lower()
        if answer == 'replace':
            password = getpass.getpass("\nEnter new password for user '" + userDict['username'] + "': ")
            connection.execute("UPDATE scUsers SET password = AES_ENCRYPT('" + password + "', '" + enc_pass + "') "\
                       "WHERE id = '" + str(userDict['id']) + "'")
            print "\nPassword Updated!!!"
            break
        elif answer == 'remove':
            connection.execute("DELETE FROM scUsers where id = '" + str(userDict['id']) + "'")
            print "\nUser Removed!!!"
            break
        else:
            print "\nPlease type Replace or Remove only\n"

if __name__ == "__main__":
    
    #get directories for all SC's to pull from
    masterDirectory = 'SecurityCenters'
    serverFileName = 'securitycenter.txt'
    directories = os.listdir(masterDirectory)

    #create the database stuff that we need
    connection_string = 'mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST'
    ssl_args = {'ssl':{'cert':'/opt/mist/database/certificates/mist-interface.crt', 'key':'/opt/mist/database/certificates/mist-interface.key', 'ca':'/opt/mist/database/certificates/si_ca.crt'}}
    db = create_engine(connection_string, connect_args=ssl_args, echo=False)
    connection = db.connect()

    for directory in directories:
        securityCenter = os.path.join(masterDirectory, directory)
        if os.path.isdir(securityCenter):
            if os.path.isfile(os.path.join(securityCenter, serverFileName)):
                enc_pass = base64.b64decode(config.password)
                scFile = open(os.path.join(securityCenter, serverFileName), 'r')
                for line in scFile:
                    line = line.rstrip()
                    if line.startswith('server='):
                        server = line.split('=')[1]
                scFile.close()
        
                while True:
                    answer = raw_input("\nFound Security Center '" + server + "' would you like to add/update credentials [y/n]: ").lower()
                    if answer == 'y':        
                        #Check if there is already an entry for this server    
                        results = checkServer(server, connection)
                        print ""

                        if len(results) < 1:
                            insertUser(connection)
                        elif len(results) == 1:
                            updateUser(connection, results)
                        else:
                            print "Error there are too many entries for this security center, someone must have entered entry manually!"
                        break

                    elif answer == 'n':
                        break
                    else:
                        print "\nPlease type only y or n!\n"    
        

