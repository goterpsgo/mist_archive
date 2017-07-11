import base64
from sqlalchemy import Column, Enum, DateTime, String, Integer, func, ForeignKey, create_engine, join, and_, distinct, between, select, event, exc
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import select, func
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.exc import IntegrityError, ProgrammingError, StatementError, OperationalError, InvalidRequestError, ResourceClosedError, NoSuchColumnError
from sqlalchemy.dialects.mysql import TIMESTAMP, CHAR
from base_model import Base

class UserPermission(Base.Model):
    __tablename__ = "userPermissions"
    id = Column(Integer, primary_key=True)
    name = Column(String(20))

class MistUser(Base.Model):
    __tablename__ = "mistUsers"
    id = Column(Integer, primary_key=True)
    username = Column(String(200))
    password = Column(String(65))
    subjectDN = Column(String(400))
    firstName = Column(String(200))
    lastName = Column(String(200))
    organization= Column(String(200))
    lockout = Column(String(5), default="No")
    permission = Column(Integer, default=2)

    permission_id = Column(Integer, ForeignKey('userPermissions.id'))
    permissions = relationship("UserPermission", backref="mistUser")
    # user_accesses = relationship('UserAccess', backref="mistUser", cascade="all, delete-orphan", lazy="dynamic", single_parent=True)
    # request_user_accesses = relationship('RequestUserAccess', backref="mistUser", cascade="all, delete-orphan", lazy="dynamic", single_parent=True)
    # permissions = relationship("UserPermission", backref="mistUser", cascade="all, delete-orphan", lazy='dynamic', single_parent=True)

class Repos(Base.Model):
    __tablename__ = "Repos"
    id = Column(Integer, primary_key=True)
    assetID = Column(Integer)
    repoID = Column(Integer)
    scID = Column(String(150))
    repoName = Column(String(500))
    serverName = Column(String(300))

class UserAccess(Base.Model):
    __tablename__ = "userAccess"
    id = Column(Integer, primary_key=True)
    repoID = Column(Integer, ForeignKey('Repos.id'))
    userID = Column(Integer, ForeignKey('mistUsers.id'))
    scID = Column(String(150))
    userName = Column(String(45), ForeignKey('mistUsers.username'))
    is_assigned = Column(TIMESTAMP)

class requestUserAccess(Base.Model):
    __tablename__ = "requestUserAccess"
    id = Column(Integer, primary_key=True)
    repoID = Column(Integer, ForeignKey('Repos.id'))
    userID = Column(Integer, ForeignKey('mistUsers.id'))
    scID = Column(String(150))
    userName = Column(String(45), ForeignKey('mistUsers.username'))

class SecurityCenter(Base.Model):
    __tablename__ = "securityCenters"
    id = Column(Integer, primary_key=True)
    fqdn_IP = Column(String(256))
    serverName = Column(String(100))
    version = Column(String(45))
    username = Column(String(45), nullable=True)
    pw = Column(String(256), nullable=True)
    certificateFile = Column(String(512), nullable=True)
    keyFile = Column(String(512), nullable=True)

class BannerText(Base.Model):
    __tablename__ = "bannerText"
    index = Column(Integer, primary_key=True)
    BannerText = Column(String(256))

class Classifications(Base.Model):
    __tablename__ = "classifications"
    index = Column(Integer, primary_key=True)
    level = Column(String(45))
    color = Column(String(45))
    selected = Column(String(1), default="N")
    display = Column(String(100))

class MistParams(Base.Model):
    __tablename__ = "mistParams"
    id = Column(Integer, primary_key=True)
    chunkSize = Column(Integer, default=2000)   # in KB
    scPullFreq = Column(Integer, default=24)    # in hours
    logsRollOverPeriod = Column(Integer, default=30)    # in days
    pubsRollOverPeriod = Column(Integer, default=30)    # in days

class PublishSites(Base.Model):
    __tablename__ = "publishSites"
    id = Column(Integer, primary_key=True)
    location = Column(String(500))
    name = Column(String(50))

class TagDefinitions(Base.Model):
    __tablename__ = "tagDefinition"
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    title = Column(String(200))
    description = Column(String(1500))
    required = Column(Enum("Y", "N"))
    defaultValue = Column(String(25))
    type = Column(String(100))
    cardinality = Column(Integer)
    version = Column(String(25))
    rollup = Column(String(250))
    category = Column(String(150))
    timestamp = Column(TIMESTAMP)
    tags = relationship('Tags', backref="tagDefinition", cascade="all, delete-orphan", lazy="dynamic", single_parent=True)

class Tags(Base.Model):
    __tablename__ = "Tags"
    id = Column(Integer, primary_key=True)
    nameID = Column(String(20))
    category = Column(String(50), ForeignKey('tagDefinition.category'))
    rollup = Column(String(300))
    tag_definition_id = Column(Integer)
    parentID = Column(String(20), default="Top")
    hname = Column(String(1000))
    dname = Column(String(1000))
    tagType = Column(String(1), default="L")
    depth = Column(Integer, default=1)

class TaggedRepos(Base.Model):
    __tablename__ = "taggedRepos"
    id = Column(Integer, primary_key=True)
    repoID = Column(Integer)
    scID = Column(String(150))
    tagID = Column(String(20))
    rollup = Column(String(300), ForeignKey('tagDefinition.rollup'))
    category = Column(String(50))
    timestamp = Column(TIMESTAMP)
    status = Column(String(5))
    taggedBy = Column(String(200))

