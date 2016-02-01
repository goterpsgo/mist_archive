import getpass
import sqlalchemy
import base64
import os
import hashlib

#database stuff
import sys
sys.path.insert(0, '/opt/mist/database')
import config

def check_admin_user(user, password):
	#Set up connection
	engine = sqlalchemy.create_engine('mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST', echo=False)
    	conn = engine.connect()

	#convert password to sha-256 password
	hash_object = hashlib.sha256(password)
	hex_pass = hash_object.hexdigest()

	user_exists = False
	results = conn.execute("SELECT permission FROM mistUsers WHERE username = '" + username + "' and password = '" + hex_pass + "'")
	if results:
		for result in results:
			permission = result[0]
			user_exists = True

	if user_exists:
		if permission == 2 or permission == 3:
			admin = True
		else:
			admin = False
	else:
		admin = False

	return user_exists, admin

def check_int(s):
	if s[0] in ('-', '+'):
    		return s[1:].isdigit()
	return s.isdigit()

def get_user_edits():
	#Set up connection
	engine = sqlalchemy.create_engine('mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST', echo=False)
        conn = engine.connect()
	
	#Get a list of all the user names
	user_results = conn.execute("SELECT username FROM mistUsers")
	user_dict = {}
	user_change_dict = {}
	count = 1
	if user_results:
		for result in user_results:
			user_dict[count] = result[0]
			user_change_dict[count] = 'N'
			count += 1

	print "\nList of available users:\n"
	for user_count, user in user_dict.iteritems():
		print str(user_count) + ". " + user

	user_selection = True
	while user_selection:	
		user_change = raw_input("\nEnter the number of the user you wish to make admin: ")
		is_integer = check_int(user_change)
		if is_integer:
			if int(user_change) in user_change_dict:
				user_change_dict[int(user_change)] = 'Y'
				correct_input = True
			else:
				print "\nYou did not enter a number on the list provided, please try again" 
				correct_input = False
		else:
			print "\nYou did not enter a number from the list provided, please try again"
			correct_input = False

		if correct_input:
			add_another = True
			while add_another:
				another_user = raw_input("Would you like to change another user? (y/n): ")
				accepted_answers = ['n', 'y', 'yes', 'no']
				if another_user.lower() not in accepted_answers:
					print "Incorrect Choice, please type one of the following", accepted_answers
				else:
					add_another = False
					if another_user.lower() == 'n' or another_user.lower() == 'no':
						user_selection = False
	
	return user_dict, user_change_dict
					
				
def edit_user_permission(user_dict, user_change_dict):
	#Set up connection
        engine = sqlalchemy.create_engine('mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST', echo=False)
        conn = engine.connect()

	for key, set_permission in user_change_dict.iteritems():
		if set_permission == 'Y':
			conn.execute("UPDATE mistUsers SET permission = 2 WHERE username = '" + user_dict[key] + "'")

	conn.close()

if __name__ == "__main__":

	#Make sure that user running this is an admin
	username = raw_input("\nEnter your MIST username: ")
    	password = getpass.getpass("Enter your MIST password: ")
	user_exists, admin = check_admin_user(username, password)
	
	#Check to make sure that user exists and can make admin changes
	edit_user = False
	if user_exists:
		if admin:
			edit_user = True
		else:
			print "\nYou are not admin user so you cannot complete this function\n"
	else:
		print "\nYou are not a user in the mist application, or your username and password are incorrect\n"

	if edit_user:
		#let him change person to admin
		user_dict, user_change_dict = get_user_edits()
		#make changes to users in database
		edit_user_permission(user_dict, user_change_dict)

			






