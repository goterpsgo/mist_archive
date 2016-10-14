from datetime import timedelta

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, '_app.db')
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Secret key for signing cookies
SECRET_KEY = "key4Mist!!!"

JWT_EXPIRATION_DELTA = timedelta(seconds=600)
JWT_VERIFY_CLAIMS = ['signature', 'exp', 'nbf', 'iat']
JWT_REQUIRED_CLAIMS = ['exp', 'iat', 'nbf']
