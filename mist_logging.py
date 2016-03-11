
import os
import datetime
import pwd
import grp


class Log:

    def __init__(self):
        # Initialize Variables
        self.user = 'mist'
        self.group = 'mist'
        self.path = "/var/log/MIST"

        # Create the directories needed
        if not os.path.exists(self.path + "/assets"):
            os.makedirs(self.path + "/assets")
        if not os.path.exists(self.path + "/publishing"):
            os.makedirs(self.path + "/publishing")
        if not os.path.exists(self.path + '/tagging'):
            os.makedirs(self.path + '/tagging')

        # Set the file names for the logs
        self.asset_error = self.path + "/assets/error.log"
        self.asset_event = self.path + "/assets/events.log"
        self.publishing_error = self.path + "/publishing/error.log"
        self.publishing_event = self.path + "/publishing/event.log"

    def set_log_ownership(self):
        for root, dirs, files in os.walk(self.path):
            for directory in dirs:
                os.chown(os.path.join(root, directory), pwd.getpwnam(self.user).pw_uid, grp.getgrnam(self.group).gr_gid)
            for log_file in files:
                os.chown(os.path.join(root, log_file), pwd.getpwnam(self.user).pw_uid, grp.getgrnam(self.group).gr_gid)

    def get_date(self):
        return '[' + datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y") + '] '

    def error_assets(self, messages):
        with open(self.asset_error, "a+") as lf:
            lf.write(self.get_date())
            lf.write('[Error] ')
            for error_message in messages:
                lf.write(error_message)

    def error_publishing(self, messages):
        with open(self.publishing_error, "a+") as lf:
            lf.write(self.get_date())
            lf.write('[Error] ')
            for error_message in messages:
                lf.write(error_message)

    def remove_repo(self, repo_name, server_name):
        with open(self.asset_event, "a+") as lf:
            lf.write(self.get_date())
            event = ['[Repository Removed] ', "The repo ", repo_name, ", on Security Center ", server_name,
                     " was removed from MIST\n"]
            for message in event:
                lf.write(message)

    def add_repo(self, repo_name, server_name):
        with open(self.asset_event, "a+") as lf:
            lf.write(self.get_date())
            event = ['[Repository Added] ', "The Repository ", repo_name, " from Security Center ", server_name,
                     " was added to MIST\n"]
            for message in event:
                lf.write(message)

    def remove_asset(self, asset_id):
        with open(self.asset_event, "a+") as lf:
            lf.write(self.get_date())
            event = ['[Asset Removed] ', "Asset ", str(asset_id), " was removed from MIST\n"]
            for message in event:
                lf.write(message)

    def add_asset(self, asset_id):
        with open(self.asset_event, "a+") as lf:
            lf.write(self.get_date())
            event = ['[Asset Added] ', "Asset ", str(asset_id), " was added to MIST\n"]
            for message in event:
                lf.write(message)

    def web_publish(self, username, url):
        with open(self.publishing_event, "a+") as lf:
            lf.write(self.get_date())
            event = ['[Web Publish] ', "User ", username, "successfully published to ", url, '\n']
            for message in event:
                lf.write(message)

    def local_publish(self, username, filename):
        with open(self.publishing_event, "a+") as lf:
            lf.write(self.get_date())
            event = ['[Local Publishing] ', 'User ', username, 'locally published file: ', filename, '\n']
            for message in event:
                lf.write(message)

