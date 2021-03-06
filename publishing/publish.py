import os
import base64
import optparse
import datetime
import zipfile
import shutil
import traceback
import requests
import mist_logging
import traceback

# External Classes
from opattr import OpAttributes 
from arf import ARF
from cve_asr import CVE_ASR
from iavm_asr import IAVM_ASR
from plugin_asr import Plugin_ASR
from benchmark_asr import Benchmark_ASR

# database stuff
import sys
sys.path.insert(0, '/opt/mist/database')
sys.path.insert(0, '/opt/mist/assets')
import config
from sqlalchemy import *
import pull_assets

def get_asset_list(asset_dict):
    asset_id_list = []
    for sc, repoDict in asset_dict.iteritems():
        for repo, assetList in repoDict.iteritems():
            for asset in assetList:
                if asset not in asset_id_list:
                    asset_id_list.append(asset)

    return asset_id_list


def get_assets(db, sc_repo_dict):
    # Make asset dictionary
    asset_dict = {}
    for sc, repoList in sc_repo_dict.iteritems():
        if sc not in asset_dict:
            asset_dict[sc] = {}
        for repo in repoList:
            if not repo in asset_dict[sc]:
                asset_dict[sc][repo] = []
            assets = db.execute("SELECT assetID FROM Repos WHERE scID = '" + sc + "' and repoID = " + str(repo))
            for asset in assets:
                asset_id = asset[0]
                asset_dict[sc][repo].append(asset_id)
    return asset_dict
        

def get_access(db, user_id):
    sc_dict = {}
    results = db.execute("SELECT scID, repoID FROM userAccess WHERE repoID > 0 and userID = " + str(user_id))
    for scRepo in results:
        if not scRepo[0] in sc_dict:
            sc_dict[scRepo[0]] = []
        sc_dict[scRepo[0]].append(scRepo[1])
    return sc_dict


def set_ref_number(db, user_id):
    # Look up the user in database so we can get username
    results = db.execute("Select username FROM mistUsers WHERE id = " + str(user_id))
    for result in results:
        if result:
            username = result[0]
        else:
            print "User does not exist\n"
            sys.exit(1)
    db.execute("INSERT INTO published VALUES (DEFAULT, '" + username + "', " + str(user_id) + ", DEFAULT)")
    current_ids = db.execute("Select id from published ORDER BY id DESC LIMIT 1")
    return_id = 1
    for currentID in current_ids:
        if currentID:
            return_id = currentID[0]
    return username, return_id


def insert_last_published(db, asset_dict, column):
    time_format = '%Y-%m-%d %H:%M:%S'
    current_time = datetime.datetime.now().strftime(time_format)
    for sc, repoAssetDict in asset_dict.iteritems():
        for repo, assetList in repoAssetDict.iteritems():
                results = db.execute("select scID, repoID FROM repoPublishTimes where scID = '" + sc +
                                     "' and repoID = " + str(repo))
                entry_exists = False
                for result in results:
                    if result:
                        entry_exists = True
                if entry_exists:
                    db.execute('update repoPublishTimes set ' + column + ' = "' + current_time + '" where repoID = ' +
                               str(repo) + ' and scID = "' + sc + '"')
                else:
                    db.execute('insert into repoPublishTimes (scID, repoID,' + column + ') VALUES ("' + sc + '", ' +
                               str(repo) + ', "' + current_time + '")')
     

def create_job(db, username):
    db.execute("INSERT INTO publishJobs (jobID, finishTime, status, userName) VALUES (DEFAULT, DEFAULT, 'running', '" +
               username + "')")
    results = db.execute("SELECT LAST_INSERT_ID()")
    for result in results:
        job_id = result[0]
    return job_id


def mark_assets_as_published(db, asset_id_list):
    for assetID in asset_id_list:
        db.execute("UPDATE Assets set state = 'P' where assetID = " + str(assetID))


