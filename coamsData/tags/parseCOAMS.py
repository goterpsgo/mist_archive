
# -*- coding: utf-8 -*-
import requests
import xml.etree.ElementTree as ET
import csv
import os
import datetime
import base64

#databse stuff
import sys
sys.path.insert(0, '/opt/mist/database')
import config
from sqlalchemy import *


def getDefaultRollupInfo(root, tagType, NS):
	#Set dictionaries needed for data
	refDict = {}
	displayNameDict = {}
	idMapping = {}

	#Get items in default rollup
        for item in root.findall('{' + NS + '}' + tagType):
                if item.get('active') == "true":
			refDict[item.get('nameID')] = item.get('hName')
			displayNameDict[item.get('nameID')] = item.get('dName')
			if not item.get('superiorNameID'):
				idMapping[item.get('nameID')] = 'Top'
			else:
				idMapping[item.get('nameID')] = item.get('superiorNameID')
	return refDict, idMapping, displayNameDict

def getOtherRollupInfo(root, tagType, rollup, NS):
	#Set dictionaries needed for data
	refDict = {}
	idMapping = {}
	displayNameDict = {}

	#Get items in the other rollups which are passed in
	for item in root.findall('{' + NS + '}' + tagType):
		if item.get('active') == "true" and item.get('rollupType') == rollup:
			refDict[item.get('nameID')] = item.get('hName')
			displayNameDict[item.get('nameID')] = item.get('dName')
			if not item.get('superiorNameID'):
                        	idMapping[item.get('nameID')] = 'Top'
			else:
				idMapping[item.get('nameID')] = item.get('superiorNameID')
	return refDict, idMapping, displayNameDict


def getCOAMSData(fileName, NS):
	fileXML = "COAMS_data/XML/" + fileName

	#Try to see if file is correct XML to parse info from	
	try:
		tree = ET.parse(fileXML)
		root = tree.getroot()
		nameType = root.attrib['nameType']
	except:
		print "Not XML"
		return None, None, None, None

	idDict={}
        refDict={}
	displayDict={}
	#Getting Default Rollup and top level elements
	for item in root.getiterator('{%s}NameDistro' % NS):
		refDictionary, idMapping, displayNameDict = getDefaultRollupInfo(root, 'Modification', NS)
		refDict[item.get('defaultRollup')] = refDictionary
		idDict[item.get('defaultRollup')] = idMapping
		displayDict[item.get('defaultRollup')] = displayNameDict

	#Getting other Rollups and their top Level elements
	otherRollups = []
	for item in root.findall('{%s}FunctionalMod' % NS):
		if item.get('active') == "true":
			rollup = item.get('rollupType')
			if rollup not in otherRollups:
				otherRollups.append(rollup)

	#Once all the different rollups are gathered we parse the information in them
	if otherRollups:
		for rollup in otherRollups:
			refDictionary, idMapping, displayNameDict = getOtherRollupInfo(root, 'FunctionalMod', rollup, NS)
			refDict[rollup] = refDictionary
			idDict[rollup] = idMapping
			displayDict[rollup] = displayNameDict
	
	return refDict, idDict, displayDict, nameType

def checkIfExists(nameID, category, rollup, tagsTable):
	s = tagsTable.select(and_(tagsTable.c.nameID == nameID,
				  tagsTable.c.category == category,
				  tagsTable.c.rollup == rollup))
	rs = s.execute()
	for row in rs:
		if row:
			return True
		else:
			return False
	return False
			

def updateTag(tagsTable, nameID, category, rollup, parentID, hname, dname, tagType, depth):
	u = tagsTable.update().where(and_(tagsTable.c.nameID == nameID, tagsTable.c.category == category, tagsTable.c.rollup == rollup))\
			      .values(parentID = parentID, hname = hname, dname = dname, tagType = tagType, depth=depth)
	u.execute()

def insertTag(tagsTable, nameID, category, rollup, parentID, hname, dname, tagType, depth):
	i = tagsTable.insert()
	i.execute(nameID = nameID, category = category, rollup = rollup, 
		  parentID = parentID, hname = hname, dname = dname, tagType = tagType, depth = depth)

def createDatabase():
	#create the database stuff that we need
        connect_string = 'mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST'
        ssl_args = {'ssl':{'cert':'/opt/mist/database/certificates/mist-interface.crt', 'key':'/opt/mist/database/certificates/mist-interface.key', 'ca':'/opt/mist/database/certificates/si_ca.crt'}}
        db = create_engine(connect_string, connect_args=ssl_args, echo=False)
        #db.echo = True
        metadata = MetaData(db)
        tagsTable = Table('Tags', metadata, autoload=True)
	return db, tagsTable

def checkNodeLeaf(nameID, ids):
	#checking to see if ID is a parent or not
	tagType = 'L'
	for key, parentID in ids.iteritems():
		if nameID == parentID:
			tagType = 'N'
	return tagType
			
def getDepth(ids, nameID):
	count = 0
        parentID = ids[nameID]
        while not parentID == 'Top':
		if parentID == nameID:
                	return "drop"
                count += 1
                nameID = parentID
                parentID = ids[nameID]
        return count

def makeDatabase(tagsTable, refDict, idDict, displayDict, category):
	for rollup in idDict:
		ids = idDict[rollup]
		refs = refDict[rollup]
		display = displayDict[rollup]
 
		for nameID, parentID in ids.iteritems():
			tagType = checkNodeLeaf(nameID, ids)
			depth = getDepth(ids, nameID)
			if depth == "drop":
				continue
			exists = checkIfExists(nameID, category, rollup, tagsTable)
			if exists:
				updateTag(tagsTable, nameID, category, rollup, parentID, refs[nameID], display[nameID], tagType, depth)
			else:
				insertTag(tagsTable, nameID, category, rollup, parentID, refs[nameID], display[nameID], tagType, depth)


if __name__ == "__main__":

	#Base information about COAMS XML
	NS = 'http://metadata.dod.mil/mdr/ns/netops/ndl/0.1'
	files = os.listdir("COAMS_data/XML")

	# Loop through each XML file and get the data 
	for fileName in files:
		print 'Working On "' + fileName + '"'
		# Get data for whichever nameType we are on 
		refDict, idDict, displayDict, nameType = getCOAMSData(fileName, NS)
		if not nameType == None:
			# Make the sqlite databases for each nametype (Could use diff DB)
			db, tagsTable = createDatabase()
			makeDatabase(tagsTable, refDict, idDict, displayDict, nameType)

	#Test Code
	#refDict, idDict, displayDict, nameType = getCOAMSData('MAC.xml', NS)
	#makeDatabase(refDict, idDict, displayDict, nameType)
	
	#print nameType
	#print "refDict", refDict
	#print "idDict", idDict
	#print "displayDict", displayDict

