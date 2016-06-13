
import httplib
import urllib2
import urllib
import json
import mist_logging


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
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        if self.cert:
            return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)
        else:
            return httplib.HTTPSConnection(host)


class SecurityCenter:
    
    def __init__(self, server, cert=None, key=None):
        self.server = server
        self.cert = cert
        self.key = key
        self.log = mist_logging.Log()
        self.token = ''
        self.cookie = ''

    def login(self, username=None, password=None):
        if self.cert:
            resp = self.connect('system', 'init')
        else:
            data = {'username': username, 'password': password}
            resp = self.connect('auth', 'login', sc_input=data)

        self.token, self.cookie = resp['token'], resp['sessionID']

    def get_ip_info(self, data):
        results = self.connect('vuln', 'getIP', data)
        return results['records'][0]

    def query(self, module, action, data):
        results = self.connect(module, action, data)
        return results

    def connect(self, module, action, sc_input={}):
        # Set parameters for query against SC
        data = {'module': module,
                'action': action,
                'input': json.dumps(sc_input),
                'token': self.token,
                'request_id': 1}
        # Set URL for server which will be used
        url = "https://" + self.server + '/request.php'
        try:
            # bulid opener toi connect to SC
            if self.cert:
                opener = urllib2.build_opener(HTTPSClientAuthHandler(self.key, self.cert))
            else:
                opener = urllib2.build_opener(HTTPSClientAuthHandler())
            # Add TNS session ID if we alredy have it
            opener.addheaders.append(('Cookie', 'TNS_SESSIONID=' + self.cookie))
            # Connect To SC and gather data
            resp = opener.open(url, urllib.urlencode(data))
            # Read data which is returned in json format
            content = json.loads(resp.read())

            # This wil catch error messages from the API and log them
            if content['error_code'] != 0:
                error = ['Error returned from API on server ', self.server, ': ', content['error_msg']]
                self.log.error_publishing(error)

            return content['response']

        except Exception, e:
            # If we have error connecting log it to file
            if self.cert:
                error = ["Error while connect to ", self.server, " with cert ", str(self.cert), ": ", repr(e)]
                self.log.error_publishing(error)
            else:
                error = ["Error connecting to ", self.server, " with credentials provided: ", repr(e)]
                self.log.error_publishing(error)
            return None