def get_db():
    # create the database stuff that we need
    connect_string = 'mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST'
    ssl_args = {'ssl': {'cert': '/opt/mist/database/certificates/mist-interface.crt',
                        'key': '/opt/mist/database/certificates/mist-interface.key',
                        'ca': '/opt/mist/database/certificates/si_ca.crt'}}
    db = create_engine(connect_string, connect_args=ssl_args, echo=False)
    return db


def publish_error(db, error_message, job_id):
    # Remove the tmp folder
    error_message = error_message.replace("'", '"')
    sql = "UPDATE publishJobs set finishTime = DEFAULT, status = 'Error', filename = '%s' WHERE jobID = %s" % \
          (error_message, str(job_id))
    db.execute(sql)
    if os.path.exists('/opt/mist/publishing/tmp'):
        shutil.rmtree('/opt/mist/publishing/tmp')
    sys.exit(1)


def check_for_still_running(db, job_id, log):
    results = db.execute('SELECT status FROM publishJobs WHERE jobID = ' + str(job_id))
    status = None
    for result in results:
        status = result[0]

    if status == 'running':
        sql = "UPDATE publishJobs SET status='Error', filename = 'Error While Publishing' WHERE jobID = " + str(job_id)
        db.execute(sql)
        log.error_publishing(["MIST publishing failed for unknown reason\n"])


def get_file_chunk_size(db):
    sql = "SELECT chunkSize from mistParams"
    results = db.execute(sql)
    chunk_size = 19922944
    for result in results:
        chunk_size_mb = float(result[0])
    chunk_size = int((chunk_size_mb - 0.1) * 1000000)
    return chunk_size


