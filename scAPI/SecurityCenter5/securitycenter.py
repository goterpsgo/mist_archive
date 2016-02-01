import json
import requests
import datetime

class SecurityCenter:

	def __init__(self, host, logFile, cert=None, key=None, port="443", ssl_verify=False, scheme='https'):
		self.ssl_verify = ssl_verify
		self.base_url = scheme + "://" + host + ":" + port + "/rest"
		self.cert = cert
		if cert and key:
			self.cert_group = (cert, key)
		self.log = logFile
	
	def get(self, resource, headers, cookies, values=""):
		url = self.base_url + "/" + resource + "?" + values
		try:
			if self.cert:
				response = requests.get(url, headers=headers, cookies=cookies, verify=self.ssl_verify, cert=(self.cert_group))
			else:
				response = requests.get(url, headers=headers, cookies=cookies, verify=self.ssl_verify)
			return response
		except Exception, e:
			#If we have error connecting log it to file
                        f = open(self.log, 'a+')
			if self.cert:
                                f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " Error connecting with cert " + str(self.cert_group) + ":\n")
                                f.write("     Error: " + str(e) + "\n")
                        else:
                                f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " Error connecting with credentials provided\n")
                                f.write("     Error: " + str(e) + "\n")
                        f.close()
                        return None

	def post(self, resource, headers, cookies, values):
		url = self.base_url + "/" + resource
		try:
			if self.cert:
				response = requests.post(url, json.dumps(values), headers=headers, cookies=cookies, verify=self.ssl_verify, cert=(self.cert_group))
			else:
                                response = requests.post(url, json.dumps(values), headers=headers, cookies=cookies, verify=self.ssl_verify)
			return response
		except Exception, e:
                        #If we have error connecting log it to file
                        f = open(self.log, 'a+')
			if self.cert:
                        	f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " Error connecting with cert " + str(self.cert_group) + ":\n")
                        	f.write("     Error: " + str(e) + "\n")
			else:
				f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " Error connecting with credentials provided\n")
                                f.write("     Error: " + str(e) + "\n")
                        f.close()
                        return None
	
	def analysis(self, headers, cookies, qType, qTool, qSource, qStart, qEnd, qFilters=""):
		query = {"type": qType, "query": {"tool":qTool, "type":qType, "filters":[], "startOffset": qStart, "endOffset": qEnd}, "sourceType":qSource}
		for f in qFilters:
                	d = {"filterName": f[0], "operator": f[1], "value": f[2], "type": query["type"]}
                	query["query"]["filters"].append(d)
		response = self.post('analysis', headers, cookies, query)
		if response:
			return response.json()	
		else:
			return None
