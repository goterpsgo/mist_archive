
import requests
import json
import datetime


class SecurityCenter:

    def __init__(self, server, cert, key, log_file, port="443", ssl_verify=False, scheme='https'):
        self.ssl_verify = ssl_verify
        self.base_url = scheme + "://" + server + ":" + port + "/rest"
        self.cert = cert
        self.log = log_file
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
            return response

        except Exception, e:
            f = open(self.log, 'a+')
            if self.cert_group:
                f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " Error connecting with cert " +
                        str(self.cert) + ":\n")
                f.write("     Error: " + str(e) + "\n")
            else:
                f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') +
                        " Error connecting with credentials provided\n")
                f.write("     Error: " + str(e) + "\n")
                f.close()
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
            return response
        except Exception, e:
            f = open(self.log, 'a+')
            if self.cert_group:
                f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " Error connecting with cert " +
                        str(self.cert) + ":\n")
                f.write("     Error: " + str(e) + "\n")
            else:
                f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') +
                        " Error connecting with credentials provided\n")
                f.write("     Error: " + str(e) + "\n")
                f.close()
            return None

