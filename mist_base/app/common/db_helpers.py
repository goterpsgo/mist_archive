import ConfigParser
import re

class PasswordCheck:

    def __init__(self, password):
        self.pw = password
        self.config = ConfigParser.ConfigParser()

    def check_password(self):
        # Get the complexity Rules
        self.config.readfp(open('./common/.password_complexity.conf'))

        # Check complexity
        if not self.long_enough():
            return '\nNot long enough must have ' + self.config.get('Rules', 'length') + ' characters'
        elif not self.has_lowercase():
            return '\nNot enough lower case characters must have at least: ' + self.config.get('Rules', 'lowercase')
        elif not self.has_uppercase():
            return '\nNot enough upper case character must have at least: ' + self.config.get('Rules', 'uppercase')
        elif not self.has_numeric():
            return '\nNot enough numeric characters must have at least: ' + self.config.get('Rules', 'numbers')
        elif not self.has_special():
            return '\nNot enough special characters must have at least: ' + self.config.get('Rules', 'special')
        else:
            return None

    def long_enough(self):
        return len(self.pw) >= self.config.getint('Rules', 'length')

    def has_lowercase(self):
        return len(re.findall(r'[a-z]', self.pw)) >= self.config.getint('Rules', 'lowercase')

    def has_uppercase(self):
        return len(re.findall(r'[A-Z]', self.pw)) >= self.config.getint('Rules', 'uppercase')

    def has_numeric(self):
        return len(re.findall(r'\d', self.pw)) >= self.config.getint('Rules', 'numbers')

    def has_special(self):
        return len(re.findall(r'[^0-9A-Za-z]', self.pw)) >= self.config.getint('Rules', 'special')