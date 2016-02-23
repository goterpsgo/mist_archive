
import os
import securitycenter4
import securitycenter5
import base64

# databse stuff
import sys
sys.path.insert(0, '/opt/mist/database')
import config
from sqlalchemy import *


class GatherSCData:

    def __init__(self):
        self.master_directory = "/opt/mist/assets/SecurityCenters"
        self.server_file_name = "securitycenter.txt"
        connect_string = 'mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST'
        ssl_args = {'ssl': {'cert': '/opt/mist/database/certificates/mist-interface.crt',
                        'key': '/opt/mist/database/certificates/mist-interface.key',
                        'ca': '/opt/mist/database/certificates/si_ca.crt'}}
        self.db = create_engine(connect_string, connect_args=ssl_args, echo=False)
        self.metadata = MetaData(self.db)
        if not os.path.exists('/var/log/MIST'):
            os.makedirs('var/log/MIST')
        self.log_file = "/var/log/MIST/publishing_errors.log"
        self.sc = None
        self.version = None

    def get_user_password(self, server):
        connection = self.db.connect()
        results = connection.execute("Select username, AES_DECRYPT(password,'" + base64.b64decode(config.password) +
                                     "') FROM scUsers WHERE securityCenter = '" + server + "'").fetchone()
        connection.close()
        return results[0], results[1]

    def login(self, server):
        cert = None
        key = None
        sc_directory = None
        sc_full_path = None
        version = 0
    
        # figure out the directories
        directories = os.listdir(self.master_directory)
        for directory in directories:
            sc_dir = os.path.join(self.master_directory, directory)
            if os.path.isdir(sc_dir):
                if os.path.isfile(os.path.join(sc_dir, self.server_file_name)):
                    server_file = open(os.path.join(sc_dir, self.server_file_name), 'r')
                    for line in server_file:
                        line = line.rstrip()
                        if line.startswith('server='):
                            file_server = line.split('=')[1]
                            if file_server == server:
                                sc_directory = directory
                        elif line.startswith('version='):
                            version = line.split('=')[1]
                    server_file.close()
            if sc_directory:
                sc_full_path = os.path.join(self.master_directory, sc_directory)
                self.version = version
                break

        if sc_full_path and (self.version == '4' or self.version == '5'):
            for cert_file in os.listdir(sc_full_path):
                if cert_file.endswith(".crt"):
                    cert = os.path.join(sc_full_path, cert_file)
                if cert_file.endswith(".key"):
                    key = os.path.join(sc_full_path, cert_file)

            if not cert:
                if self.version == '4':
                    self.sc = securitycenter4.SecurityCenter(server, self.log_file)
                elif self.version == '5':
                    self.sc = securitycenter5.SecurityCenter(server, self.log_file)

                # Login to the sc with username and password
                username, password = self.get_user_password(server)
                self.sc.login(username, password)

            else:
                if self.version == '4':
                    self.sc = securitycenter4.SecurityCenter(server, self.log_file, cert, key)
                elif self.version == '5':
                    self.sc = securitycenter5.SecurityCenter(server, self.log_file, cert, key)
                # Log into SC with cert and key
                self.sc.login()

    def get_ip_info(self, data):
        results = self.sc.get_ip_info(data)
        return results

    def query(self, module, action, data):
        results = self.sc.query(module, action, data)
        return results

