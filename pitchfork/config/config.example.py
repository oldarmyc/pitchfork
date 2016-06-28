# Copyright 2014 Dave Kludt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
    If you are running the application within docker using the provided
    Dockerfile and docker-compose then you will need to change the MONGO_HOST
    option to use the correct container.

    import os

    MONGO_HOST = os.environ['PITCHFORK_DB_1_PORT_27017_TCP_ADDR']

"""

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_KWARGS = {'tz_aware': True}
MONGO_DATABASE = 'pitchfork'

ADMIN_USERNAME = 'cloud_username'
ADMIN_NAME = 'Admin Full Name'
ADMIN_EMAIL = 'Admin Email'

SECRET_KEY = 'secret_key_for_cookie'
