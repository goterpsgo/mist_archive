import subprocess
import getpass
from sqlalchemy import *
import base64
import py_compile
import os
import hashlib
import ConfigParser
import re

#database stuff
import sys
sys.path.insert(0, '/opt/mist/database')
import config


class PasswordCheck:

    def __init__(self, password):
        self.pw = password
        self.config = ConfigParser.ConfigParser()

    def check_password(self):
        # Get the complexity Rules
        self.config.readfp(open('/opt/mist/database/.password_complexity.conf'))

        # Check complexity
        if not self.long_enough():
            return '\nNot long enough must have ' + self.config.get('Rules', 'length') + ' characters'
        elif not self.has_lowercase():
            return '\nNot enough lower case characters must have at least: ' + self.config.get('Rules', 'lowercase')
        elif not self.has_uppercase():
            return '\nNot enough upper case character must have at least: ' + self.config.get('Rules', 'uppercase')
        elif not self.has_numeric():
            return '\nNot enough numeric characters must have at least: ' + self.config.get('Rules', 'numbers')
        elif not self.has_special():
            return '\nNot enough special characters must have at least: ' + self.config.get('Rules', 'special')
        else:
            return None

    def long_enough(self):
        return len(self.pw) >= self.config.getint('Rules', 'length')

    def has_lowercase(self):
        return len(re.findall(r'[a-z]', self.pw)) >= self.config.getint('Rules', 'lowercase')

    def has_uppercase(self):
        return len(re.findall(r'[A-Z]', self.pw)) >= self.config.getint('Rules', 'uppercase')

    def has_numeric(self):
        return len(re.findall(r'\d', self.pw)) >= self.config.getint('Rules', 'numbers')

    def has_special(self):
        return len(re.findall(r'[^0-9A-Za-z]', self.pw)) >= self.config.getint('Rules', 'special')


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
    while True:
        password = getpass.getpass("\nEnter a password to be used by root for the mysqldb: ")
        pw_complexity = PasswordCheck(password)
        error = pw_complexity.check_password()
        if error:
            print error
        else:
            break
    process_call("/usr/bin/mysqladmin -u root password " + password)     


def encode_password(password):
    return base64.b64encode(password)


def create_mist_admin():
    print "\nCreating initial admin account"
    username = raw_input("\nEnter MIST username: ")
    
    while True:
        mist_password = getpass.getpass("\nEnter MIST password: ")
        confirm_password = getpass.getpass("Confirm password: ")
       
        if mist_password == confirm_password:
            # Check the complexity
            pw_complexity = PasswordCheck(mist_password)
            error = pw_complexity.check_password()
            if error:
                print error
            else:
                break
        else:
            print "\nThe passwords do not match please try again \n"

    # hash password
    hash_object = hashlib.sha256(mist_password)
    hex_pass = hash_object.hexdigest()

    # set up connection
    connect_string = 'mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST'
    ssl_args = {'ssl': {'cert': '/opt/mist/database/certificates/mist-interface.crt',
                        'key': '/opt/mist/database/certificates/mist-interface.key',
                        'ca': '/opt/mist/database/certificates/si_ca.crt'}}
    db = create_engine(connect_string, connect_args=ssl_args, echo=False)
    conn = db.connect()
    
    conn.execute("INSERT INTO mistUsers VALUES (DEFAULT, '" + username + "', '" + hex_pass +
                 "', 2, '', 'admin', '', 'mist', DEFAULT)")

    conn.close()


def main():

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
    set_mysql_pass()

    # restart the mysql service
    process_call("service mysqld restart")

    # Edit the host file to point to mist DB
    #get local ip addr
    f = os.popen("ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/'")
    ip = f.read().rstrip()
    with open("/etc/hosts", "a") as myfile:
        myfile.write(ip + "       mistDB backendHost")

    # create inital admin account for mist
    create_mist_admin()

    # Remove the sql file
    os.remove('/opt/mist/database/mist_db.sql')


if __name__ == "__main__":

    main()


   



