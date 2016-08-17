import base64
from sqlalchemy import Column, DateTime, String, Integer, func, ForeignKey, create_engine
from sqlalchemy.orm import relationship
from base_model import Base

class MistUsers(Base.Model):
    __tablename__ = "mistUsers"
    id = Column(Integer, primary_key=True)
    username = Column(String(200))
    password = Column(String(65))
    permission = Column(Integer)
    subjectDN = Column(String(400))
    firstName = Column(String(200))
    lastName = Column(String(200))
    organization= Column(String(200))
    lockout = Column(String(5), default="No")

# engine = create_engine('mysql+mysqldb://mistUser:' + base64.b64decode('m1$TD@t@B@$3!@#') + '@mistDB/MIST')

connect_string = 'mysql://mistUser:m1$TD@t@B@$3!@#@mistDB:3306/MIST'
ssl_args = {'ssl': {'cert': '/opt/mist_base/certificates/mist-interface.crt',
                    'key': '/opt/mist_base/certificates/mist-interface.key',
                    'ca': '/opt/mist_base/certificates/si_ca.crt'}}
engine = create_engine(connect_string, connect_args=ssl_args, echo=False)
