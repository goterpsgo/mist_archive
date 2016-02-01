
# -*- coding: utf-8 -*-
import requests
import os
import getpass
import optparse
import sys
import warnings

def saveOutputXML(IDs, baseURL, user, password):
        #Code run to save the XML's ouputed by API
        baseFolder = "COAMS_data/XML"
        if not os.path.exists(baseFolder):
                os.makedirs(baseFolder)

        #Run through each name type and download the all XML
        for nameType, typeID in IDs.iteritems():
                print "Working On " + nameType

                #Create file on local system
                outputFile = baseFolder+'/' + nameType + '.xml'

                #Download the XML from the coams API (Change Auth to whatever works in product)
		warnings.filterwarnings("ignore")
                with open(outputFile, 'wb') as handle:
                        URL = baseURL + str(typeID)
			if user and password:
                       		r = requests.get(URL, auth=('user1', 'Qwerty1@'), verify=False, stream=True)
			else:
				r = requests.get(URL, verify=False, stream=True)
			if r:
				print "OK"
			else:
				print "No Data Retrived"
                        for block in r.iter_content(1024):
                                handle.write(block)

if __name__ == "__main__":

	#Set parser options
	parser = optparse.OptionParser()
	parser.add_option('--site', action='store', dest="site", type="string", help="DNS name of site the COAMS API is at")
	parser.add_option('--user', action='store', dest="user", type="string", default='None', help="Name of user to authenticate to COAMS API")
	options, remainder = parser.parse_args()

	if not options.site:
		print "\nYou must enter a site for COAMS API!\n"
		parser.print_help()
		sys.exit(1)
	
	if options.user == 'None':
		user = None
		password = None
	else:
		user = options.user
		password = getpass.getpass("\nEnter the password: ")

	#Base information about COAMS API 
	baseURL = "https://" + options.site + "/COAMS/Services/NameDistro?nameTypeKey="
	IDs = {'Location':1, 'Organization':2,'MAC':3,'Confidentiality Level':4,'FIPS Confidentiality Level':5,
	'FIPS Availability Level':6,'FIPS Integrity Level':7,'DOD Network':8,'CND Service Provider':9,'Classification':10,
	'NonDOD Network':11,'System':12,'CCSD':13,'NonDoD Circuit ID':14,'Network Zone':15, 'Function':16,'Permission':17,'Role':18,'Data Publisher':19,
	'Enterprise Application Roles':20}

	# Get and Save the ouput XML from API Call
	saveOutputXML(IDs, baseURL, user, password)
