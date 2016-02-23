import requests
import json
import datetime


class SecurityCenter:

    def __init__(self, server, log_file, cert=None, key=None, port="443", ssl_verify=False, scheme='https'):
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

    def get_ip_info(self, data):
        headers = {'Content-Type': 'application/json', 'X-SecurityCenter': self.token}
        values = "fields=pluginSet,policyName,lastAuthRun,biosGUID,mcafeeGUID&ip=" + str(data['ip'])
        results = self.get('ipInfo', headers, values)
        return results.json()['response']

    def query(self, type, tool, data):
        headers = {'Content-Type': 'application/json', 'X-SecurityCenter': self.token}
        results = self.analysis(headers, type, data['tool'], data['sourceType'], data['startOffset'], data['endOffset'],
                                data['filters'])
        return results['response']

    def analysis(self, headers, query_type, query_tool, query_source, query_start, query_end, query_filters=[]):
        query = {"type": query_type, "query": {"tool": query_tool, "type": query_type, "filters": query_filters,
                                               "startOffset": query_start, "endOffset": query_end},
                 "sourceType": query_source}
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