def main():
    # Set parser options
    parser = optparse.OptionParser()
    parser.add_option('--user', action='store', dest="userID", type="int",
                      help="sets which assets to put in XMLs by user access")
    parser.add_option('--assets', action='store_true', dest='arf', default=False,
                      help="use this option to generate arf file")
    parser.add_option('--opattr', action='store_true', dest='opattr', default=False,
                      help="use this option to generate opattr file")
    parser.add_option('--cve', action='store_true', dest='cve', default=False,
                      help="use this option to generate CVE ASR")
    parser.add_option('--iavm', action='store_true', dest='iavm', default=False,
                      help="use this option to generate IAVM ASR")
    parser.add_option('--plugin', action='store_true', dest='plugin', default=False,
                      help="use this option to generate Plugin ID ASR")
    parser.add_option('--benchmark', action='store_true', dest='benchmark', default=False,
                      help="use this option to generate Benchmark ASR")
    parser.add_option('--all_asset', action='store_true', dest='allAsset', default=False,
                      help="use this option to publish all assets for a user instead of just changed or new ones")
    parser.add_option('--all_scan', action='store_true', dest='allScan', default=False,
                      help="use this option to publish all scan data per asset instead of just newly discovered data "
                           "since last published")
    parser.add_option('--all_opattr', action='store_true', dest='allOpattr', default=False,
                      help="use this option to publish all tags  per asset instead of just newly discovered data "
                           "since last published")
    parser.add_option('--site', action='store', dest="site", type="string", default=None,
                      help="sets the cmrs site to publish to, if this option is not selected it will save locally")
    parser.add_option('--cleartext', action='store_true', dest='cleartext', default=False,
                      help="publishes document in clear text to remote site")
    options, remainder = parser.parse_args()

    # if they did not use program right print help and exit
    if not options.userID:
        print "A user ID id required!\n"
        parser.print_help()
        sys.exit(1)
    if not options.site:
        print "A publishing site is required (enter 'localhost' if you want to save locally)"
        parser.print_help()
        sys.exit(1)
    else:
        user_id = options.userID
        site = options.site

    # Set up log constructor
    log = mist_logging.Log()

    # pull assets before publishing
    pull_assets.main()

    # Initialize jobID
    job_id = None

    # create database instance
    db = get_db()

    # Get file chunk size for publishcation docs
    file_chunk_size = get_file_chunk_size(db)

    try:
        # Keep track of who published which XML
        username, ref_number = set_ref_number(db, user_id)

        # Create New entry for job and get that jobs ID
        job_id = create_job(db, username)

        # Build the temp folder to hold building of XML
        temp_directory = '/opt/mist/publishing/tmp/' + str(ref_number)
        if not os.path.exists(temp_directory):
            os.makedirs(temp_directory)

        # Get Security Center and Repos associated with user
        repo_sc_dict = get_access(db, user_id)

        # Get assets for each security center in a dict by security center and repo
        asset_dict = get_assets(db, repo_sc_dict)

        # Get just the asset ids to build the arf and opattr files
        asset_id_list = get_asset_list(asset_dict)

        # Build the ARF
        if options.arf:
            arf = ARF(options.allAsset, file_chunk_size)
            build_attr = arf.buildXML(asset_id_list, ref_number, temp_directory)

        if options.opattr:
            # Build the Operational Attributes
            attr = OpAttributes(file_chunk_size, options.allOpattr)
            attr.buildXML(asset_id_list, ref_number, temp_directory)
	    insert_last_published(db, asset_dict, 'opattrLast') 

        # Build CVE ASR
        if options.cve:
            cve_asr = CVE_ASR(options.allScan, file_chunk_size)
            cve_asr.buildXML(asset_dict, ref_number, temp_directory)
            insert_last_published(db, asset_dict, 'cveLast')

        # Build IAVM ASR
        if options.iavm:
            iavm_asr = IAVM_ASR(options.allScan, file_chunk_size)
            iavm_asr.buildXML(asset_dict, ref_number, temp_directory)
            insert_last_published(db, asset_dict, 'iavmLast')

        # Build the PLugin ASR
        if options.plugin:
            plugin_asr = Plugin_ASR(options.allScan, file_chunk_size)
            plugin_asr.buildXML(asset_dict, ref_number, temp_directory)
            insert_last_published(db, asset_dict, 'pluginLast')

        # Build the Benchmark ASR
        if options.benchmark:
            benchmark_asr = Benchmark_ASR(options.allScan, file_chunk_size)
            benchmark_asr.buildXML(asset_dict, ref_number, temp_directory)
            insert_last_published(db, asset_dict, 'benchmarkLast')

        # Write Zip
        files = [f for f in os.listdir(temp_directory) if os.path.isfile(os.path.join(temp_directory, f))]
        if files:
            if site == 'localhost':
                #directory = '/opt/mist/frontend/app/MIST/Users/' + username
		directory = '/opt/mist/publishing/published_files/' + username
                if not os.path.exists(directory):
                    os.makedirs(directory)
                zip_file_name = 'MIST_' + str(ref_number) + '_' + \
                                datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.zip'
                zip_file = directory + '/' + zip_file_name
                zf = zipfile.ZipFile(zip_file, 'w')
                for mistFile in files:
                    zf.write(temp_directory + '/' + mistFile, mistFile)
                    if "arf" in mistFile:
                        mark_assets_as_published(db, asset_id_list)
                zf.close()

                # Mark the job as complete and give the name of file
                db.execute("UPDATE publishJobs set finishTime = DEFAULT, status = 'Completed', filename = '" +
                           zip_file_name + "' WHERE jobID = " + str(job_id))

                log.local_publish(username, zip_file_name)

            else:
                url = site
                headers = {'Accept': 'application/soap+xml', 'Content-Type': 'text/xml',
                           'SOAPAction': '"http://tempuri.org/ws/Notify"'}
                for mist_file in files:
                    # Injecting the needed SOAP envolope
                    with open(temp_directory + '/' + mist_file, 'r') as original_file:
                            data = original_file.readlines()
                    new_file = open(temp_directory + '/' + mist_file, 'w')
                    new_file.write(data[:1][0])
                    new_file.write('<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">\n')
                    new_file.write('<S:Body>\n')
                    for line in data[1:]:
                        new_file.write(line)
                    new_file.write('</S:Body>\n')
                    new_file.write('</S:Envelope>')
                    new_file.close()

                    cert_directory = '/opt/mist/publishing/certificates'
                    cert, key, ca = None, None, None
                    for cert_file in os.listdir(cert_directory):
                        if cert_file.endswith(".crt"):
                            cert = os.path.join(cert_directory, cert_file)
                        if cert_file.endswith(".key"):
                            key = os.path.join(cert_directory, cert_file)
                        if cert_file.endswith(".ca"):
                            ca = os.path.join(cert_directory, cert_file)
                    cert_and_key = (cert, key)
                    with open(temp_directory + '/' + mist_file) as payload:
                        requests.packages.urllib3.disable_warnings()

                        # Try connection and catch responses
                        if options.cleartext:
                            try:
                                resp = requests.post(url, data=payload, headers=headers, verify=ca)
                            except requests.exceptions.ConnectTimeout as e:
                                error = ["Error with  publishing to ", url, ": ", repr(e), "\n"]
                                log.error_publishing(error)
                                publish_error(db, "Connection Timeout", job_id)
                            except requests.exceptions.ConnectionError as e:
                                error = ["Error with  publishing to ", url, ": ", repr(e), "\n"]
                                log.error_publishing(error)
                                publish_error(db, "Could Not Connect: " + str(e), job_id)
                            except Exception, e:
                                error = ['Error with publishing to ', url, ": ", repr(e), "\n"]
                                log.error_publishing(error)
                                publish_error(db, "Error publishing to site " + str(e), job_id)
                        else:
                            try:
                                resp = requests.post(url, cert=cert_and_key, data=payload, headers=headers, verify=ca)
                            except requests.exceptions.SSLError as e:
                                error = ["Error with  publishing to ", url, ": ", repr(e), "\n"]
                                log.error_publishing(error)
                                publish_error(db, "SSL Error: " + str(e).split("SSL routines:", 1)[1], job_id)
                            except requests.exceptions.ConnectTimeout as e:
                                error = ["Error with  publishing to ", url, ": ", repr(e), "\n"]
                                log.error_publishing(error)
                                publish_error(db, "Connection Timeout", job_id)
                            except requests.exceptions.ConnectionError as e:
                                error = ["Error with  publishing to ", url, ": ", repr(e), "\n"]
                                log.error_publishing(error)
                                publish_error(db, "Could Not Connect: " + str(e), job_id)
                            except Exception, e:
                                error = ['Error with publishing to ', url, ": ", repr(e), "\n"]
                                log.error_publishing(error)
                                publish_error(db, "Error publishing to site " + str(e), job_id)

                        # Handle errors sent via the web
                        try:
                            resp.raise_for_status()
                        except requests.exceptions.HTTPError as e:
                            error = ["Error with  publishing to ", url, " site responded with: ", repr(e), "\n"]
                            log.error_publishing(error)
                            publish_error(db, "Web Error: " + str(e), job_id)

                    # Mark all the assets just published as 'P' in the Assets table
                    if "arf" in mist_file:
                        mark_assets_as_published(db, asset_id_list)

                # Mark the job as complete and give the name of file
                db.execute("UPDATE publishJobs set finishTime = DEFAULT, status = 'Completed', "
                           "filename = 'published to " + url + "' WHERE jobID = " + str(job_id))

                # Log successful publish
                log.web_publish(username, url)

            # Mark who published it
            db.execute("UPDATE published set timestamp = DEFAULT WHERE id = " + str(ref_number))

        else:
            # Mark the job as complete and leave filename field as null
            db.execute("UPDATE publishJobs set finishTime = DEFAULT, status = 'Completed' WHERE jobID = " + str(job_id))

        # Remove the tmp folder
        shutil.rmtree('/opt/mist/publishing/tmp')

        # Check if the job is still marked as running, which means it errored but was not caught
        if job_id:
            check_for_still_running(db, job_id, log)

    except Exception as e:
        print traceback.print_exc()
        error = ["Error with  publishing CMRS files: ", repr(e), "\n"]
        log.error_publishing(error)
        if job_id:
            error_string = "Error no publication generated"
            publish_error(db, error_string, job_id)
        # Remove the tmp folder
        shutil.rmtree('/opt/mist/publishing/tmp')


if __name__ == "__main__":
    main()
