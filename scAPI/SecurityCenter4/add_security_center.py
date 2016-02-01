import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/modules")
from crontab import CronTab

def add_pull_assets_cron():
	tab = CronTab()
    	cmd = 'python /opt/mist/scAPI/SecurityCenter4/pull_assets.py'
    	cron_job = tab.new(cmd)
    	cron_job.minute.every(30)
    	tab.write()


if __name__ == "__main__":

	if os.path.isdir("SecurityCenters"):
		#server = raw_input('Enter the DNS name of the Security Center you wish to add: ')

		#Check if the direcotry fo that server is already there
		#if os.path.isdir('SecurityCenters/' + server):
		#	print "You have already added a Security Center with that name"
		#	exit(0)
		#else:
		#	os.makedirs('SecurityCenters/' + server)

		
		#Add the file we need
		#with open('SecurityCenters/'+ server + '/securitycenter.txt', 'w') as sc_file:
		#	sc_file.write("server=" + server)
	
		#Add the cronjob
		add_pull_assets_cron()
	
	else:
		print "You are missing the SecurityCenters directory in this folder, please create then run this script again"