class Assets(Base.Model):
    __tablename__ = "Assets"
    assetID = Column(Integer, primary_key=True)
    biosGUID = Column(String(50))
    macAddress = Column(String(17))
    ip = Column(String(39))
    lastUnauthRun = Column(Integer)
    lastAuthRun = Column(Integer)
    netbiosName = Column(String(100))
    osCPE = Column(String(200))
    dnsName = Column(String(200))
    mcafeeGUID = Column(String(100))
    state = Column(CHAR(1))
    published = Column(CHAR(1))
    purged = Column(CHAR(1))

class TaggedAssets(Base.Model):
    __tablename__ = "taggedAssets"
    id = Column(Integer, primary_key=True)
    assetID = Column(Integer)
    tagID = Column(String(20))
    rollup = Column(String(300))
    category = Column(String(50))
    taggedBy = Column(String(200))
    timestamp = Column(TIMESTAMP)
    status = Column(String(5))
    tagMode = Column(String(45))

class PublishSched(Base.Model):
    __tablename__ = "publishSched"
    id = Column(Integer, primary_key=True)
    user = Column(String)
    destSite = Column(String)
    publishOptions = Column(String)
    freqOption = Column(String)
    weekOfMonth = Column(CHAR(3))
    dayOfMonth = Column(CHAR(2))
    time = Column(String)
    daysOfWeeks = Column(String)
    timezone = Column(String)
    status = Column(String)
    assetOptions = Column(String)
    destSiteName = Column(String)
    dateScheduled = Column(TIMESTAMP)

class PublishJobs(Base.Model):
    __tablename__ = "publishJobs"
    jobID = Column(Integer, primary_key=True)
    finishTime = Column(TIMESTAMP)
    status = Column(String)
    userName = Column(String)
    filename = Column(String)

class Published(Base.Model):
    __tablename__ = "published"
    id = Column(Integer, primary_key=True)
    userName = Column(String)
    userID = Column(Integer)
    timestamp = Column(TIMESTAMP)

class RepoPublishTimes(Base.Model):
    __tablename__ = "repoPublishTimes"
    id = Column(Integer, primary_key=True)
    scID = Column(String)
    repoID = Column(Integer)
    arfLast = Column(TIMESTAMP)
    cveLast = Column(TIMESTAMP)
    pluginLast = Column(TIMESTAMP)
    benchmarkLast = Column(TIMESTAMP)
    iavmLast = Column(TIMESTAMP)
    opattrLast = Column(TIMESTAMP)

class RemovedSCs(Base.Model):
    __tablename__ = "removedSCs"
    id = Column(Integer, primary_key=True)
    scName = Column(String)
    ack = Column(String)
    ackUser = Column(String)
    removeDate = Column(TIMESTAMP)
    ackDate = Column(TIMESTAMP)

connect_string = 'mysql://mistUser:m1$TD@t@B@$3!@#@mistDB:3306/MIST'
# connect_string = 'mysql://mistUser:m1$TD@t@B@$3!@#@10.11.1.241:3306/MIST'
ssl_args = {'ssl': {'cert': '/opt/mist/mist_base/certificates/mist-interface.crt',
                    'key': '/opt/mist/mist_base/certificates/mist-interface.key',
                    'ca': '/opt/mist/mist_base/certificates/si_ca.crt'}}

# ========== NOTE ==========
# MySQL times out after 8 hours of inactivity by default:
# http://dev.mysql.com/doc/refman/5.7/en/server-system-variables.html#sysvar_wait_timeout
# added pool_recycle param (set to 1 hour) to create_engine to prevent connections from timing out
# http://docs.sqlalchemy.org/en/latest/core/engines.html?highlight=pool_recycle#sqlalchemy.create_engine.params.pool_recycle
# In /etc/my.cnf, set wait_timeout and interactive_timeout values to > pool_recycle value.
# https://support.rackspace.com/how-to/how-to-change-the-mysql-timeout-on-a-server/
engine = create_engine(connect_string, connect_args=ssl_args, echo=False, pool_recycle=3600)
Session = sessionmaker(bind=engine)
session = Session()

# http://docs.sqlalchemy.org/en/latest/core/pooling.html#custom-legacy-pessimistic-ping
@event.listens_for(engine, "engine_connect")
def ping_connection(connection, branch):
    if branch:
        # "branch" refers to a sub-connection of a connection,
        # we don't want to bother pinging on these.
        return

    # turn off "close with result".  This flag is only used with
    # "connectionless" execution, otherwise will be False in any case
    save_should_close_with_result = connection.should_close_with_result
    connection.should_close_with_result = False

    try:
        # run a SELECT 1.   use a core select() so that
        # the SELECT of a scalar value without a table is
        # appropriately formatted for the backend
        connection.scalar(select([1]))
    except exc.DBAPIError as err:
        # catch SQLAlchemy's DBAPIError, which is a wrapper
        # for the DBAPI's exception.  It includes a .connection_invalidated
        # attribute which specifies if this connection is a "disconnect"
        # condition, which is based on inspection of the original exception
        # by the dialect in use.
        if err.connection_invalidated:
            # run the same SELECT again - the connection will re-validate
            # itself and establish a new connection.  The disconnect detection
            # here also causes the whole connection pool to be invalidated
            # so that all stale connections are discarded.
            connection.scalar(select([1]))
        else:
            raise
    finally:
        # restore "close with result"
        connection.should_close_with_result = save_should_close_with_result

