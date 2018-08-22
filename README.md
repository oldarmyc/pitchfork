[![Build Status](https://travis-ci.org/oldarmyc/pitchfork.svg)](https://travis-ci.org/oldarmyc/pitchfork)

Pitchfork
=========

#### Rackspace Cloud API Interactive Application

Using a browser you can execute any Rackspace API command for any Cloud product without the need to get on a command line or use another CLI tool.

To use the application just login with your username and Cloud Account API key. The application does not store the API key and keeps no record of it. It only uses the API key to make the authentication call so that the application can generate the token. The token is then used in subsequent API calls, and is kept as long as there is a session. A logout will clear the session of any data, or when the token expires whichever comes first.

[View Authentication Call details](https://developer.rackspace.com/docs/cloud-identity/v2/developer-guide/#authenticate-as-user-with-password-or-api-key)

The application is divided up by the different cloud products that are available to all customers.
Each call includes the following information:
* Variables needed with descriptions, data types, and what is required
* Endpoint and URI
* Links to the API docs specific section for the call you are needing more information for.

For each API call you will be shown the following information in the browser.
* Request URL
* Request Headers
* Request Object (If data object is used i.e. on Create and Update Statements)
* Response Headers
* Response Body

Warnings are on the calls that do things that could potentially impact an account (creates, updates, deletes, etc.).

Mocking is available to allow for the call to be built out using the parameters you have chosen so you can see all of the details. The only difference is the call will not actually be executed.

**Note:** You do not have to login to the application in order to use the Mock capability for any product

View the public version at [https://pitchfork.cloudapi.co](https://pitchfork.cloudapi.co "Pitchfork Application")

#### Want to run it locally?
All you need is Python 2.7, Mongodb, and a web browser or use docker

##### Create a virtual environment
**Note:** The below example uses virtualenvwrapper

````
mkvirtualenv pitchfork
cd pitchfork
git clone https://github.com/oldarmyc/pitchfork.git
cd pitchfork
workon pitchfork
````

##### Use pip to install the requirements:
```
pip install -r requirements.txt
```

##### Setup the config file:
````
cp pitchfork/config/config.example.py pitchfork/config/config.py
vi pitchfork/config/config.py
````

*Change the following for your setup:*  
**MONGO_DATABASE** : Database name to use  
**ADMIN** : Cloud account username for first admin  
**ADMIN_NAME** : Full name of admin for the account above
**SECRET_KEY** : Used for sessions

*Optional Additions:*  
**MONGO_USER** = 'Username for mongo database instance'  
**MONGO_PASS** = 'Password for mongo database instance'  

You can add to the KWARGS config item to add a replica set.  
**MONGO_KWARGS** = {'tz_aware': True, 'replicaSet': 'my_replica_set'}

For more information on the options for Mongo see the hapPyMongo documentation.  
https://github.com/sivel/happymongo

##### Running the Application:
After you have saved the config file and your mongo database is up and running, run the following command to start the application.
````
python runapp.py
````
Browse to http://localhost:5000 to view the application and login using your Cloud credentials

#### Run the application using docker

##### Create and git the code
```
mkdir pitchfork
git clone https://github.com/oldarmyc/pitchfork.git
cd pitchfork
```

##### Copy over sample configs
````
cp pitchfork/config/config.example.py pitchfork/config/config.py
````

##### Edit the config.py file
```
vim pitchfork/config/config.py
```

##### Add import at top of file
```python
import os
```

##### Change MONGO_HOST from localhost to the following:
```python
MONGO_HOST = os.environ['PITCHFORK_DB_1_PORT_27017_TCP_ADDR']
```

##### Start the build
```
docker-compose build
```

##### Bring the containers up and run in the background
```
docker-compose up -d
```

##### Verify that everything is running
```
docker ps
```

##### Stoping the application
```
docker-compose stop
```

#### Upgrading
To upgrade an existing install to work with the recent changes do the following:

````
git pull origin master
pip install -r requirements
````

Log into mongodb. The command below assumes the database is named pitchfork.

````
use pitchfork
db.settings.remove()
db.api_settings.remove()
db.reporting.remove()
````

Browse to the home page and after it loads refresh the page. The refresh will force the app to repopulate the settings, reporting, and api_settings collections automatically to work with the new changes.

#### Adding API Calls

[Pitchfork API Calls](https://9050ceb3e176bf11567b-e447b4b840d054d4f862ad6101a6d6ee.ssl.cf5.rackcdn.com/api_calls/api_calls.tar.gz)

The download above will provide all of the mongodb bson files for each of the Rackspace products. Once you download the files you can do the following to restore all of the product collections to the pitchfork database.

```
tar xzvf api_calls.tar.gz
mongorestore -d pitchfork --drop pitchfork/
```

**Note:** If you have added your own calls into the collections you can omit the --drop in the call above, and the calls will be added to the existing collection.

If you are running pitchfork using the docker method above, the mongo container has the port 27017 exposed to the local machine. You can connect and do the restore just as you would using the above method.

#### Testing
The application unit tests can be run with nose and selenium. To install the requirements to run test do the following in your virtual environment
````
pip install nose coverage selenium
````

Selenium was setup to use firefox when the tests are run. However you can update the following to use the driver of your choice.

**Note:** If you do not have Firefox the tests will be skipped
````
def setUpClass(cls):
    try:
        cls.client = webdriver.Firefox()
    except:
        pass
````
Documentation for selenium can be found here: http://selenium-python.readthedocs.org/en/latest/

Once you are ready to run the tests do the following.
Run tests only
````
nosetests
````
Run tests with verbosity to see what tests are being run
````
nosetests -v
````
Run tests with coverage
````
nosetests --with-coverage --cover-erase --cover-package pitchfork
````
**Note:** Selenium tests uses port 5000 when running so ensure the application is not already running or some tests will fail.
