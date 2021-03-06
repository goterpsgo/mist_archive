
import os
import datetime
import pwd
import grp
import tarfile


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

        # Set file ownership
        self.set_log_ownership()

        # Set the file names for the logs
        self.log_prefix = datetime.datetime.now().strftime('%m%Y')
        self.asset_error = self.path + "/assets/" + self.log_prefix + "_error.log"
        self.asset_event = self.path + "/assets/" + self.log_prefix + "_events.log"
        self.publishing_error = self.path + "/publishing/" + self.log_prefix + "_error.log"
        self.publishing_event = self.path + "/publishing/" + self.log_prefix + "_event.log"
        self.tag_event = self.path + "/tagging/" + self.log_prefix + "_tag_events.log"

        #check for old logs and tar them up
        self.tar_old_logs()

    def tar_old_logs(self):
        log_files = []
        for (dirpath, dirnames, filenames) in os.walk(self.path):
            for filename in filenames:
                if filename.endswith('.log'):
                    log_files.append(os.path.join(dirpath, filename))

        for log_file in log_files:
            local_log_prefix = os.path.basename(log_file).split('_')[0]
            if local_log_prefix != self.log_prefix:
                tar = tarfile.open(os.path.splitext(log_file)[0] + '.tar.gz', "w:gz")
                tar.add(os.path.abspath(log_file), arcname=os.path.basename(log_file))
                os.remove(log_file)

    def set_log_ownership(self):
        for root, dirs, files in os.walk(self.path):
            for directory in dirs:
                if directory != 'frontend':
                    os.chown(os.path.join(root, directory), pwd.getpwnam(self.user).pw_uid,
                             grp.getgrnam(self.group).gr_gid)
            for log_file in files:
                if root != self.path + "/frontend":
                    os.chown(os.path.join(root, log_file), pwd.getpwnam(self.user).pw_uid,
                             grp.getgrnam(self.group).gr_gid)

    def get_date(self):
        return '[' + datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y") + '] '

    def error_assets(self, messages):
        with open(self.asset_error, "a+") as lf:
            lf.write(self.get_date())
            lf.write('[Error] ')
            for error_message in messages:
                lf.write(error_message)
            lf.write('\n')
        # Set file ownership
        self.set_log_ownership()

    def error_publishing(self, messages):
        with open(self.publishing_error, "a+") as lf:
            lf.write(self.get_date())
            lf.write('[Error] ')
            for error_message in messages:
                lf.write(error_message)
            lf.write('\n')
        # Set file ownership
        self.set_log_ownership()

    def remove_repo(self, repo_name, server_name):
        with open(self.asset_event, "a+") as lf:
            lf.write(self.get_date())
            event = ['[Repository Removed] ', "The repo ", repo_name, ", on Security Center ", server_name,
                     " was removed from MIST\n"]
            for message in event:
                lf.write(message)
        # Set file ownership
        self.set_log_ownership()

    def add_repo(self, repo_name, server_name):
        with open(self.asset_event, "a+") as lf:
            lf.write(self.get_date())
            event = ['[Repository Added] ', "The Repository ", repo_name, " from Security Center ", server_name,
                     " was added to MIST\n"]
            for message in event:
                lf.write(message)
        # Set file ownership
        self.set_log_ownership()

    def remove_asset(self, asset_id):
        with open(self.asset_event, "a+") as lf:
            lf.write(self.get_date())
            event = ['[Asset Removed] ', "Asset ", str(asset_id), " was removed from MIST\n"]
            for message in event:
                lf.write(message)
        # Set file ownership
        self.set_log_ownership()

    def add_asset(self, asset_id):
        with open(self.asset_event, "a+") as lf:
            lf.write(self.get_date())
            event = ['[Asset Added] ', "Asset ", str(asset_id), " was added to MIST\n"]
            for message in event:
                lf.write(message)
        # Set file ownership
        self.set_log_ownership()

    def web_publish(self, username, url):
        with open(self.publishing_event, "a+") as lf:
            lf.write(self.get_date())
            event = ['[Web Publish] ', "User ", username, " successfully published to ", url, '\n']
            for message in event:
                lf.write(message)
        # Set file ownership
        self.set_log_ownership()

    def local_publish(self, username, filename):
        with open(self.publishing_event, "a+") as lf:
            lf.write(self.get_date())
            event = ['[Local Publishing] ', 'User ', username, ' locally published file: ', filename, '\n']
            for message in event:
                lf.write(message)
        # Set file ownership
        self.set_log_ownership()

    def user_collision(self, result):
        tag_method, username, assets, repo, error_message = result
        error_message = error_message.strip()
        if tag_method == 'Manual':
            asset_list = assets[:-1]
            messages = ['[User Collision] ', 'User {', username, '} attempted to tag assets {', asset_list,
                        '} but received error message {', error_message, '}\n']
        else:
            messages = ['[User Collision] ', 'User {', username, '} attempted to tag repo {', repo,
                        '} but received error message {', error_message, '}\n']
        with open(self.tag_event, "a+") as lf:
            lf.write(self.get_date())
            for message in messages:
                lf.write(message)
        # Set file ownership
        self.set_log_ownership()
