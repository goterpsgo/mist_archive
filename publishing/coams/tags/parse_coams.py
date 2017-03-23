# Regular imports
import os
import sys
import base64

# Import database config and sqlalchemy
#database stuff
sys.path.insert(0, '/opt/mist/database')
import config
from sqlalchemy import *

# Import XML parser module
from modules import xmltodict


class Modification:

    def __init__(self, category, default_rollup):
        self.category = category
        self.default_rollup = default_rollup

    def get_details(self, mod):
        if mod['@active'] == 'true':
            if '@superiorNameID' in mod:
                parent_id = mod['@superiorNameID']
            else:
                parent_id = 'Top'
            details = {'dname': mod['@dName'], 'hname': mod['@hName'], 'parentID': parent_id, 'category': self.category}
            return details
        else:
            return None

    def modification(self, modifications):
        modification_dict = {self.default_rollup: {}}
        if isinstance(modifications, list):
            for mod in modifications:
                details = self.get_details(mod)
                if details:
                    modification_dict[self.default_rollup][mod['@nameID']] = details
        else:
            details = self.get_details(modifications)
            if details:
                    modification_dict[self.default_rollup][modifications['@nameID']] = details
        return modification_dict

    def functional_modification(self, functional_mods):
        functional_dict = {}
        if isinstance(functional_mods, list):
            for mod in functional_mods:
                rollup = mod['@rollupType']
                details = self.get_details(mod)
                if details:
                    if rollup not in functional_dict:
                        functional_dict[rollup] = {}
                    functional_dict[rollup][mod['@nameID']] = details
        else:
            rollup = functional_mods['@rollupType']
            details = self.get_details(functional_mods)
            if details:
                    if rollup not in functional_dict:
                        functional_dict[rollup] = {}
                    functional_dict[rollup][functional_mods['@nameID']] = details
        return functional_dict

    def parse(self, xml_dict):
        # look at each one and see if there are tags
        functional_mod_dict, mod_dict = None, None
        for tag, attributes in xml_dict.iteritems():
            if tag == 'ndl:FunctionalMod':
                functional_mod_dict = self.functional_modification(attributes)
            elif tag == 'ndl:Modification':
                mod_dict = self.modification(attributes)
        return mod_dict, functional_mod_dict


class Migration:

    def __init__(self, category, default_rollup):
        self.category = category
        self.default_rollup = default_rollup

    def migration(self, migrations):
        migration_dict = {}
        if isinstance(migrations, list):
            for migration in migrations:
                details = {'newID': migration['@newID'], 'rollup': self.default_rollup, 'category': self.category}
                migration_dict[migration['@nameID']] = details
        else:
            details = {'newID': migrations['@newID'], 'rollup': self.default_rollup, 'category': self.category}
            migration_dict[migrations['@nameID']] = details
        return migration_dict

    def functional_migration(self, functional_migrations):
        functional_migrations_dict = {}
        if isinstance(functional_migrations, list):
            for migration in functional_migrations:
                details = {'newID': migration['@migrateTo'], 'rollup': migration['@rollupType'],
                           'category': self.category}
                functional_migrations_dict[migration['@nameID']] = details
        else:
            details = {'newID': functional_migrations['@migrateTo'], 'rollup': functional_migrations['@rollupType'],
                       'category': self.category}
            functional_migrations_dict[functional_migrations['@nameID']] = details
        return functional_migrations_dict

    def parse(self, xml_dict):
        # look at each one and see if
        functional_migration_dict, migration_dict = None, None
        for tag, attributes in xml_dict.iteritems():
            if tag == 'ndl:FunctionalMigration':
                functional_migration_dict = self.functional_migration(attributes)
            elif tag == 'ndl:Migration':
                migration_dict = self.migration(attributes)
        return migration_dict, functional_migration_dict


class Database:

    def __init__(self):
        connect_string = 'mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST'
        ssl_args = {'ssl': {'cert': '/opt/mist/database/certificates/mist-interface.crt',
                           'key': '/opt/mist/database/certificates/mist-interface.key',
                           'ca': '/opt/mist/database/certificates/si_ca.crt'}}
        self.db = create_engine(connect_string, connect_args=ssl_args, echo=False)

    def insert_modifications(self, rollup_dictionary):
        for rollup, tag_dictionary in rollup_dictionary.iteritems():
            for name_id, details in tag_dictionary.iteritems():
                sql = "SELECT id FROM Tags WHERE nameID = %s AND category = %s AND rollup = %s"
                tag_id = None
                results = self.db.execute(sql, (name_id, details['category'], rollup))
                for result in results:
                    tag_id = result[0]

                if tag_id:
                    sql = "UPDATE Tags SET nameID = %s, category = %s, rollup = %s, parentID = %s, hname = %s, " \
                          "dname = %s, tagType = %s, depth = %s WHERE id = " + str(tag_id)
                else:
                    sql = "INSERT INTO Tags VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s)"
                self.db.execute(sql, (name_id, details['category'], rollup, details['parentID'],
                                      details['hname'], details['dname'], details['tagType'], str(details['depth'])))

    def insert_migrations(self, tag_dictionary):
        for name_id, details in tag_dictionary.iteritems():
            # Check if the tag id exists:
            sql_tags = "SELECT id FROM Tags WHERE nameID = %s AND category = %s AND rollup = %s"
            sql_assets = "SELECT id FROM taggedAssets WHERE tagID = %s AND category = %s AND rollup = %s"
            sql_repos = "SELECT id FROM taggedRepos WHERE tagID = %s AND category = %s AND rollup = %s"
            sql_commands = {'tags': sql_tags, 'assets': sql_assets, 'repos': sql_repos}
            tag_ids = {'tags': None, 'assets': None, 'repos': None}
            for key, sql in sql_commands.iteritems():
                results = self.db.execute(sql, (name_id, details['category'], details['rollup']))
                for result in results:
                    tag_ids[key] = result[0]

            # If it exists migrate it
            if tag_ids['tags']:
                sql = "UPDATE Tags SET nameID = %s WHERE id = " + str(tag_ids['tags'])
                self.db.execute(sql, (details['newID']))
            if tag_ids['assets']:
                sql = "UPDATE taggedAsset SET tagID = %s WHERE id = " + str(tag_ids['tags'])
                self.db.execute(sql, (details['newID']))
            if tag_ids['repos']:
                sql = "UPDATE taggedRepos SET tagID = %s WHERE id = " + str(tag_ids['tags'])
                self.db.execute(sql, (details['newID']))


