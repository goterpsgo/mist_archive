
# -*- coding: utf-8 -*-
import requests
import os
import getpass
import optparse
import sys
import warnings


def save_output_xml(ids, base_url, user, password):
    # Code run to save the XML's outputed by API
    base_folder = "COAMS_XML"
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)

    # Run through each name type and download the all XML
    for name_type, type_id in ids.iteritems():
        print "Working On " + name_type

        # Create file on local system
        output_file = base_folder + '/' + name_type + '.xml'

        # Download the XML from the coams API (Change Auth to whatever works in product)
        warnings.filterwarnings("ignore")
        with open(output_file, 'wb') as handle:
            url = base_url + str(type_id)
            if user and password:
                r = requests.get(url, auth=(user, password), verify=False, stream=True)
            else:
                r = requests.get(url, verify=False, stream=True)
            if r.status_code == "200":
                print "OK"
            else:
                print "No Data Retrived"
            for block in r.iter_content(1024):
                handle.write(block)

if __name__ == "__main__":

    # Set parser options
    parser = optparse.OptionParser()
    parser.add_option('--site', action='store', dest="site", type="string", help="DNS name of site the COAMS API is at")
    parser.add_option('--user', action='store', dest="user", type="string", default='None',
                      help="Name of user to authenticate to COAMS API")
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

    # Base information about COAMS API
    base_url = "https://" + options.site + "/COAMS/Services/NameDistro?nameTypeKey="
    IDs = {'Location': 1, 'Organization': 2, 'MAC': 3, 'Confidentiality Level': 4, 'FIPS Confidentiality Level': 5,
           'FIPS Availability Level': 6, 'FIPS Integrity Level': 7, 'DOD Network': 8, 'CND Service Provider': 9,
           'Classification': 10, 'NonDOD Network': 11, 'System': 12, 'CCSD': 13, 'NonDoD Circuit ID': 14,
           'Network Zone': 15, 'Function': 16, 'Permission': 17, 'Role': 18, 'Data Publisher': 19,
           'Enterprise Application Roles': 20}

    # Get and Save the ouput XML from API Call
    save_output_xml(IDs, base_url, user, password)
