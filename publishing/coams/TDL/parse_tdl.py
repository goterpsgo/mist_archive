import sys
import os
import optparse
import urllib2
import base64

#database stuff
sys.path.insert(0, '/opt/mist/database')
import config
from sqlalchemy import *

#Extra non native modules
from modules import xmltodict


def parse_xml(filename):
    with open(filename) as xml_file:
        xml_dict = xmltodict.parse(xml_file.read())
    return xml_dict

def extract_uri_components(uri):
    category_rollup_uri = uri.split("?")[1]
    category_rollup = category_rollup_uri.split("&")
    category = category_rollup[0].split("=")[1]
    category = urllib2.unquote(category.decode('utf8'))
    rollup = category_rollup[1].split("=")[1]
    rollup = urllib2.unquote(rollup.decode('utf8'))
    return category, rollup

def parse_definition(definition):
    definition_dictionary = {'name':'','title':'', 'description':'', 'required':'N', 'defaultValue':'', 'type':'', 'cardinality':0, 'version':'', 'rollup':'', 'category':''}
    for key, value in definition.iteritems():
        if key == "dataSource":
            type_def, type_def_data = value.popitem()
            definition_dictionary['type'] = type_def
            for attribute, attribute_data in type_def_data.iteritems():
                if attribute == "@uri":
                    uri = attribute_data
            category, rollup = extract_uri_components(uri)
            definition_dictionary['category'] = category
            definition_dictionary['rollup'] = rollup
        elif key == "notRequired":
            definition_dictionary['required'] = 'N'
        elif key == "required":
            definition_dictionary['required'] = 'Y'
            default_key, default_value = value.popitem()
            definition_dictionary[default_key] = default_value
        else:
            definition_dictionary[key] = value
    return definition_dictionary


def print_definitions(db, definitions_dict):
    # This will parse the TDL and print out the different definitions
    for definition in definitions_dict['TagCatalog']['TagDefinitions']['TagDefinition']:
        definition_dictionary = parse_definition(definition)
        rollup_exists = check_for_rollup(db, definition_dictionary)
        if rollup_exists:
            for key, value in definition_dictionary.iteritems():
                print key, ":", value
            print "\n"

def check_definition(db, definition_name):
    results = db.execute('SELECT id FROM tagDefinition WHERE name = "' + definition_name + '"')
    def_id = None
    for result in results:
        def_id = result[0]
    return def_id

def check_for_rollup(db, def_dict):
    results = db.execute('SELECT id FROM Tags WHERE category = "' + def_dict['category'] + '" and rollup = "' + def_dict['rollup'] + '"')
    rollup_exists = False
    for result in results:
        if result > 1:
            rollup_exists = True
    return rollup_exists

def insert_definitions(db, definitions_dict):
    #This will parse out all the neccassary info and place it into the database
    for definition in definitions_dict['TagCatalog']['TagDefinitions']['TagDefinition']:
        def_dict = parse_definition(definition)
        rollup_exists = check_for_rollup(db, def_dict)
        definition_id = check_definition(db, def_dict['name'])
        k = ['name', 'title', 'description', 'required', 'defaultValue', 'type', 'cardinality', 'version', 'rollup', 'category']
        if rollup_exists:
            if definition_id:
                #update the existing name
                sql = "UPDATE tagDefinition SET title = %s, description = %s, required = %s, defaultValue = %s, type = %s, cardinality = %s, version = %s, rollup = %s, category = %s WHERE id = " + str(definition_id)
                db.execute(sql, (def_dict[k[1]], def_dict[k[2]], def_dict[k[3]], def_dict[k[4]], def_dict[k[5]], def_dict[k[6]], def_dict[k[7]], def_dict[k[8]], def_dict[k[9]]))
            else:
                #insert new definition
                sql = "INSERT INTO tagDefinition VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, DEFAULT)"
                db.execute(sql, (def_dict[k[0]], def_dict[k[1]], def_dict[k[2]], def_dict[k[3]], def_dict[k[4]], def_dict[k[5]], def_dict[k[6]], def_dict[k[7]], def_dict[k[8]], def_dict[k[9]]))

if __name__ == "__main__":

    #set up options for program
    parser = optparse.OptionParser()
    parser.add_option('--filename', action='store', dest="xml_file", help="name of the file in the TDL_files folder you wish ingest")
    parser.add_option('--test', action='store_true', dest='test_parse', default=False, help="prints out TDL info instead of databasing it")
    options, remainder = parser.parse_args()

    #if they did not use program right print help and exit
    if not options.xml_file:
        parser.print_help()
        sys.exit(1)
    else:
        definitions_dict = parse_xml(options.xml_file)
        #create the database stuff that we need
        connect_string = 'mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST'
        ssl_args = {'ssl':{'cert':'/opt/mist/database/certificates/mist-interface.crt', 'key':'/opt/mist/database/certificates/mist-interface.key', 'ca':'/opt/mist/database/certificates/si_ca.crt'}}
        db = create_engine(connect_string, connect_args=ssl_args, echo=False)
        #db.echo = True
        metadata = MetaData(db)
        if options.test_parse:
            #print what will be in the inser to db, instead of putting it in the db
            print_definitions(db, definitions_dict)
        else:
            #Insert the tag definition
            insert_definitions(db, definitions_dict)




