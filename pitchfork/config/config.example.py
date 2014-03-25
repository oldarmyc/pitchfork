# Application config file
import os


MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_KWARGS = {'tz_aware': True}
MONGO_DATABASE = 'pitchfork'

ADMIN = 'cloud_username'
ADMIN_NAME = 'Admin Full Name'

SECRET_KEY = 'secret_key_for_cookie'
LOG_PATH = os.path.join(os.path.dirname(__file__), 'logs/devel.log')
