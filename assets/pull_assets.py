
import os
import base64

# databse stuff
import sys
sys.path.insert(0, '/opt/mist/database')
import config
from sqlalchemy import *

# Path for SC module
from modules import securitycenter4
# from modules import securitycenter5


class SecurityCenter:

    def __init__(self, hostname, version, cert, key, log, db):
        self.host = hostname
        self.cert = cert
        self.key = key
        self.version = version
        self.log = log
        if version == '4':
            self.sc = securitycenter4.SecurityCenter(self.host, self.cert, self.key, self.log)
        # elif version == '5':
            # self.sc = securitycenter5.SecurityCenter(self.host, self.cert, self.key, self.log)

    def get_user_password(self):
        connection_string = 'mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST'
        ssl_args = {'ssl': {'cert': '/opt/mist/database/certificates/mist-interface.crt',
                            'key': '/opt/mist/database/certificates/mist-interface.key',
                            'ca': '/opt/mist/database/certificates/si_ca.crt'}}
        db = create_engine(connection_string, connect_args=ssl_args, echo=False)
        connection = db.connect()
        results = connection.execute("Select username, AES_DECRYPT(password,'" + base64.b64decode(config.password) +
                                     "') FROM scUsers WHERE securityCenter = '" + self.host + "'").fetchone()
        connection.close()
        return results[0], results[1]

    def login(self):
        # Perform login with creds or cert and key
        if self.cert:
            sc_login_result = self.sc.login()
        else:
            username, password = self.get_user_password()
            sc_login_result = self.sc.login(username, password)

        return sc_login_result

    def get_sc_id(self):
        return self.sc.get_sc_id()

    def get_repo_mapping(self):
        repo_dictionary = {}
        repositories = self.sc.get_repositories()
        if repositories:
            for repository in repositories:
                repo_dictionary[repository['id']] = repository['name']
        return repo_dictionary

    def get_asset_list(self, fields):
        return self.sc.get_asset_info(fields)


class Database:

    def __init__(self, needed_fields):
        connection_string = 'mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST'
        ssl_args = {'ssl': {'cert': '/opt/mist/database/certificates/mist-interface.crt',
                            'key': '/opt/mist/database/certificates/mist-interface.key',
                            'ca': '/opt/mist/database/certificates/si_ca.crt'}}
        self.db = create_engine(connection_string, connect_args=ssl_args, echo=False)
        self.metadata = MetaData(self.db)
        self.assets_table = Table('Assets', self.metadata, autoload=True)
        self.repo_table = Table('Repos', self.metadata, autoload=True)
        self.update_fields = needed_fields
        self.insert_fields = needed_fields + ['state']

    def check_exists(self, sql):
        # Execute SQL query
        rs = self.db.execute(sql)
        found = False
        primary_key = 0
        for row in rs:
            primary_key = row[0]
            found = True

        if found:
            return True, primary_key
        else:
            return False, None

    def check_asset(self, asset_dictionary):
        # Checking if the asset already exists by checking unique attribute in order
        # biosGUID, netbiosName, dns, ip/mac combo
        asset_found = False
        mist_id = 0

        # checking for biosGUID match first
        if asset_dictionary['biosGUID'] and asset_found is False:
            sql = "SELECT assetID FROM Assets WHERE biosGUID = '%s'" % asset_dictionary['biosGUID']
            asset_found, mist_id = self.check_exists(sql)

        # checking for dnsName second
        if asset_dictionary['dnsName'] and asset_found is False:
            sql = "SELECT assetID FROM Assets WHERE dnsName = '%s'" % asset_dictionary['dnsName']
            asset_found, mist_id = self.check_exists(sql)

        # checking for netbiosName third
        if asset_dictionary['netbiosName'] and asset_found is False:
            sql = "SELECT assetID FROM Assets WHERE netbiosName = '%s'" % asset_dictionary['netbiosName']
            asset_found, mist_id = self.check_exists(sql)

        # Checking for ip and mac combo last
        if asset_dictionary['ip'] and asset_dictionary['macAddress'] and asset_found is False:
            sql = "SELECT assetID FROM Assets WHERE ip = '%s' and macAddress = '%s'" % \
                  (asset_dictionary['ip'], asset_dictionary['macAddress'])
            asset_found, mist_id = self.check_exists(sql)

        return asset_found, mist_id

    def update_asset(self, asset_dict, mist_id):
        # Get all Values that will be updated
        fields = self.update_fields
        sql = "UPDATE Assets SET "
        for info in fields:
            if info is not "repositoryID":
                sql = sql + info + "='" + str(asset_dict[info]) + "', "
        sql = sql[:-2] + " WHERE assetID = " + str(mist_id)
        self.db.execute(sql)

    def check_repo(self, mist_id, repo_id, sec_center_id):
        # Check the repo to make sure asset has already been added to it
        s = self.repo_table.select(and_(self.repo_table.c.repoID == repo_id, self.repo_table.c.scID == sec_center_id,
                                        self.repo_table.c.assetID == mist_id))
        repo_exists, row_id = self.check_exists(s)

        # Return the result of the query
        return repo_exists

    def insert_repo(self, repo_id, sec_center_id, repo_name, server_name, mist_id):
        # get the values needed to insert an asset into repo table
        values = {'repoID': repo_id, 'scID': sec_center_id, 'repoName': repo_name, 'serverName': server_name,
                  'assetID': mist_id}

        # insert the asset
        i = self.repo_table.insert()
        i.execute(values)

    def insert_asset(self, asset_dict):
        # Set the static variables
        fields = self.insert_fields
        asset_dict['state'] = 'R'
        sql_columns = "INSERT INTO Assets (assetID,"
        sql_values = " VALUES (DEFAULT,"

        for info in fields:
            if info is not 'repositoryID':
                sql_columns = sql_columns + info + ","
                sql_values += "'" + str(asset_dict[info]) + "',"

        # Clean up the sql statement and execute
        sql_columns = sql_columns[:-1] + ")"
        sql_values = sql_values[:-1] + ")"
        sql = sql_columns + sql_values
        self.db.execute(sql)

        results = self.db.execute("Select assetID from Assets ORDER BY assetID DESC LIMIT 1")
        last_id = 0
        for row in results:
            last_id = row[0]
        return last_id


