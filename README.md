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

Mocking is available to allow for the call to be built out using the parameters you have chosen so you can see all of the details. The only difference is the call will not actually be executed.

**Note:** You do not have to login to the application in order to use the Mock capability for any product

View the public version at [https://cloud-api.info](https://cloud-api.info "Pitchfork Application")

#### Want to run it locally?
All you need is Python 2.7, Mongodb, and a web browser

##### Create a virtual environment
**Note:** The below example uses virtualenvwrapper

````
mkvirtualenv pitchfork
cd pitchfork
git clone https://github.com/rackerlabs/pitchfork.git
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

#### Testing
The application unit tests can be run with nose and selenium. To install the requirements to run test do the following in your virtual environment
````
pip install nose coverage selenium
````

Selenium by default uses PhantomJS driver to run the browser tests. You can change the driver by editing the tests/test_selenium.py file and commenting out the PhantomJS line and uncommenting the Firefox driver line.

**Note:** If you do not have the PhantomJS driver and the driver is not changed the tests will be skipped
````
def setUpClass(cls):
    try:
        cls.client = webdriver.PhantomJS(service_log_path=os.path.devnull)
        # cls.client = webdriver.Firefox()
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
**Note:** Selenium tests uses port 5000 when running.
