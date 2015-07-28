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

from pitchfork.setup_application import create_app
from pitchfork.config import config
from uuid import uuid4
from datetime import datetime, timedelta
from dateutil import parser


import unittest
import json
import urlparse
import re


class PitchforkEngineTests(unittest.TestCase):
    def setUp(self):
        check_db = re.search('_test', config.MONGO_DATABASE)
        if not check_db:
            test_db = '%s_test' % config.MONGO_DATABASE
        else:
            test_db = config.MONGO_DATABASE

        self.pitchfork, self.db = create_app(test_db)
        self.app = self.pitchfork.test_client()
        self.app.get('/')

    def teardown_app_data(self):
        self.db.sessions.remove()
        self.db.settings.remove()
        self.db.api_settings.remove()
        self.db.forms.remove()
        self.db.reporting.remove()
        self.db.history.remove()

    def setup_user_login(self, sess):
        sess['username'] = 'test'
        sess['csrf_token'] = 'csrf_token'
        sess['role'] = 'logged_in'
        sess['_permanent'] = True
        sess['ddi'] = '654846'
        sess['cloud_token'] = uuid4().hex

    def setup_admin_login(self, sess):
        sess['username'] = 'oldarmyc'
        sess['csrf_token'] = 'csrf_token'
        sess['role'] = 'administrators'
        sess['_permanent'] = True
        sess['ddi'] = '654846'
        sess['cloud_token'] = uuid4().hex

    def setup_useable_logged_history(self, days=None):
        data = {
            'username': 'bobo1234',
            'ddi': '123456',
            'details': {
                'description': 'Retrieve a listing of the feed catalog',
                'doc_url': (
                    'http://docs.rackspace.com/cloud-feeds/api/v1.0/feeds-'
                    'getting-started/content/Cloud_Feeds_Catalog.html'
                ),
                'id': '53e50582192a8b6a41d06d3f',
                'title': 'Retrieve Feed Catalog'
            },
            'data_center': 'dfw',
            'product': 'Cloud Feeds',
            'request': {
                'url': 'https://dfw.feeds.api.rackspacecloud.com/123456/',
                'verb': 'GET',
                'data': None
            },
            'response': {
                'body': None,
                'headers': {
                    'content-length': '510',
                    'via': '1.1 Repose (Repose/5.0.2)',
                    'content-language': 'en-US',
                    'content-encoding': 'gzip',
                    'accept-ranges': 'bytes',
                    'vary': 'Accept-Encoding',
                    'x-newrelic-app-data': 'misc_data',
                    'server': 'Jetty(8.y.z-SNAPSHOT)',
                    'last-modified': 'Tue, 29 Jul 2014 17:17:46 GMT',
                    'connection': 'Keep-Alive',
                    'etag': 'W/\"5406-1406654266000\"',
                    'date': 'Fri, 08 Aug 2014 19:48:27 GMT',
                    'content-type': 'application/xml;charset=UTF-8'
                },
                'code': 200
            }
        }
        if days:
            data['completed_at'] = datetime.now() + timedelta(days=days)
        else:
            data['completed_at'] = datetime.now()

        self.db.history.insert(data)

    def setup_recorded_item_edge(self):
        data = {
            'test_list': [
                {'nested': 'value'}
            ],
            'test_dict': {
                'sso': 'value',
                'displayname': 'value_2'
            }
        }
        self.db.history.insert(data)

    def setup_useable_report_field(self, disable=None):
        data = {
            'description': 'region',
            'data_type': 'text',
            'field_display_data': '',
            'graphable': True,
            'field_display': 'SelectField',
            'field_name': 'region',
            'submit': 'Submit'
        }
        if disable:
            data['searchable'] = False
        else:
            data['searchable'] = True
        self.db.reporting.insert(data)

    def setup_all_report_fields(self):
        data = [
            {
                'description': 'Application Name',
                'data_type': 'text',
                'field_display_data': '',
                'graphable': True,
                'field_display': 'SelectField',
                'searchable': True,
                'field_name': 'appname'
            }, {
                'description': 'Status',
                'searchable': True,
                'field_display_data': '',
                'graphable': True,
                'data_type': 'text',
                'field_display': 'SelectField',
                'field_name': 'status'
            }, {
                'description': 'Completed At',
                'searchable': True,
                'field_display_data': '',
                'graphable': False,
                'data_type': 'datetime',
                'field_display': 'TextField',
                'field_name': 'completed_at'
            }, {
                'description': 'Billable',
                'searchable': True,
                'field_display_data': '',
                'graphable': False,
                'data_type': 'boolean',
                'field_display': 'SelectField',
                'field_name': 'billable'
            }, {
                'description': 'Waived',
                'searchable': True,
                'field_display_data': '',
                'graphable': False,
                'data_type': 'boolean',
                'field_display': 'BooleanField',
                'field_name': 'waive_billable'
            }
        ]
        for item in data:
            self.db.reporting.insert(item)

    def setup_misc_fields(self):
        data = [
            {
                'description': 'Text Field',
                'data_type': 'text',
                'field_display_data': '',
                'graphable': False,
                'field_display': 'TextField',
                'searchable': True,
                'field_name': 'misc_text'
            }, {
                'description': 'Select with choices',
                'data_type': 'text',
                'field_display_data': 'Select 1,Select 2',
                'graphable': True,
                'field_display': 'SelectField',
                'searchable': True,
                'field_name': 'misc_select'
            }, {
                'description': 'Boolean',
                'data_type': 'boolean',
                'field_display_data': '',
                'graphable': True,
                'field_display': 'SelectField',
                'searchable': True,
                'field_name': 'rework_step'
            }, {
                'description': 'CB Boolean',
                'data_type': 'boolean',
                'field_display_data': '',
                'graphable': True,
                'field_display': 'BooleanField',
                'searchable': True,
                'field_name': 'misc_checkbox'
            }
        ]
        for item in data:
            self.db.reporting.insert(item)

    def retrieve_csrf_token(self, data):
        temp = re.search('id="csrf_token"(.+?)>', data)
        if temp:
            token = re.search('value="(.+?)"', temp.group(1))
            if token:
                return token.group(1)
        return 'UNK'

    def test_engine_admin(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/engine/')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.teardown_app_data()

    def test_engine_user(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)
            response = c.get('/engine/')

        assert response._status_code == 302, (
            'Invalid response code %s' % response._status_code
        )
        location = response.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )
        self.teardown_app_data()

    def test_engine_admin_all_fields(self):
        self.setup_useable_logged_history()
        self.setup_all_report_fields()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.teardown_app_data()

    """ Setup """

    def test_engine_admin_setup(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/setup')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.teardown_app_data()

    def test_engine_user_setup(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)
            response = c.get('/engine/setup')

        assert response._status_code == 302, (
            'Invalid response code %s' % response._status_code
        )
        location = response.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )
        self.teardown_app_data()

    """ Manage Fields """

    def test_engine_admin_setup_fields(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/fields/manage')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.teardown_app_data()

    def test_engine_user_setup_fields(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)
            response = c.get('/engine/fields/manage')

        assert response._status_code == 302, (
            'Invalid response code %s' % response._status_code
        )
        location = response.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )
        self.teardown_app_data()

    """ Report Setup """

    def test_engine_admin_setup_settings_good(self):
        settings = self.db.settings.update(
            {}, {
                '$unset': {'reporting': 1}
            }
        )
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/setup')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'collection': 'work',
                'description': 'This is a description',
                'enabled': True,
                'allow_team': True
            }
            response = c.post(
                '/engine/setup',
                data=data,
                follow_redirects=True
            )

        settings = self.db.settings.find_one()
        reporting = settings.get('reporting')
        self.assertEquals(
            reporting.get('collection'),
            'work',
            'Collection was not saved correctly'
        )
        self.assertEquals(
            reporting.get('description'),
            'This is a description',
            'Description was not saved correctly'
        )
        self.assertEquals(
            reporting.get('enabled'),
            True,
            'Reporting was not disabled as expected'
        )
        self.assertEquals(
            reporting.get('allow_team'),
            True,
            'Team allow was not disabled as expected'
        )
        self.assertIn(
            'Reporting settings successfully updated',
            response.data,
            'Incorrect flash message after update'
        )
        self.teardown_app_data()

    def test_engine_admin_setup_settings_bad_data(self):
        settings = self.db.settings.update(
            {}, {
                '$unset': {'reporting': 1}
            }
        )
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            data = {
                'collection': 'work',
                'description': 'This is a description',
                'enabled': True,
                'allow_team': True
            }
            response = c.post(
                '/engine/setup',
                data=data,
                follow_redirects=True
            )

        settings = self.db.settings.find_one()
        reporting = settings.get('reporting')
        self.assertEquals(
            reporting,
            None,
            'Data was saved when it was not supposed to be'
        )
        self.assertIn(
            'Form validation error. Please check the form and resend request',
            response.data,
            'Incorrect flash message after sending bad data'
        )
        self.teardown_app_data()

    def test_engine_admin_setup_settings_no_data(self):
        self.db.settings.update({}, {'$unset': {'reporting': 1}})
        settings = self.db.settings.find_one()
        report_settings = settings.get('reporting')
        assert not report_settings, 'Settings should be empty'
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/setup')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'collection': 'work',
                'description': 'This is a description',
                'enabled': True,
                'allow_team': True
            }
            response = c.post(
                '/engine/setup',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Reporting settings successfully updated',
            response.data,
            'Incorrect flash message after update'
        )
        settings = self.db.settings.find_one()
        report_settings = settings.get('reporting')
        assert report_settings, 'Report setting were not set'
        self.teardown_app_data()

    """ Manage reporting fields """

    def test_engine_admin_setup_manage_fields_add_good(self):
        self.setup_useable_logged_history()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/fields/add')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'description': 'data_center',
                'data_type': 'text',
                'field_display_data': '',
                'graphable': True,
                'searchable': True,
                'field_display': 'SelectField',
                'field_name': 'data_center',
                'submit': 'Submit'
            }
            response = c.post(
                '/engine/fields/add',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Field was successfully added',
            response.data,
            'Incorrect flash message after add of field'
        )
        found = self.db.reporting.find_one()
        assert found, 'Added field was not found in db'
        self.teardown_app_data()

    def test_engine_admin_setup_manage_fields_add_empty_collection(self):
        self.db.history.remove()
        self.db.reporting.remove()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/fields/add')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'description': 'region',
                'data_type': 'text',
                'field_display_data': '',
                'graphable': True,
                'searchable': True,
                'field_display': 'SelectField',
                'field_name': 'region',
                'submit': 'Submit'
            }
            response = c.post(
                '/engine/fields/add',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            (
                'Collection has no data in it. Please '
                'insert data and resubmit form'
            ),
            response.data,
            'Incorrect flash message after add attempt with empty collection'
        )
        found = self.db.reporting.count()
        self.assertEquals(
            found,
            0,
            'Added field was found when it should not have been'
        )
        self.teardown_app_data()

    def test_engine_admin_setup_manage_fields_add_bad_field(self):
        self.setup_useable_logged_history()
        self.db.reporting.remove()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/fields/add')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'description': 'region',
                'data_type': 'text',
                'field_display_data': '',
                'graphable': True,
                'searchable': True,
                'field_display': 'SelectField',
                'field_name': 'bad_field',
                'submit': 'Submit'
            }
            response = c.post(
                '/engine/fields/add',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            (
                'Field name could not be found in collection.'
                ' Please check the name and resubmit form'
            ),
            response.data,
            'Incorrect flash message after add attempt with bad field'
        )
        found = self.db.reporting.count()
        self.assertEquals(
            found,
            0,
            'Added field was found when it should not have been'
        )
        self.teardown_app_data()

    def test_engine_admin_setup_manage_fields_add_invalid_form_data(self):
        self.db.reporting.remove()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            data = {
                'description': 'region',
                'data_type': 'text',
                'field_display_data': '',
                'graphable': True,
                'searchable': True,
                'field_display': 'SelectField',
                'field_name': 'region',
                'submit': 'Submit'
            }
            response = c.post(
                '/engine/fields/add',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            (
                'Form validation error. Please'
                ' check the form and resend request'
            ),
            response.data,
            'Incorrect flash message after add attempt with bad data'
        )
        found = self.db.reporting.count()
        self.assertEquals(
            found,
            0,
            'Added field was found when it should not have been'
        )
        self.teardown_app_data()

    def test_engine_admin_setup_manage_fields_edit_good(self):
        self.db.reporting.remove()
        self.setup_useable_logged_history()
        self.setup_useable_report_field()
        found = self.db.reporting.find_one()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get(
                '/engine/fields/edit/%s' % found.get('_id')
            )
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'description': 'Edit Field',
                'data_type': 'text',
                'field_display_data': '',
                'graphable': True,
                'searchable': True,
                'field_display': 'SelectField',
                'field_name': 'region',
                'submit': 'Submit'
            }
            response = c.post(
                '/engine/fields/edit/%s' % found.get('_id'),
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Field was successfully updated',
            response.data,
            'Incorrect flash message after add of field'
        )
        found = self.db.reporting.find_one()
        self.assertEquals(
            found.get('description'),
            'Edit Field',
            'Field edit was not successful'
        )
        self.teardown_app_data()

    def test_engine_admin_setup_manage_fields_deactivate(self):
        self.db.reporting.remove()
        self.setup_useable_report_field()
        found = self.db.reporting.find_one()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get(
                '/engine/fields/action/%s/deactivate' % found.get('_id'),
                follow_redirects=True
            )

        self.assertIn(
            'Field was marked as inactive',
            response.data,
            'Incorrect flash message after deactivate'
        )
        found = self.db.reporting.find_one()
        assert not found.get('searchable'), (
            'Field was not deactivated correctly'
        )
        self.teardown_app_data()

    def test_engine_admin_setup_manage_fields_activate(self):
        self.db.reporting.remove()
        self.setup_useable_report_field(True)
        found = self.db.reporting.find_one()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get(
                '/engine/fields/action/%s/activate' % found.get('_id'),
                follow_redirects=True
            )

        self.assertIn(
            'Field was marked as active',
            response.data,
            'Incorrect flash message after activate'
        )
        found = self.db.reporting.find_one()
        assert found.get('searchable'), 'Field was not deactivated correctly'
        self.teardown_app_data()

    def test_engine_admin_setup_manage_fields_bad_action(self):
        self.db.reporting.remove()
        self.setup_useable_report_field()
        found = self.db.reporting.find_one()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get(
                '/engine/fields/action/%s/bad_action' % found.get('_id'),
                follow_redirects=True
            )

        self.assertIn(
            'Incorrect action specified. No action taken',
            response.data,
            'Incorrect flash message after bad action'
        )
        found_after = self.db.reporting.find_one()
        assert found == found_after, 'Field was changed when not supposed to'
        self.teardown_app_data()

    def test_engine_admin_setup_manage_fields_bad_id(self):
        bad_id = '5319dbead7d30459940487f4'
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get(
                '/engine/fields/action/%s/activate' % bad_id,
                follow_redirects=True
            )

        self.assertIn(
            'Field could not be found. No action was taken',
            response.data,
            'Incorrect flash message after bad id number'
        )
        self.teardown_app_data()

    def test_engine_admin_setup_manage_fields_remove(self):
        self.db.reporting.remove()
        self.setup_useable_report_field()
        found = self.db.reporting.find_one()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get(
                '/engine/fields/remove/%s' % found.get('_id'),
                follow_redirects=True
            )

        self.assertIn(
            'Field has been removed',
            response.data,
            'Incorrect flash message after remove'
        )
        found = self.db.reporting.find()
        self.assertEquals(
            found.count(),
            0,
            'A field was found when it should have been removed'
        )
        self.teardown_app_data()

    def test_engine_admin_setup_manage_fields_remove_bad_id(self):
        self.db.reporting.remove()
        self.setup_useable_report_field()
        bad_id = '5319dbead7d30459940487f4'
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get(
                '/engine/fields/remove/%s' % bad_id,
                follow_redirects=True
            )

        self.assertIn(
            'Field could not be found, and nothing was removed',
            response.data,
            'Incorrect flash message after remove'
        )
        found = self.db.reporting.find()
        self.assertEquals(
            found.count(),
            1,
            'A field was not found when it should have been'
        )
        self.teardown_app_data()

    """ Generate Reports """

    def test_engine_admin_generate(self):
        self.setup_useable_logged_history()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.post('/engine/generate')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )

        self.assertIn(
            '<h3>Query Results - (1)</h3>',
            response.data,
            'Did not find any reporting results'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_daily_with_both_dates(self):
        self.setup_useable_logged_history()
        use_today = '%d-%d-%d' % (
            datetime.now().year,
            datetime.now().month,
            datetime.now().day
        )
        today = datetime.now() - timedelta(days=14)
        use_date = '%d-%d-%d' % (today.year, today.month, today.day)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': use_today,
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': use_date
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        self.assertEquals(
            len(response_data.get('labels')),
            15,
            'Incorrect number of labels in returned data'
        )
        self.assertEquals(
            len(response_data.get('points')),
            15,
            'Incorrect number of data points in returned data'
        )
        self.assertEquals(
            response_data.get('delta'),
            14,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )

        self.teardown_app_data()

    def test_engine_admin_generate_trend_daily_with_start_date(self):
        self.setup_useable_logged_history()
        today = datetime.now() - timedelta(days=14)
        use_date = '%d-%d-%d' % (today.year, today.month, today.day)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': '',
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': use_date
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        self.assertEquals(
            len(response_data.get('labels')),
            15,
            'Incorrect number of labels in returned data'
        )
        self.assertEquals(
            len(response_data.get('points')),
            15,
            'Incorrect number of data points in returned data'
        )
        self.assertEquals(
            response_data.get('delta'),
            14,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_daily_with_end_date(self):
        self.setup_useable_logged_history()
        today = datetime.now()
        use_date = '%d-%d-%d' % (today.year, today.month, today.day)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': use_date,
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': ''
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        self.assertEquals(
            len(response_data.get('labels')),
            1,
            'Incorrect number of labels in returned data'
        )
        self.assertEquals(
            len(response_data.get('points')),
            1,
            'Incorrect number of data points in returned data'
        )
        self.assertEquals(
            response_data.get('delta'),
            -1,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_daily_no_date_range(self):
        self.setup_useable_logged_history()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': '',
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': ''
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        self.assertEquals(
            len(response_data.get('labels')),
            1,
            'Incorrect number of labels in returned data'
        )
        self.assertEquals(
            len(response_data.get('points')),
            1,
            'Incorrect number of data points in returned data'
        )
        self.assertEquals(
            response_data.get('delta'),
            0,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_daily_multiple_reworks(self):
        self.setup_useable_logged_history(-7)
        self.setup_useable_logged_history()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': '',
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': ''
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        self.assertEquals(
            len(response_data.get('labels')),
            8,
            'Incorrect number of labels in returned data'
        )
        self.assertEquals(
            len(response_data.get('points')),
            8,
            'Incorrect number of data points in returned data'
        )
        self.assertEquals(
            response_data.get('delta'),
            7,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_weekly(self):
        self.setup_useable_logged_history(-30)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': '',
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': ''
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        assert (
            len(response_data.get('labels')) > 4 and
            len(response_data.get('labels')) < 7
        ), 'Incorrect number of labels in returned data'
        assert (
            len(response_data.get('points')) > 4 and
            len(response_data.get('points')) < 7
        ), 'Incorrect number of data points in returned data'
        self.assertEquals(
            response_data.get('delta'),
            30,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_weekly_with_start_and_end(self):
        self.setup_useable_logged_history()
        use_today = '%d-%d-%d' % (
            datetime.now().year,
            datetime.now().month,
            datetime.now().day
        )
        today = datetime.now() - timedelta(days=28)
        use_date = '%d-%d-%d' % (today.year, today.month, today.day)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': use_today,
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': use_date
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        self.assertEquals(
            len(response_data.get('labels')),
            5,
            'Incorrect number of labels in returned data'
        )
        self.assertEquals(
            len(response_data.get('points')),
            5,
            'Incorrect number of data points in returned data'
        )
        self.assertEquals(
            response_data.get('delta'),
            28,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_weekly_with_end(self):
        self.setup_useable_logged_history()
        today = datetime.now() + timedelta(days=28)
        use_date = '%d-%d-%d' % (today.year, today.month, today.day)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': use_date,
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': ''
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        self.assertEquals(
            len(response_data.get('labels')),
            5,
            'Incorrect number of labels in returned data'
        )
        self.assertEquals(
            len(response_data.get('points')),
            5,
            'Incorrect number of data points in returned data'
        )
        self.assertEquals(
            response_data.get('delta'),
            27,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_weekly_with_start_dates(self):
        today = datetime.now() + timedelta(days=-28)
        use_date = '%d-%d-%d' % (today.year, today.month, today.day)
        self.setup_useable_logged_history()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': '',
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': use_date
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        self.assertEquals(
            len(response_data.get('labels')),
            5,
            'Incorrect number of labels in returned data'
        )
        self.assertEquals(
            len(response_data.get('points')),
            5,
            'Incorrect number of data points in returned data'
        )
        self.assertEquals(
            response_data.get('delta'),
            28,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_weekly_with_multiple_actions(self):
        self.setup_useable_logged_history(-28)
        self.setup_useable_logged_history()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': '',
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': ''
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        self.assertEquals(
            len(response_data.get('labels')),
            5,
            'Incorrect number of labels in returned data'
        )
        self.assertEquals(
            len(response_data.get('points')),
            5,
            'Incorrect number of data points in returned data'
        )
        self.assertEquals(
            response_data.get('delta'),
            28,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_monthly(self):
        self.setup_useable_logged_history()
        today = datetime.now() - timedelta(days=65)
        use_date = '%d-%d-%d' % (today.year, today.month, today.day)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': '',
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': use_date
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        assert(
            len(response_data.get('labels')) > 2 and
            len(response_data.get('labels')) < 5
        ), 'Incorrect number of labels in returned data'
        assert(
            len(response_data.get('points')) > 2 and
            len(response_data.get('points')) < 5
        ), 'Incorrect number of data points in returned data'
        self.assertEquals(
            response_data.get('delta'),
            65,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_monthly_with_start_and_end(self):
        self.setup_useable_logged_history()
        use_today = '%d-%d-%d' % (
            datetime.now().year,
            datetime.now().month,
            datetime.now().day
        )
        today = datetime.now() - timedelta(days=65)
        use_date = '%d-%d-%d' % (today.year, today.month, today.day)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': use_today,
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': use_date
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        assert(
            len(response_data.get('labels')) > 2 and
            len(response_data.get('labels')) < 5
        ), 'Incorrect number of labels in returned data'
        assert(
            len(response_data.get('points')) > 2 and
            len(response_data.get('points')) < 5
        ), 'Incorrect number of data points in returned data'
        self.assertEquals(
            response_data.get('delta'),
            65,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_monthly_with_end(self):
        self.setup_useable_logged_history()
        today = datetime.now() + timedelta(days=65)
        use_date = '%d-%d-%d' % (today.year, today.month, today.day)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': use_date,
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': ''
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        assert(
            len(response_data.get('labels')) > 2 and
            len(response_data.get('labels')) < 5
        ), 'Incorrect number of labels in returned data'
        assert(
            len(response_data.get('points')) > 2 and
            len(response_data.get('points')) < 5
        ), 'Incorrect number of data points in returned data'
        assert(
            response_data.get('delta') > 63 and
            response_data.get('delta') < 66
        ), 'Incorrect delta returned'
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_monthly_no_dates(self):
        self.setup_useable_logged_history(-65)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': '',
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': ''
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        assert(
            len(response_data.get('labels')) > 2 and
            len(response_data.get('labels')) < 5
        ), 'Incorrect number of labels in returned data'
        assert(
            len(response_data.get('points')) > 2 and
            len(response_data.get('points')) < 5
        ), 'Incorrect number of data points in returned data'
        self.assertEquals(
            response_data.get('delta'),
            65,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_monthly_multiple_reworks(self):
        self.setup_useable_logged_history(-65)
        self.setup_useable_logged_history()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': '',
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': ''
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        assert(
            len(response_data.get('labels')) > 2 and
            len(response_data.get('labels')) < 5
        ), 'Incorrect number of labels in returned data'
        assert(
            len(response_data.get('points')) > 2 and
            len(response_data.get('points')) < 5
        ), 'Incorrect number of data points in returned data'
        self.assertEquals(
            response_data.get('delta'),
            65,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_monthly_by_user(self):
        self.setup_useable_logged_history(-65)
        self.setup_useable_logged_history()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': '',
                'csrf_token': token,
                'search_on': 'bobo1234',
                'Appname': '',
                'graph_key': 'username',
                'key': 'username',
                'Completed At-start': ''
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        assert(
            len(response_data.get('labels')) > 2 and
            len(response_data.get('labels')) < 5
        ), 'Incorrect number of labels in returned data'
        assert(
            len(response_data.get('points')) > 2 and
            len(response_data.get('points')) < 5
        ), 'Incorrect number of data points in returned data'
        self.assertEquals(
            response_data.get('delta'),
            65,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_monthly_multiple_data_points(self):
        self.setup_useable_logged_history()
        end_day = datetime.now() + timedelta(days=1)
        end_time = '%d-%d-%d' % (end_day.year, end_day.month, end_day.day)
        self.setup_useable_logged_history(-180)
        self.setup_useable_logged_history(-65)
        self.setup_useable_logged_history()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': end_time,
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': ''
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        assert(
            len(response_data.get('labels')) > 5 and
            len(response_data.get('labels')) < 8
        ), 'Incorrect number of labels in returned data'
        assert(
            len(response_data.get('points')) > 5 and
            len(response_data.get('points')) < 8
        ), 'Incorrect number of data points in returned data'
        self.assertEquals(
            response_data.get('delta'),
            180,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_weekly_multiple_data_points(self):
        self.setup_useable_logged_history()
        end_day = datetime.now() + timedelta(days=1)
        end_time = '%d-%d-%d' % (end_day.year, end_day.month, end_day.day)
        self.setup_useable_logged_history(-42)
        self.setup_useable_logged_history(-14)
        self.setup_useable_logged_history()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': end_time,
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': ''
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        self.assertEquals(
            len(response_data.get('labels')),
            7,
            'Incorrect number of labels in returned data'
        )
        self.assertEquals(
            len(response_data.get('points')),
            7,
            'Incorrect number of data points in returned data'
        )
        self.assertEquals(
            response_data.get('delta'),
            42,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_weekly_across_years(self):
        start_time = '2014-01-10'
        self.db.history.insert(
            {
                'username': 'bobo1234',
                'ddi': '123456',
                'details': {
                    'description': 'Retrieve a listing of the feed catalog',
                    'doc_url': (
                        'http://docs.rackspace.com/cloud-feeds/api/v1.0/feeds-'
                        'getting-started/content/Cloud_Feeds_Catalog.html'
                    ),
                    'id': '53e50582192a8b6a41d06d3f',
                    'title': 'Retrieve Feed Catalog'
                },
                'region': 'dfw',
                'product': 'Cloud Feeds',
                'request': {
                    'url': 'https://dfw.feeds.api.rackspacecloud.com/123456/',
                    'verb': 'GET',
                    'data': None
                },
                'response': {
                    'body': None,
                    'headers': {
                        'content-length': '510',
                        'via': '1.1 Repose (Repose/5.0.2)',
                        'content-language': 'en-US',
                        'content-encoding': 'gzip',
                        'accept-ranges': 'bytes',
                        'vary': 'Accept-Encoding',
                        'x-newrelic-app-data': 'misc_data',
                        'server': 'Jetty(8.y.z-SNAPSHOT)',
                        'last-modified': 'Tue, 29 Jul 2014 17:17:46 GMT',
                        'connection': 'Keep-Alive',
                        'etag': 'W/\"5406-1406654266000\"',
                        'date': 'Fri, 08 Aug 2014 19:48:27 GMT',
                        'content-type': 'application/xml;charset=UTF-8'
                    },
                    'code': 200
                },
                'completed_at': parser.parse(start_time)
            }
        )
        end_time = '2014-02-10'
        self.db.history.insert(
            {
                'username': 'bobo1234',
                'ddi': '123456',
                'details': {
                    'description': 'Retrieve a listing of the feed catalog',
                    'doc_url': (
                        'http://docs.rackspace.com/cloud-feeds/api/v1.0/feeds-'
                        'getting-started/content/Cloud_Feeds_Catalog.html'
                    ),
                    'id': '53e50582192a8b6a41d06d3f',
                    'title': 'Retrieve Feed Catalog'
                },
                'region': 'dfw',
                'product': 'Cloud Feeds',
                'request': {
                    'url': 'https://dfw.feeds.api.rackspacecloud.com/123456/',
                    'verb': 'GET',
                    'data': None
                },
                'response': {
                    'body': None,
                    'headers': {
                        'content-length': '510',
                        'via': '1.1 Repose (Repose/5.0.2)',
                        'content-language': 'en-US',
                        'content-encoding': 'gzip',
                        'accept-ranges': 'bytes',
                        'vary': 'Accept-Encoding',
                        'x-newrelic-app-data': 'misc_data',
                        'server': 'Jetty(8.y.z-SNAPSHOT)',
                        'last-modified': 'Tue, 29 Jul 2014 17:17:46 GMT',
                        'connection': 'Keep-Alive',
                        'etag': 'W/\"5406-1406654266000\"',
                        'date': 'Fri, 08 Aug 2014 19:48:27 GMT',
                        'content-type': 'application/xml;charset=UTF-8'
                    },
                    'code': 200
                },
                'completed_at': parser.parse(end_time)
            }
        )
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': end_time,
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': '2013-12-20'
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        self.assertEquals(
            len(response_data.get('labels')),
            9,
            'Incorrect number of labels in returned data'
        )
        self.assertEquals(
            len(response_data.get('points')),
            9,
            'Incorrect number of data points in returned data'
        )
        self.assertEquals(
            response_data.get('delta'),
            52,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_daily_multiple_data_points(self):
        self.setup_useable_logged_history()
        end_day = datetime.now() + timedelta(days=1)
        end_time = '%d-%d-%d' % (end_day.year, end_day.month, end_day.day)
        self.setup_useable_logged_history(-14)
        self.setup_useable_logged_history(-7)
        self.setup_useable_logged_history()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': end_time,
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': ''
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        self.assertEquals(
            len(response_data.get('labels')),
            16,
            'Incorrect number of labels in returned data'
        )
        self.assertEquals(
            len(response_data.get('points')),
            16,
            'Incorrect number of data points in returned data'
        )
        self.assertEquals(
            response_data.get('delta'),
            14,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_for_year_ago(self):
        start_day = datetime.now() + timedelta(days=-366)
        start_time = '%d-%d-%d' % (
            start_day.year,
            start_day.month,
            start_day.day
        )
        self.setup_useable_logged_history(-365)
        self.setup_useable_logged_history(-7)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': '',
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': start_time
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        assert len(response_data.get('labels')) in [13, 14], (
            'Incorrect number of labels in returned data'
        )
        assert len(response_data.get('points')) in [13, 14], (
            'Incorrect number of data points in returned data'
        )
        self.assertEquals(
            response_data.get('delta'),
            366,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_trend_for_start_date_in_other_year(self):
        start_day = datetime.now() + timedelta(days=-366)
        start_time = '%d-%d-%d' % (
            start_day.year, start_day.month, start_day.day
        )
        self.setup_useable_logged_history(-7)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': '',
                'csrf_token': token,
                'search_on': 'DFW',
                'graph_key': 'region',
                'key': 'region',
                'Appname': '',
                'Completed At-start': start_time
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'labels',
            response.data,
            'Did not find returned labels from trend generate'
        )
        self.assertIn(
            'points',
            response.data,
            'Did not find returned data points from trend generate'
        )
        response_data = json.loads(response.data)
        assert len(response_data.get('labels')) in [13, 14], (
            'Incorrect number of labels in returned data'
        )
        assert len(response_data.get('points')) in [13, 14], (
            'Incorrect number of data points in returned data'
        )
        self.assertEquals(
            response_data.get('delta'),
            366,
            'Incorrect delta returned'
        )
        self.assertEquals(
            len(response_data.get('points')),
            len(response_data.get('labels')),
            'Data labels and data points do not have the same number of values'
        )
        self.teardown_app_data()

    def test_engine_admin_report_fields_setup(self):
        self.db.reporting.remove()
        self.setup_misc_fields()
        self.setup_useable_logged_history()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            (
                '<select class="form-control" id="Misc Select" name="Misc '
                'Select"><option value=""></option><option value="Select 1">'
                'Select 1</option><option value="Select 2">Select 2</option>'
                '</select>'
            ),
            response.data,
            'Could not find generated select with defined options'
        )
        self.assertIn(
            (
                '<select class="form-control" id="Rework Step" name="Rework '
                'Step"><option value=""></option><option value="1">True'
                '</option><option value="0">False</option></select>'
            ),
            response.data,
            'Could not find generated boolean select'
        )
        self.assertIn(
            (
                '<input id="Misc Checkbox" name="Misc Checkbox" '
                'type="checkbox" value="y">'
            ),
            response.data,
            'Could not find generated boolean checkbox'
        )
        self.assertIn(
            (
                '<input class="form-control" id="Misc Text" name="Misc Text"'
                ' type="text" value="">'
            ),
            response.data,
            'Could not find generated text field select'
        )
        self.teardown_app_data()

    """ Edge and Misc Tests """

    def test_engine_admin_generate_full_query(self):
        self.setup_useable_logged_history()
        self.setup_all_report_fields()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'region': 'DFW',
                'Completed At-end': '2014-04-01',
                'csrf_token': token,
                'Completed At-start': '2014-03-01',
                'Billable': '1',
                'Waive Billable': 'y'
            }
            response = c.post(
                '/engine/generate',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            '<h3>Query Results - (0)</h3>',
            response.data,
            'Did not find the correct return data in response'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_only_start_time(self):
        self.setup_useable_logged_history()
        self.setup_all_report_fields()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': '',
                'csrf_token': token,
                'Appname': '',
                'Completed At-start': '2014-03-01'
            }
            response = c.post(
                '/engine/generate',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            '<h3>Query Results - (1)</h3>',
            response.data,
            'Did not find the correct return data in response'
        )
        self.teardown_app_data()

    def test_engine_admin_generate_only_end_time(self):
        self.setup_useable_logged_history()
        self.setup_all_report_fields()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': '2014-03-01',
                'csrf_token': token,
                'Appname': '',
                'Completed At-start': ''
            }
            response = c.post(
                '/engine/generate',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            '<h3>Query Results - (0)</h3>',
            response.data,
            'Did not find the correct return data in response'
        )
        self.teardown_app_data()

    def test_engine_admin_setup_manage_fields_nested_dict(self):
        self.setup_recorded_item_edge()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/fields/add')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'description': 'Test',
                'data_type': 'text',
                'field_display_data': '',
                'graphable': False,
                'searchable': True,
                'field_display': 'TextField',
                'field_name': 'test_dict.sso',
                'submit': 'Submit'
            }
            response = c.post(
                '/engine/fields/add',
                data=data,
                follow_redirects=True
            )
        self.assertIn(
            'Field was successfully added',
            response.data,
            'Incorrect flash message after add of field'
        )
        found = self.db.reporting.find_one()
        assert found, 'Added field was not found in db'
        self.teardown_app_data()

    def test_engine_reporting_trend_nested_dict(self):
        self.setup_useable_logged_history()
        self.setup_useable_logged_history(7)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/fields/add')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': '',
                'csrf_token': token,
                'search_on': 'bobo1234',
                'Appname': '',
                'graph_key': 'username',
                'key': 'username',
                'Completed At-start': ''
            }
            response = c.post(
                '/engine/generate/trend',
                data=json.dumps(data),
                content_type='application/json'
            )

        results = json.loads(response.data)
        self.assertEquals(
            len(results.get('points')),
            2,
            'Incorrect number of data points found'
        )
        self.assertEquals(
            results.get('title'),
            'bobo1234 : Trending Report',
            'Incorrect title was created'
        )
        self.teardown_app_data()

    """ CSV """

    def test_engine_generate_csv(self):
        self.setup_useable_logged_history()
        self.setup_all_report_fields()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'Status': '',
                'Completed At-end': '',
                'csrf_token': token,
                'Appname': '',
                'Completed At-start': ''
            }
            response = c.post(
                '/engine/generate/csv',
                data=data
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            '"bobo1234","123456","DFW","Cloud Feeds"',
            response.data,
            'Did not find the correct return data in response'
        )
        self.teardown_app_data()

    def test_engine_generate_csv_with_no_form(self):
        self.setup_useable_logged_history()
        self.setup_all_report_fields()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/')
            response = c.post(
                '/engine/generate/csv'
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )

        print response.data

        self.assertIn(
            '"bobo1234","123456","DFW","Cloud Feeds"',
            response.data,
            'Did not find the correct return data in response'
        )
        self.teardown_app_data()

    """ View Item """

    def test_engine_view_item_display(self):
        self.setup_useable_logged_history()
        found = self.db.history.find_one()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/view/%s' % found.get('_id'))

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Call Information',
            response.data,
            'Could not find modal title in display'
        )
        self.assertIn(
            'http://docs.rackspace.com/cloud-feeds/api/v1.0/feeds-getting',
            response.data,
            'Could not find ticket link in display data'
        )
        self.teardown_app_data()

    def test_engine_view_item_display_no_data(self):
        self.setup_useable_logged_history()
        found = self.db.history.find_one()
        self.db.history.remove()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/engine/view/%s' % found.get('_id'))
            assert response._status_code == 302, (
                'Invalid response code %s' % response._status_code
            )
            response = c.get(
                '/engine/view/%s' % found.get('_id'),
                follow_redirects=True
            )
        self.assertIn(
            'Item could not be found to display',
            response.data,
            'Could not find correct error message displayed after redirect'
        )
        self.teardown_app_data()
