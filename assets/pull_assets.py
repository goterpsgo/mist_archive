
import os
import base64
import mist_logging

# databse stuff
import sys
sys.path.insert(0, '/opt/mist/database')
import config
from sqlalchemy import *

# Path for SC module
from modules import securitycenter4
from modules import securitycenter5


class SecurityCenter:

    def __init__(self, hostname, version, cert, key):
        self.host = hostname
        self.cert = cert
        self.key = key
        self.version = version
        if version == '4':
            self.sc = securitycenter4.SecurityCenter(self.host, self.cert, self.key)
        elif version == '5':
            self.sc = securitycenter5.SecurityCenter(self.host, self.cert, self.key)

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
        self.log = mist_logging.Log()

    def execute_sql(self, sql):
        try:
            results = self.db.execute(sql)
            return results
        except Exception, e:
            error = ['Database Error: ', str(e)]
            self.log.error_assets(error)

    def check_exists(self, sql):
        # Execute SQL query
        rs = self.execute_sql(sql)
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
        self.execute_sql(sql)

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

        # Log the event
        sql = "SELECT COUNT(*) FROM Repos WHERE repoName = '%s' and serverName='%s'" % (repo_name, server_name)
        results = self.execute_sql(sql)
        count = 0
        for result in results:
            count = result[0]
        if count == 1:
            self.log.add_repo(repo_name, server_name)

    def update_repo(self, repo_dict, sec_center_id):
        for repo_id, repo_name in repo_dict.iteritems():
            sql = "SELECT id FROM Repos WHERE repoID=" + str(repo_id) + " and scID = '" + str(sec_center_id) + "'"
            results = self.execute_sql(sql)
            ids = []
            for result in results:
                ids.append(result[0])

            if ids:
                for id in ids:
                    sql = "UPDATE Repos SET repoName='" + repo_name + "' WHERE id = " + str(id)
                    self.execute_sql(sql)

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
        self.execute_sql(sql)

        results = self.execute_sql("Select assetID from Assets ORDER BY assetID DESC LIMIT 1")
        last_id = 0
        for row in results:
            last_id = row[0]

        # Log event
        self.log.add_asset(last_id)
        return last_id

    def get_mist_repo_mapping(self, sc_id):
        sql = "SELECT DISTINCT repoID, repoName FROM Repos WHERE scID = '" + sc_id + "'"
        results = self.execute_sql(sql)
        mist_repo_mapping = {}
        for result in results:
            mist_repo_mapping[result[0]] = result[1]
        return mist_repo_mapping

    def get_unique_repo_assets(self, repo_id, sc_id):
        unique_assets = []
        sql = "SELECT assetID FROM Repos WHERE repoID=%s and scID='%s'" % (str(repo_id), sc_id)
        results = self.execute_sql(sql)
        assets_in_repo = []
        for result in results:
            assets_in_repo.append(result[0])
        for asset in assets_in_repo:
            sql = "SELECT EXISTS(SELECT id FROM Repos WHERE (Not(scID) = '%s' or Not(repoID)= %s) and assetID =%s)" % \
                  (sc_id, str(repo_id), str(asset))
            results = self.execute_sql(sql)
            for result in results:
                if result[0] == 0:
                    unique_assets.append(asset)
        return unique_assets

    def remove_repo(self, repo, sc_id):
        # Log the event
        sql = "SELECT DISTINCT serverName, repoName FROM Repos WHERE repoID = %s and scID='%s'" % (str(repo), sc_id)
        results = self.execute_sql(sql)
        server = ''
        repo_name = ''
        for result in results:
            server = result[0]
            repo_name = result[1]
        self.log.remove_repo(repo_name, server)

        sql_repo = "DELETE FROM Repos WHERE repoID = %s and scID='%s'" % (str(repo), sc_id)
        sql_tag = "DELETE FROM taggedRepos WHERE repoID = %s and scID='%s'" % (str(repo), sc_id)
        sql_user = "DELETE FROM userAccess WHERE repoID = %s and scID='%s'" % (str(repo), sc_id)
        sql_publish = "DELETE FROM repoPublishTimes WHERE repoID = %s and scID='%s'" % (str(repo), sc_id)
        self.execute_sql(sql_repo)
        self.execute_sql(sql_tag)
        self.execute_sql(sql_user)
        self.execute_sql(sql_publish)

        return repo_name, server

    def remove_asset(self, asset):
        sql_asset = "DELETE FROM Assets WHERE assetID = %s" % (str(asset))
        sql_tag = "DELETE FROM taggedAssets WHERE assetID = %s" % (str(asset))
        self.execute_sql(sql_asset)
        self.execute_sql(sql_tag)

        # Log the event
        self.log.remove_asset(asset)

    def update_removed_repos(self, repo_name, server_name):
        sql = "INSERT INTO removedRepos (repoName, serverName, removeDate, ack) VALUES ('%s','%s',DEFAULT,'No')" % \
              (repo_name, server_name)
        self.execute_sql(sql)


class RepoRemoval:

    def __init__(self, sc_repo_mapping, sc_id, mist_db):
        self.sc_repo_mapping = sc_repo_mapping
        self.sc_id = sc_id
        self.mist_db = mist_db

    def clean(self):
        repos_to_be_removed = self.compare_repo_list()

        assets_to_be_removed = []
        for repo in repos_to_be_removed:
            unique_assets = self.mist_db.get_unique_repo_assets(repo, self.sc_id)
            for asset in unique_assets:
                if asset not in assets_to_be_removed:
                    assets_to_be_removed.append(asset)

        server_name, repo_name_list = self.remove_repos(repos_to_be_removed)
        self.remove_assets(assets_to_be_removed)
        self.update_removed_repos(server_name, repo_name_list)

    def compare_repo_list(self):
        repos_to_be_removed = []
        mist_repo_mapping = self.mist_db.get_mist_repo_mapping(self.sc_id)
        for repo_id in mist_repo_mapping:
            if str(repo_id) not in self.sc_repo_mapping:
                repos_to_be_removed.append(repo_id)
        return repos_to_be_removed

    def remove_repos(self, repo_list):
        repo_name_list = []
        server_name = ''
        for repo in repo_list:
            repo_name, server = self.mist_db.remove_repo(repo, self.sc_id)
            repo_name_list.append(repo_name)
            server_name = server
        return server_name, repo_name_list

    def remove_assets(self, asset_list):
        for asset in asset_list:
            self.mist_db.remove_asset(asset)

    def update_removed_repos(self, server_name, repo_name_list):
        for repo_name in repo_name_list:
            self.mist_db.update_removed_repos(repo_name, server_name)


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


def is_asset(asset):
    unique_asset = False
    if asset['biosGUID']:
        unique_asset = True
    if asset['dnsName']:
        unique_asset = True
    if asset['netbiosName']:
        unique_asset = True
    if asset['ip'] and asset['macAddress']:
        unique_asset = True

    return unique_asset


def main():

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
                            security_center_dict['cert'], security_center_dict['key'])
        sc_id = sc.get_sc_id()
        sc_login = sc.login()

        if sc_login:
            # Getting all the repos names
            repo_dict = sc.get_repo_mapping()

            # Update Repos that already exists
            mist_database.update_repo(repo_dict, sc_id)

            # Remove Repos that dont exist in the SC anymore
            repo_removal = RepoRemoval(repo_dict, sc_id, mist_database)
            repo_removal.clean()

            # Get a list of assets
            asset_list = sc.get_asset_list(needed_fields)

            # Loop through all assets
            for asset in asset_list:
                # Check to see if asset has enough fields to be added
                if not is_asset(asset):
                    continue
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
