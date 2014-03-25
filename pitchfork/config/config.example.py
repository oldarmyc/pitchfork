# Application config file
import os


MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_USER = None
MONGO_PASS = None
MONGO_KWARGS = None

ADMIN = 'cloud_username'
ADMIN_NAME = 'Full Name'

SECRET_KEY = 'secret_key'
LOG_PATH = os.path.join(os.path.dirname(__file__), 'logs/devel.log')
