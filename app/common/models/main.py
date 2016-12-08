import base64
from sqlalchemy import Column, DateTime, String, Integer, func, ForeignKey, create_engine, join, and_, distinct
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import select
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.exc import IntegrityError, ProgrammingError, StatementError, OperationalError, InvalidRequestError, ResourceClosedError, NoSuchColumnError
from sqlalchemy.dialects.mysql import TIMESTAMP
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
    repoID = Column(Integer)
    userID = Column(Integer)
    scID = Column(String(150))
    userName = Column(String(45), ForeignKey('mistUsers.username'))
    is_assigned = Column(TIMESTAMP)

class requestUserAccess(Base.Model):
    __tablename__ = "requestUserAccess"
    id = Column(Integer, primary_key=True)
    repoID = Column(Integer)
    userID = Column(Integer)
    scID = Column(String(150))
    userName = Column(String(45), ForeignKey('mistUsers.username'))

class SecurityCenter(Base.Model):
    __tablename__ = "securityCenters"
    id = Column(Integer, primary_key=True)
    fqdn_IP = Column(String(256))
    serverName = Column(String(100), nullable=True)
    version = Column(String(45))
    username = Column(String(45), nullable=True)
    pw = Column(String(256), nullable=True)
    certificateFile = Column(String(512), nullable=True)
    keyFile = Column(String(512))

connect_string = 'mysql://mistUser:m1$TD@t@B@$3!@#@mistDB:3306/MIST'
ssl_args = {'ssl': {'cert': '/opt/mist_base/certificates/mist-interface.crt',
                    'key': '/opt/mist_base/certificates/mist-interface.key',
                    'ca': '/opt/mist_base/certificates/si_ca.crt'}}

# ========== NOTE ==========
# MySQL times out after 8 hours of inactivity by default:
# http://dev.mysql.com/doc/refman/5.7/en/server-system-variables.html#sysvar_wait_timeout
# added pool_recycle param (set to 6 hours) to create_engine to prevent connections from timing out
# http://docs.sqlalchemy.org/en/latest/core/engines.html?highlight=pool_recycle#sqlalchemy.create_engine.params.pool_recycle
engine = create_engine(connect_string, connect_args=ssl_args, echo=False, pool_recycle=21600)
Session = sessionmaker(bind=engine)
session = Session()