def check_bad_children(bad_id, tag_dictionary):
        bad_children = []
        for name_id, tag_dict in tag_dictionary.iteritems():
            if tag_dict['parentID'] == bad_id and name_id != bad_id:
                bad_children.append(name_id)
        return bad_children


def delete_bad_tags(tag_dictionary):
    # Get initial Set of bad IDs
    bad_ids = []
    for name_id in tag_dictionary:
        if name_id == tag_dictionary[name_id]['parentID']:
            bad_ids.append(name_id)
    ids_to_delete = bad_ids

    # Get all the children of those bad ids
    while bad_ids:
        bad_children = []
        for bad_id in bad_ids:
            new_children = check_bad_children(bad_id, tag_dictionary)
            if new_children:
                ids_to_delete.extend(new_children)
                bad_children.extend(new_children)
            bad_ids = bad_children

    # Delete all the bad tags
    for bad_id in ids_to_delete:
        del tag_dictionary[bad_id]

    return tag_dictionary


def add_depth(tag_dictionary):
        for name_id in tag_dictionary:
            count = 0
            tag_id = name_id
            parent_id = tag_dictionary[tag_id]['parentID']
            while not parent_id == 'Top':
                count += 1
                tag_id = parent_id
                parent_id = tag_dictionary[tag_id]['parentID']
            else:
                tag_dictionary[name_id]['depth'] = count

        return tag_dictionary


def add_tag_type(tag_dictionary):
    for name_id in tag_dictionary:
        tag_type = 'L'
        for value in tag_dictionary.values():
            if 'parentID' in value:
                if name_id == value['parentID']:
                    tag_type = 'N'
        tag_dictionary[name_id]['tagType'] = tag_type
    return tag_dictionary


def prep_tags(tag_dict):
    tag_dict = delete_bad_tags(tag_dict)
    tag_dict = add_depth(tag_dict)
    tag_dict = add_tag_type(tag_dict)
    return tag_dict


def parse_xml(filename):
    try:
        with open(filename) as xml_file:
            xml_dict = xmltodict.parse(xml_file.read())
        return xml_dict
    except:
        print "File Not XML"
        return None


def get_default_rollup(xml_main_dict):
    return xml_main_dict['@defaultRollup']


def get_category(xml_main_dict):
    return xml_main_dict['@nameType']


def main():
    # Get the XML files
    xml_dir = "COAMS_XML"
    files = os.listdir(xml_dir)

    # Parser each file
    for filename in files:
        print 'Working On "' + filename + '"'
        # Convert XML to Dictionary
        xml_dict = parse_xml(xml_dir + "/" + filename)
        if xml_dict:
            xml_main_dict = xml_dict.values()[0]
            # Get default Category and Rollup
            category = get_category(xml_main_dict)
            default_rollup = get_default_rollup(xml_main_dict)

            # Handle the modification tabs
            modifications = Modification(category, default_rollup)
            mod_dict, functional_mod_dict = modifications.parse(xml_main_dict)

            # Handle all the Migrations
            migrations = Migration(category, default_rollup)
            migration_dict, functional_migration_dict = migrations.parse(xml_main_dict)

            # Prep and add dictionaries to database
            mist_db = Database()
            if migration_dict:
                mist_db.insert_migrations(migration_dict)
            if functional_migration_dict:
                mist_db.insert_migrations(functional_migration_dict)
            if mod_dict:
                for rollup, tag_dict in mod_dict.iteritems():
                    mod_dict[rollup] = prep_tags(tag_dict)
                mist_db.insert_modifications(mod_dict)
            if functional_mod_dict:
                for rollup, tag_dict in functional_mod_dict.iteritems():
                    functional_mod_dict[rollup] = prep_tags(tag_dict)
                mist_db.insert_modifications(functional_mod_dict)


if __name__ == "__main__":
    main()