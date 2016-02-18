
import httplib
import urllib2
import urllib
import json
import os
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
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        if self.cert:
            return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)
        else:
            return httplib.HTTPSConnection(host)


class SecurityCenter:
    
    def __init__(self, server, log_file, cert=None, key=None):
        self.server = server
        self.cert = cert
        self.key = key
        self.log = log_file
        self.token = ''
        self.cookie = ''

    def login(self, username=None, password=None):
        if self.cert:
            resp = self.connect('system', 'init')
        else:
            data = {'username': username, 'password': password}
            resp = self.connect('auth', 'login', sc_input=data)

        self.token, self.cookie = resp['token'], resp['sessionID']

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
