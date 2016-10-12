import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import jsonschema
import datetime
import mist_logging
import base64

class SecurityCenter:

    def __init__(self, server, cert, key, port="443", ssl_verify=False, scheme='https'):
        self.ssl_verify = ssl_verify
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self.base_url = scheme + "://" + server + ":" + port + "/rest"
        self.server = server
        self.cert = cert
        self.log = mist_logging.Log()
        self.token = ''
        self.cookies = ''
        if cert and key:
            self.cert_group = (cert, key)
        else:
            self.cert_group = None

    def login(self, username=None, password=None):
        headers = {'Content-Type': 'application/json'}
        if username and password:
            values = {'username': username, 'password': password}
            resp = self.post("token", headers, values=values)
        else:
            resp = self.get("system", headers)
        if resp:
            self.token = resp.json()['response']['token']
            self.cookies = {'TNS_SESSIONID': resp.cookies['TNS_SESSIONID']}
            return True
        else:
            return False

    def get_sc_id(self):
        headers = {'Content-Type': 'application/json'}
        resp = self.get('system', headers)
        if resp:
            return resp.json()['response']['uuid']
        else:
            return None

    def get_repositories(self):
        headers = {'Content-Type': 'application/json', 'X-SecurityCenter': self.token}
        resp = self.get('repository', headers)
        if resp:
            return resp.json()['response']
        else:
            return None

    def get_asset_info(self, needed_fields):
        asset_list = []
        headers = {'Content-Type': 'application/json', 'X-SecurityCenter': self.token}
        resp = self.analysis(headers, 'vuln', 'sumip', 'cumulative', 0, 2147483647)
        
        if resp:
            # convert results dict to JSON data set
            results_json = json.dumps(resp['response']['results'])
            schema = open("/opt/mist/assets/modules/schema_sc5.json").read().strip()

            # use lazy validation to check data set validity
            try:
                v = jsonschema.Draft4Validator(json.loads(schema))
                for error in sorted(v.iter_errors(json.loads(results_json)), key=str):
                    error = ["Bad asset data from " + self.server + ": " + error.message]
                    self.log.error_publishing(error)
            except jsonschema.ValidationError as e:
                print "[ValidationError] %s" % e.message
                print results_json

            for asset in resp['response']['results']:
                asset_dict = {}
                # Get the info asset info we want
                for field in needed_fields:
                    if field == "repositoryID":
                        asset_dict[field] = asset['repository']['id']
                    else:
                        asset_dict[field] = asset[field]

                # If there is not unauth or auth run value changing to 0 since type is integer
                if asset_dict['lastAuthRun'] == '':
                    asset_dict['lastAuthRun'] = 0
                if asset_dict['lastUnauthRun'] == '':
                    asset_dict['lastUnauthRun'] = 0

                # Add the asset to out list
                asset_list.append(asset_dict)

        return asset_list

    def log_exception_error(self, e):
        if self.cert_group:
            error = ["Error connecting to ", self.server, " with cert " + str(self.cert) + ":", "Error: " + repr(e)]
            self.log.error_assets(error)
        else:
            error = ["Error connecting to ", self.server, " with credentials provided:", "Error: " + repr(e)]
            self.log.error_assets(error)

    def log_api_error(self, response):
        # This wil catch error messages from the API and log them
        if response.json()['error_code'] != 0:
                error = ['Error returned from API on server ', self.server, ': ', response.json()['error_msg']]
                self.log.error_assets(error)

    def analysis(self, headers, query_type, query_tool, query_source, query_start, query_end, query_filters=[]):
        query = {"type": query_type, "query": {"tool": query_tool, "type": query_type, "filters": [],
                                               "startOffset": query_start, "endOffset": query_end},
                 "sourceType": query_source}
        for query_filter in query_filters:
            data = {"filterName": query_filter[0], "operator": query_filter[1], "value": query_filter[2],
                    "type": query["type"]}
            query["query"]["filters"].append(data)
        response = self.post('analysis', headers, query)
        return response.json()

    def get(self, resource, headers, values=""):
        url = self.base_url + "/" + resource + "?" + values
        try:
            if self.cert_group:
                response = requests.get(url, headers=headers, cookies=self.cookies, verify=self.ssl_verify,
                                        cert=self.cert_group)
            else:
                response = requests.get(url, headers=headers, cookies=self.cookies, verify=self.ssl_verify)

            # Check For API errors:
            self.log_api_error(response)
            return response

        except Exception, e:
            self.log_exception_error(e)
            return None

    def post(self, resource, headers, values={}):
        url = self.base_url + "/" + resource
        try:
            if self.cert_group:
                response = requests.post(url, json.dumps(values), headers=headers, cookies=self.cookies,
                                         verify=self.ssl_verify, cert=self.cert_group)
            else:
                response = requests.post(url, json.dumps(values), headers=headers, cookies=self.cookies,
                                         verify=self.ssl_verify)
            # Check for API errors:
            self.log_api_error(response)

            return response

        except Exception, e:
            self.log_exception_error(e)
            return None
