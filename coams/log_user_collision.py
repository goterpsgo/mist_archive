import optparse
import sys
from sqlalchemy import *
import base64
import datetime
import mist_logging

sys.path.insert(0, '/opt/mist/database')
import config


class Database:
    def __init__(self):
        connection_string = 'mysql://' + config.username + ':' + base64.b64decode(config.password) + '@mistDB:3306/MIST'
        ssl_args = {'ssl': {'cert': '/opt/mist/database/certificates/mist-interface.crt',
                            'key': '/opt/mist/database/certificates/mist-interface.key',
                            'ca': '/opt/mist/database/certificates/si_ca.crt'}}
        self.db = create_engine(connection_string, connect_args=ssl_args, echo=False)
        self.metadata = MetaData(self.db)

    def execute_sql(self, sql):
        try:
            results = self.db.execute(sql)
            return results
        except Exception, e:
            print e

    def get_user_collisions(self, timestamp):
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "SELECT tagMethod, username, assets, repo, errorMessage FROM userCollision WHERE timestamp " \
              "BETWEEN '%s' AND '%s'" % (timestamp, time_now)
        results = self.execute_sql(sql)
        return results


def main():
    # set parser options
    parser = optparse.OptionParser()
    parser.add_option('--time', action='store', dest='timestamp', help='Timestamp to start looking for collisins from')
    options, remainder = parser.parse_args()

    if not options.timestamp:
        print "\nNo time specified!\n"
        parser.print_help()
        sys.exit(1)

    database = Database()
    log = mist_logging.Log()

    collisions = database.get_user_collisions(options.timestamp)
    for collision in collisions:
        log.user_collision(collision)


if __name__ == "__main__":
    main()
