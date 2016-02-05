import subprocess
import getpass
from sqlalchemy import *
import base64
import py_compile
import os
import hashlib

#database stuff
import sys
sys.path.insert(0, '/opt/mist/database')
import config


def process_call(command, input_file=None):
    arguments = command.split()
    if input_file:
        f = open(input_file)
        subprocess.call(arguments, stdin=f)
        f.close()
    else:
        subprocess.call(arguments)


def set_mysql_pass():
    # Ask For the Creds
    password = getpass.getpass("\nEnter a password to be used by root for the mysqldb: ")
    process_call("/usr/bin/mysqladmin -u root password " + password)     
    return password


def encode_password(password):
    return base64.b64encode(password)


def create_mist_admin():
    print "\nCreating initial admin account"
    username = raw_input("\nEnter MIST username: ")
    
    while True:
        password = getpass.getpass("Enter MIST password: ")
        confirm_password = getpass.getpass("Confirm password: ")
       
        if password == confirm_password:
            break
        else:
            print "\nThe passwords do not match please try again \n"
   
    # hash password
    hash_object = hashlib.sha256(password)
    hex_pass = hash_object.hexdigest()

    # set up connection
    connect_string = 'mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST'
    ssl_args = {'ssl': {'cert': '/opt/mist/database/certificates/mist-interface.crt',
                        'key': '/opt/mist/database/certificates/mist-interface.key',
                        'ca': '/opt/mist/database/certificates/si_ca.crt'}}
    db = create_engine(connect_string, connect_args=ssl_args, echo=False)
    conn = db.connect()
    
    conn.execute("INSERT INTO mistUsers VALUES (DEFAULT, '" + username + "', '" + hex_pass +
                 "', 2, '', 'admin', '', 'mist')")

    conn.close()


if __name__ == "__main__":
   
    # create directory for mysql logs
    process_call("mkdir /var/log/mysql")
    process_call("chown mysql.mysql /var/log/mysql")

    # start mysqld
    process_call("service mysqld start")
    
    # set mysqld in chkconfig
    process_call("chkconfig mysqld on")
    
    # Add the database file
    process_call("mysql -u root", "/opt/mist/database/mist_db.sql")

    # Set the mysqld root password
    root_pass = set_mysql_pass()

    # restart the mysql service
    process_call("service mysqld restart")
    
    # Edit the host file to point to mist DB
    with open("/etc/hosts", "a") as myfile:
        myfile.write("127.0.0.1       mistDB backendHost")        

    # create inital admin account for mist
    create_mist_admin()


