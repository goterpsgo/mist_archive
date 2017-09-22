#!/usr/bin/env python

import subprocess
import getpass
from sqlalchemy import *
import base64
import py_compile
import os
import hashlib
import ConfigParser
import re
import commands

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


def reset_admin_password():
    print "\nResetting admin account password"
    
    while True:
        mist_password = getpass.getpass("\nEnter new MIST password: ")
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

    conn.execute("UPDATE mistUsers set password = '" + hex_pass + "' where id = 1")

    print "\nPassword for admin user updated; password digest is '%s'." % hex_pass

    conn.close()


def main():
    reset_admin_password()

if __name__ == "__main__":
    main()
