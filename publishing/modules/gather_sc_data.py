
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
        connect_string = 'mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST'
        ssl_args = {'ssl': {'cert': '/opt/mist/database/certificates/mist-interface.crt',
                        'key': '/opt/mist/database/certificates/mist-interface.key',
                        'ca': '/opt/mist/database/certificates/si_ca.crt'}}
        self.db = create_engine(connect_string, connect_args=ssl_args, echo=False)
        self.metadata = MetaData(self.db)
        self.sc = None
        self.version = None

    def get_user_password(self, server):
        connection = self.db.connect()
        results = connection.execute("Select username, AES_DECRYPT(password,'" + base64.b64decode(config.password) +
                                     "') FROM scUsers WHERE securityCenter = '" + server + "'").fetchone()
        connection.close()
        return results[0], results[1]

    def get_sc_data(self, server):
        connection = self.db.connect()
        print server
        sql = "SELECT version, username, pw, certificateFile, keyFile FROM securityCenters WHERE fqdn_IP='" + server + "'"
        print sql
        results = connection.execute(sql)
        sc_details = {}
        for result in results:
            sc_details = {'server': server, 'version': result[0], 'username': result[1], 'password': result[2],
                          'cert': result[3], 'key': result[4]}
        return sc_details


    def login(self, server):
        sc_details = self.get_sc_data(server)
        print sc_details
        if sc_details:
            if sc_details['version'] == '4':
                self.sc = securitycenter4.SecurityCenter(server, sc_details['cert'], sc_details['key'])
            elif sc_details['version'] == '5':
                self.sc = securitycenter5.SecurityCenter(server, sc_details['cert'], sc_details['key'])
            # Log into SC with cert and key
            if sc_details['cert']:
                self.sc.login()
            else:
                self.sc.login(sc_details['username'], sc_details['password'])

    def get_ip_info(self, data):
        results = self.sc.get_ip_info(data)
        return results

    def query(self, module, action, data):
        results = self.sc.query(module, action, data)
        return results

