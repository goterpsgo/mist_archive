
import os
import datetime


class Log:

    def __init__(self):
        # Create the directories needed
        if not os.path.exists('/var/log/MIST/assets'):
            os.makedirs('/var/log/MIST/assets')
        if not os.path.exists('/var/log/MIST/publishing'):
            os.makedirs('/var/log/MIST/publishing')
        if not os.path.exists('/var/log/MIST/tagging'):
            os.makedirs('/var/log/MIST/tagging')

        # Set the file names for the logs
        self.asset_error = "/var/log/MIST/assets/error.log"
        self.asset_event = "/var/log/MIST/assets/events.log"
        self.publishing_error = "/var/log/MIST/publishing/error.log"
        self.publishing_event = "/var/log/MIST/publishing/event.log"

    def get_date(self):
        return '[' + datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y") + '] '

    def error_assets(self, messages):
        with open(self.asset_error, "a+") as lf:
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

    def log_publishing_event(self, messages):
        with open(self.publishing_event, "a+") as lf:
            lf.write(self.get_date())
            for error_message in messages:
                lf.write(error_message)

