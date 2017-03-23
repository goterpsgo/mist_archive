import base64
import os
import getpass

# databse stuff
from sqlalchemy import *
import sys
sys.path.insert(0, '/opt/mist/database')
import config


def check_server(sc, db_conn):
    # check if there is already an entry for that security center
    users = db_conn.execute("SELECT id, username FROM scUsers WHERE securityCenter = '" + sc + "'").fetchall()
    return users


def insert_user(db_conn):
    # Ask For the Creds
    username = raw_input("Enter the MIST username for Security Center '" + server + "': ")
    password = getpass.getpass("Enter the MIST password for Security Center '" + server + "': ")

    # Insert User and Pass
    db_conn.execute("INSERT INTO scUsers (securityCenter, username, password) VALUES ('" + server + "', '" +
                    username + "', AES_ENCRYPT('" + password + "', '" + enc_pass + "'))")


def update_user(db_conn, users):
    # Check if they want to update or remove user
    user_dict = {'id': users[0][0], 'username': users[0][1]}
    while True:
        resp = raw_input("User '" + user_dict['username'] + "' already exists for '" + server +
                         "' would you like to replace password for '" + user_dict['username'] +
                         "' or remove '" + user_dict['username'] + "' (replace/remove): ").lower()
        if resp == 'replace':
            password = getpass.getpass("\nEnter new password for user '" + user_dict['username'] + "': ")
            db_conn.execute("UPDATE scUsers SET password = AES_ENCRYPT('" + password + "', '" + enc_pass +
                            "') WHERE id = '" + str(user_dict['id']) + "'")
            print "\nPassword Updated!!!"
            break
        elif resp == 'remove':
            db_conn.execute("DELETE FROM scUsers where id = '" + str(user_dict['id']) + "'")
            print "\nUser Removed!!!"
            break
        else:
            print "\nPlease type Replace or Remove only\n"

if __name__ == "__main__":
    
    # get directories for all SC's to pull from
    master_directory = os.path.dirname(os.path.realpath(__file__)) + '/SecurityCenters'
    server_file_name = 'securitycenter.txt'
    directories = os.listdir(master_directory)

    # create the database stuff that we need
    connection_string = 'mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST'
    ssl_args = {'ssl': {'cert': '/opt/mist/database/certificates/mist-interface.crt',
                        'key': '/opt/mist/database/certificates/mist-interface.key',
                        'ca': '/opt/mist/database/certificates/si_ca.crt'}}
    db = create_engine(connection_string, connect_args=ssl_args, echo=False)
    connection = db.connect()

    for directory in directories:
        security_center = os.path.join(master_directory, directory)
        if os.path.isfile(os.path.join(security_center, server_file_name)):
            enc_pass = base64.b64decode(config.password)
            sc_file = open(os.path.join(security_center, server_file_name), 'r')
            server = None
            for line in sc_file:
                line = line.rstrip()
                if line.startswith('server='):
                    server = line.split('=')[1]
            sc_file.close()

            if server:
                while True:
                    answer = raw_input("\nFound Security Center '" + server +
                                       "' would you like to add/update credentials [y/n]: ").lower()
                    if answer == 'y':
                        # Check if there is already an entry for this server
                        results = check_server(server, connection)
                        print ""
                        if len(results) < 1:
                            insert_user(connection)
                            break
                        elif len(results) == 1:
                            update_user(connection, results)
                            break
                        else:
                            print "Error there are too many entries for this security center, " \
                                  "someone must have entered entry manually!"
                            break
                    elif answer == 'n':
                        break
                    else:
                        print "\nPlease type only y or n!\n"
