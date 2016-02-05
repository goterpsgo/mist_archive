
import httplib
import urllib2
import urllib
import json
import datetime


class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    '''Class to handle SSL certificate authentication.'''
    def __init__(self, key=None, cert=None):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        # Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.get_connection, req)

    def get_connection(self, host, timeout=300):
        if self.cert:
            return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)
        else:
            return httplib.HTTPSConnection(host)


class SecurityCenter:
    
    def __init__(self, server, cert, key, log_file):
        self.server = server
        self.cert = cert
        self.key = key
        self.log = log_file
        self.token = ''
        self.cookie = ''

    def login(self, username=None, password=None):
        if username and password:
            data = {'username': username, 'password': password}
            resp = self.connect('auth', 'login', input=data)
        else:
            resp = self.connect('system', 'init')

        if resp:
            self.token, self.cookie = resp['token'], resp['sessionID']
            return True
        else:
            return False

    def get_sc_id(self):
        resp = self.connect('system', 'init')
        if resp:
            return resp['uuid']
        else:
            return None

    def get_repositories(self):
        resp = self.connect('group', 'init')
        if resp:
            return resp['repositories']
        else:
            return None

    def get_asset_info(self, needed_fields):
        asset_list = []
        filters = {'tool': 'sumip','sourceType': 'cumulative', 'startOffset': 0, 'endOffset': 2147483647}
        resp = self.connect('vuln', 'query', filters)
        if resp:
            for asset in resp['results']:
                asset_dict = {}
                # Get the info asset info we want
                for field in needed_fields:
                    asset_dict[field] = asset[field]

                # If there is not unauth or auth run value changing to 0 since type is integer
                if asset_dict['lastAuthRun'] == '':
                    asset_dict['lastAuthRun'] = 0
                if asset_dict['lastUnauthRun'] == '':
                    asset_dict['lastUnauthRun'] = 0

                # Add the asset to out list
                asset_list.append(asset_dict)

        return asset_list

    def connect(self, module, action, input={}):
        # Set parameters for query against SC
        data = {'module': module,
                'action': action,
                'input': json.dumps(input),
                'token': self.token,
                'request_id': 1}
        
        # Set URL for server which will be used
        url = "https://" + self.server + '/request.php'

        try:
            # build opener toi connect to SC
            if self.cert:
                opener = urllib2.build_opener(HTTPSClientAuthHandler(self.key, self.cert))
            else:
                opener = urllib2.build_opener(HTTPSClientAuthHandler())

            # Add TNS session ID if we already have it
            opener.addheaders.append(('Cookie', 'TNS_SESSIONID=' + self.cookie))
            # Connect To SC and gather data
            resp = opener.open(url, urllib.urlencode(data))
            # Read data which is returned in json format
            content = json.loads(resp.read())

            return content['response']
            
        except Exception, e:
            # If we have error connecting log it to file
            f = open(self.log, 'a+')
            if self.cert:
                f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " Error connecting with cert " +
                        str(self.cert) + ":\n")
                f.write("     Error: " + str(e) + "\n")
            else:
                f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') +
                        " Error connecting with credentials provided\n")
                f.write("     Error: " + str(e) + "\n")
                f.close()
            return None