def get_security_centers(master_dir, sc_file):
    # get all the directories in the Security Center Folder, and get sc info
    security_center_list = []
    directories = os.listdir(master_dir)
    for directory in directories:
        security_center = os.path.join(master_dir, directory)
        if os.path.isfile(os.path.join(security_center, sc_file)):
            server_file = open(os.path.join(security_center, sc_file), 'r')
            server_info = {'server': None, 'version': None, 'cert': None, 'key': None}

            for line in server_file:
                line = line.rstrip()
                if line.startswith('server='):
                    server_info['server'] = line.split('=')[1]
                elif line.startswith('version='):
                    server_info['version'] = line.split('=')[1]
            server_file.close()

            if server_info['server'] and server_info['version']:
                for pki_file in os.listdir(security_center):
                    if pki_file.endswith(".crt"):
                        server_info['cert'] = os.path.join(security_center, pki_file)
                    if pki_file.endswith(".key"):
                        server_info['key'] = os.path.join(security_center, pki_file)

                security_center_list.append(server_info)

    return security_center_list


def main():
    # Create log directory if it does not exist
    if not os.path.exists('/var/log/MIST'):
        os.makedirs('/var/log/MIST')
    log_file = '/var/log/MIST/asset_gathering.log'

    # fields needed from the asset dictionary returned from Security Center
    needed_fields = ['repositoryID', 'biosGUID', 'macAddress', 'ip', 'dnsName', 'lastAuthRun', 'lastUnauthRun',
                     'netbiosName', 'osCPE', 'mcafeeGUID']

    # create the database stuff that we need
    mist_database = Database(needed_fields)

    # get directories for all SC's to pull from
    master_directory = os.path.dirname(os.path.realpath(__file__)) + '/SecurityCenters'
    server_file_name = 'securitycenter.txt'
    sc_list = get_security_centers(master_directory, server_file_name)

    for security_center_dict in sc_list:
        # Log into that security center
        sc = SecurityCenter(security_center_dict['server'], security_center_dict['version'],
                            security_center_dict['cert'], security_center_dict['key'], log_file, mist_database)
        sc_id = sc.get_sc_id()
        sc_login = sc.login()

        if sc_login:
            # Getting all the repos names
            repo_dict = sc.get_repo_mapping()

            # Get a list of assets
            asset_list = sc.get_asset_list(needed_fields)

            # Loop through all assets
            for asset in asset_list:
                # Check to see if asset exists
                asset_exists, asset_id = mist_database.check_asset(asset)
                if asset_exists:
                    mist_database.update_asset(asset, asset_id)
                else:
                    asset_id = mist_database.insert_asset(asset)

                # Insert the repo if it is not there
                if asset_id != 0:
                    repo = mist_database.check_repo(asset_id, asset['repositoryID'], sc_id)
                    if not repo:
                        mist_database.insert_repo(asset['repositoryID'], sc_id, repo_dict[asset['repositoryID']],
                                                  security_center_dict['server'], int(asset_id))

if __name__ == "__main__":
    main()
