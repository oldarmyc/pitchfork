Pitchfork
=========

#### Cloud API Interactive Application

Using a browser you can execute any Rackspace API command for any Cloud product without the need to get on a command line or use another CLI tool.

To use the application just login with your username and Cloud Account API key.

The application is divided up by the different cloud products that are available to all customers.
Each call includes the following information:
* Variables needed with descriptions, data types, and what is required
* Endpoint and URI
* Links to the API docs specific section for the call you are needing more information for.

For each API call you will be shown the following information in the browser.
* Request URL
* Request Headers
* Request Object (If data object is used i.e. on Create or Update Statements)
* Response Headers
* Response Body

Warnings are on the calls that do things that could potentially impact an account (creates, updates, deletes, etc.).

#### Want to run it locally?
All you need is Python 2.7, Mongodb, and a web browser

##### Create a virtual environment to run it in:
mkvirtualenv your_virtual_env_name

cd into your new virtual environment

git clone https://github.com/rackerlabs/pitchfork.git

cd pitchfork

##### Use pip to install the requirements:
pip install -r requirements

##### Setup the config file:
cp pitchfork/config/config.example.py pitchfork/config/config.py

vi pitchfork/config/config.py

Change the following:
MONGO_DATABASE --> database name to use default is pitchfork

ADMIN --> Cloud account username for first admin

ADMIN_NAME --> Full name of admin

SECRET_KEY --> Used for cookie

Optional Changes:
MONGO_USER = 'Username for mongo database instance'

MONGO_PASS = 'Password for mongo database instance'

You can add to the KWARGS config item to add a replica set like the following example:

MONGO_KWARGS = {'tz_aware': True, 'replicaSet': 'my_replica_set'}

For more information on the options for Mongo see the hapPyMongo documentation

https://github.com/sivel/happymongo

##### Running the Application:
Save the file. To run the application type the following:

python runapp.py

Browse to http://localhost:5000 to view the application and login
