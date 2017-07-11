#!/usr/bin/env python
# import pdb
import json

raw_tags_list = [
        {"id": "0", "nameID": "1", "parentID": None, "name": "Root"},
        {"id": "1", "nameID": "2", "parentID": "1", "name": "One"},
        {"id": "2", "nameID": "3", "parentID": "1", "name": "Two"},
        {"id": "3", "nameID": "4", "parentID": "1", "name": "Three"},
        {"id": "4", "nameID": "5", "parentID": "3", "name": "Four"},
        {"id": "5", "nameID": "6", "parentID": "3", "name": "Five"},
        {"id": "6", "nameID": "7", "parentID": "5", "name": "Six"},
        {"id": "7", "nameID": "8", "parentID": "4", "name": "Seven"},
        {"id": "8", "nameID": "9", "parentID": "4", "name": "Eight"},
        {"id": "9", "nameID": "10" ,"parentID": "8", "name": "Nine"},
        {"id": "10", "nameID": "11", "parentID": "10", "name": "Ten"}
]

tags = dict((elem["nameID"], elem) for elem in raw_tags_list)
for elem in raw_tags_list:
        if (elem["parentID"] is not None):
                if ("children" not in tags[elem["parentID"]]):
                        tags[elem["parentID"]]['children'] = []
                tags[elem["parentID"]]['children'].append(tags[elem["nameID"]])
for key in tags.iterkeys():
        if tags[key]['parentID'] is None:
                print json.dumps(tags[key])

# print json.dumps(tags)

