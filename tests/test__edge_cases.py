import pitchfork
import flask
import unittest
import happymongo
import json
import urlparse
import re
import mock


from datetime import datetime, timedelta
from dateutil import tz
from uuid import uuid4
from bson.objectid import ObjectId


class EdgeCasesTests(unittest.TestCase):
    def setUp(self):
        pitchfork.app.config['TESTING'] = True
        if not re.search('_test', pitchfork.app.config['MONGO_DATABASE']):
            test_db = '%s_test' % pitchfork.app.config['MONGO_DATABASE']
            pitchfork.app.config['MONGO_DATABASE'] = test_db

        self.app = pitchfork.app.test_client()
        pitchfork.mongo, pitchfork.db = happymongo.HapPyMongo(pitchfork.app)
        self.app.get('/')

    def teardown_app_data(self):
        pitchfork.db.sessions.remove()
        pitchfork.db.settings.remove()
        pitchfork.db.forms.remove()
        pitchfork.db.api_settings.remove()
        pitchfork.db.cloud_identity.remove()
        pitchfork.db.queues.remove()

    def setup_user_login(self, sess):
        sess['username'] = 'test'
        sess['csrf_token'] = 'csrf_token'
        sess['role'] = 'logged_in'
        sess['_permanent'] = True
        sess['ddi'] = '654846'
        sess['cloud_token'] = 'b26dac35f5fa4993b0732a4227687695'

    def setup_admin_login(self, sess):
        sess['username'] = 'oldarmyc'
        sess['csrf_token'] = 'csrf_token'
        sess['role'] = 'administrators'
        sess['_permanent'] = True
        sess['ddi'] = '654846'
        sess['cloud_token'] = 'b26dac35f5fa4993b0732a4227687695'

    def setup_useable_api_call(self, tested=None):
        data = {
            'api_uri': '{ddi}/groups',
            'doc_url': 'http://docs.rackspace.com',
            'short_description': 'Test API Call',
            'title': 'Test Call',
            'verb': 'GET',
            'data_object': (
                '{\r\n    \"auth\": {\r\n        \"RAX-KSKEY:apiKey'
                'Credentials\": {\r\n            \"username\": \"{u'
                'sername}\",\r\n            \"apiKey\": \"{api_key}'
                '\"\r\n        }\r\n    }\r\n}'
            ),
            'use_data': True,
            'remove_token': True,
            'required_key': True,
            'required_key_name': 'required_key',
            'required_key_type': 'dict',
            'add_to_header': True,
            'custom_header_value': 'Custom Value',
            'custom_header_key': 'Custom Key',
            'variables': [
                {
                    'field_type': 'text',
                    'description': 'User',
                    'required': True,
                    'field_display_data': '',
                    'id_value': 0,
                    'field_display': 'TextField',
                    'variable_name': 'username'
                }, {
                    'field_type': 'text',
                    'description': 'Key',
                    'required': True,
                    'field_display_data': '',
                    'id_value': 1,
                    'field_display': 'TextField',
                    'variable_name': 'api_key'
                }
            ]
        }
        if tested:
            data['tested'] = True

        insert = pitchfork.db.cloud_identity.insert(data)
        return insert

    def setup_useable_api_call_with_variables(self):
        data = {
            'api_uri': '{ddi}/test',
            'doc_url': 'http://docs.rackspace.com',
            'short_description': 'Test API Call',
            'title': 'Test Call',
            'verb': 'GET',
            'use_data': True,
            'required_key': True,
            'required_key_name': 'required_key',
            'required_key_type': 'list',
            'data_object': (
                '[{"var_1": "{test_var_value}","test_nest": {"var_2": "{'
                'test_var_value_2}"},"test_list_dict": [{"var_3": "{test_'
                'var_value_3}"}],"test_list": ["{test_var_value_4}","{test_'
                'var_value_7}","{test_var_value_8}","{test_var_value_9}"],"t'
                'est_list_key_value": [{"{test_var_value_6}": "{test_var_val'
                'ue_5}"}]}]'
            ),
            'variables': [
                {
                    'field_type': 'text',
                    'description': 'Test Variable',
                    'required': True,
                    'field_display_data': '',
                    'id_value': 0,
                    'field_display': 'TextField',
                    'variable_name': 'test_var_value'
                }, {
                    'field_type': 'integer',
                    'description': 'Test Var 2',
                    'required': False,
                    'field_display_data': '',
                    'id_value': 1,
                    'field_display': 'TextField',
                    'variable_name': 'test_var_value_2'
                }, {
                    'field_type': 'boolean',
                    'description': 'Test Var 3',
                    'required': False,
                    'field_display_data': '',
                    'id_value': 2,
                    'field_display': 'TextField',
                    'variable_name': 'test_var_value_3'
                }, {
                    'field_type': 'float',
                    'description': 'Test Var 4',
                    'required': False,
                    'field_display_data': '',
                    'id_value': 3,
                    'field_display': 'TextField',
                    'variable_name': 'test_var_value_4'
                }, {
                    'field_type': 'boolean',
                    'description': 'Test Var 5',
                    'required': False,
                    'field_display_data': '',
                    'id_value': 4,
                    'field_display': 'TextField',
                    'variable_name': 'test_var_value_5'
                }, {
                    'field_type': 'text',
                    'description': 'Test Var 6',
                    'required': False,
                    'field_display_data': '',
                    'id_value': 5,
                    'field_display': 'TextField',
                    'variable_name': 'test_var_value_6'
                }, {
                    'field_type': 'integer',
                    'description': 'Test Var 7',
                    'required': False,
                    'field_display_data': '',
                    'id_value': 6,
                    'field_display': 'TextField',
                    'variable_name': 'test_var_value_7'
                }, {
                    'field_type': 'boolean',
                    'description': 'Test Var 8',
                    'required': False,
                    'field_display_data': '',
                    'id_value': 7,
                    'field_display': 'TextField',
                    'variable_name': 'test_var_value_8'
                }, {
                    'field_type': 'text',
                    'description': 'Test Var 9',
                    'required': False,
                    'field_display_data': '',
                    'id_value': 8,
                    'field_display': 'TextField',
                    'variable_name': 'test_var_value_9'
                }
            ]
        }

        insert = pitchfork.db.queues.insert(data)
        return insert

    def retrieve_csrf_token(self, data, variable=None):
        temp = re.search('id="csrf_token"(.+?)>', data)
        token = None
        if temp:
            temp_token = re.search('value="(.+?)"', temp.group(1))
            if temp_token:
                token = temp_token.group(1)

        if variable:
            var_temp = re.search('id="variable_0-csrf_token"(.+?)>', data)
            if var_temp:
                var_token = re.search('value="(.+?)"', var_temp.group(1))
                if var_token:
                    return token, var_token.group(1)
                else:
                    return token, None
            else:
                return token, None
        else:
            return token

    """
        Edge Case or Complex tests start
        Using Autoscale as the product since all products act the same
    """

    def test_misc_post_call_complex_dict(self):
        api_id = self.setup_useable_api_call()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'api_verb': 'POST',
                'username': 'username',
                'testing': False,
                'api_url': '/tokens',
                'data_center': 'us',
                'api_id': str(api_id),
                'ddi': '123456',
                'api_token': 'token',
                'api_key': 'api_key'
            }
            with mock.patch('requests.get') as patched_get:
                type(patched_get.return_value).content = mock.PropertyMock(
                    return_value='{"success": [1, 2], "made": [3, 4]}'
                )
                type(patched_get.return_value).status_code = mock.PropertyMock(
                    return_value=200
                )
                type(patched_get.return_value).headers = mock.PropertyMock(
                    return_value=(
                        '{"via": "1.1 Repose (Repose/2.12)",\
                        "x-response-id": "response_id",\
                        "transfer-encoding": "chunked",\
                        "server": "Jetty(8.0.y.z-SNAPSHOT)",\
                        "date": "Tue, 18 Mar 2014 19:52:26 GMT",\
                        "content-type": "application/json"}'
                    )
                )
                response = c.post(
                    '/identity/api_call/process',
                    data=json.dumps(data),
                    content_type='application/json'
                )

        data = json.loads(response.data)
        assert data.get('response_code'), 'No response code received'
        assert data.get('api_url'), 'API URL was not found'
        assert data.get('response_headers'), (
            'No response headers were received'
        )
        assert data.get('response_body'), 'No response content was received'
        assert data.get('request_headers'), 'No request headers was received'
        assert data.get('data_package'), (
            'No response data package was received'
        )
        self.teardown_app_data()

    def test_misc_post_call_complex_list(self):
        api_id = self.setup_useable_api_call_with_variables()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'api_verb': 'GET',
                'username': 'username',
                'testing': False,
                'api_url': '/tokens',
                'data_center': 'us',
                'api_id': str(api_id),
                'ddi': '123456',
                'token': 'Test Token',
                'test_var_value': 'test text',
                'test_var_value_2': '99',
                'test_var_value_3': 'TRUE',
                'test_var_value_4': '9.5',
                'test_var_value_5': 'FALSE',
                'test_var_value_6': '',
                'test_var_value_7': '9',
                'test_var_value_8': 'FALSE',
                'test_var_value_9': 'Test'
            }

            with mock.patch('requests.get') as patched_get:
                type(patched_get.return_value).content = mock.PropertyMock(
                    return_value='{"success": [1, 2], "made": [3, 4]}'
                )
                type(patched_get.return_value).status_code = mock.PropertyMock(
                    return_value=200
                )
                type(patched_get.return_value).headers = mock.PropertyMock(
                    return_value=(
                        '{"via": "1.1 Repose (Repose/2.12)",\
                        "x-response-id": "response_id",\
                        "transfer-encoding": "chunked",\
                        "server": "Jetty(8.0.y.z-SNAPSHOT)",\
                        "date": "Tue, 18 Mar 2014 19:52:26 GMT",\
                        "content-type": "application/json"}'
                    )
                )
                response = c.post(
                    '/queues/api_call/process',
                    data=json.dumps(data),
                    content_type='application/json'
                )

        data = json.loads(response.data)
        assert data.get('response_code'), 'No response code received'
        assert data.get('api_url'), 'API URL was not found'
        assert data.get('response_headers'), (
            'No response headers were received'
        )
        assert data.get('response_body'), 'No response content was received'
        assert data.get('request_headers'), 'No request headers was received'
        assert data.get('data_package'), (
            'No response data package was received'
        )
        self.teardown_app_data()

    def test_misc_browse_index_with_calls(self):
        self.setup_useable_api_call(True)
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/')

        self.assertIn(
            '<h4>Test Call - Identity</h4>',
            response.data,
            'Could not find correct call for front most accessed'
        )
        self.teardown_app_data()

    def test_misc_search_for_valid_call(self):
        self.setup_useable_api_call(True)
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'search_string': 'Test API'
            }
            response = c.post(
                '/search',
                data=json.dumps(data),
                content_type='application/json'
            )

        self.assertIn(
            '<h4>Test Call - Identity</h4>',
            response.data,
            'Could not find correct html after search'
        )
        self.teardown_app_data()

    def test_misc_search_for_call_no_data(self):
        pitchfork.db.api_settings.remove()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'search_string': 'Test API'
            }
            response = c.post(
                '/search',
                data=json.dumps(data),
                content_type='application/json'
            )

        self.assertIn(
            'No Results Found',
            response.data,
            'Could not find correct message after no items'
        )
        self.teardown_app_data()

    def test_misc_search_for_call_bad_search(self):
        pitchfork.db.api_settings.update(
            {
            }, {
                '$set': {
                    'active_products': []
                }
            }
        )
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'search_string': 'Test API'
            }
            response = c.post(
                '/search',
                data=json.dumps(data),
                content_type='application/json'
            )

        self.assertIn(
            'No Active Products to Search',
            response.data,
            'Could not find correct message after no active products'
        )
        self.teardown_app_data()

    def test_misc_post_call_parse_through_html(self):
        api_id = self.setup_useable_api_call_with_variables()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'api_verb': 'GET',
                'username': 'username',
                'testing': False,
                'api_url': '/tokens',
                'data_center': 'us',
                'api_id': str(api_id),
                'ddi': '123456',
                'token': 'Test Token',
                'test_var_value': 'test text',
            }
            with mock.patch('requests.get') as patched_get:
                type(patched_get.return_value).content = mock.PropertyMock(
                    return_value='<html><body><p>Inner Code</p></body></html>'
                )
                type(patched_get.return_value).status_code = mock.PropertyMock(
                    return_value=200
                )
                type(patched_get.return_value).headers = mock.PropertyMock(
                    return_value=(
                        '{"via": "1.1 Repose (Repose/2.12)",\
                        "x-response-id": "response_id",\
                        "transfer-encoding": "chunked",\
                        "server": "Jetty(8.0.y.z-SNAPSHOT)",\
                        "date": "Tue, 18 Mar 2014 19:52:26 GMT",\
                        "content-type": "application/json"}'
                    )
                )
                response = c.post(
                    '/queues/api_call/process',
                    data=json.dumps(data),
                    content_type='application/json'
                )

        data = json.loads(response.data)
        assert data.get('response_code'), 'No response code received'
        assert data.get('api_url'), 'API URL was not found'
        assert data.get('response_headers'), (
            'No response headers were received'
        )
        assert data.get('response_body'), 'No response content was received'
        assert data.get('request_headers'), 'No request headers was received'
        assert data.get('data_package'), (
            'No response data package was received'
        )
        self.teardown_app_data()

    def test_pf_add_call_with_variables(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/autoscale/manage/api/add'
            )
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'title': 'Add Call',
                'doc_url': 'http://docs.rackspace.com',
                'verb': 'GET',
                'api_uri': '/queues/{queue_name}/claims/{claim_id}',
                'variable_0-field_display': 'TextField',
                'variable_0-field_type': 'text',
                'variable_0-description': 'Name of Queue',
                'variable_0-variable_name': 'queue_name',
                'variable_0-required': 'y',
                'variable_0-id_value': '0',
                'variable_1-variable_name': 'claim_id',
                'variable_1-description': 'Claim ID',
                'variable_1-field_type': 'text',
                'variable_1-required': 'y',
                'variable_1-id_value': '1',
                'variable_1-field_display': 'TextField',
                'variable_2-variable_name': 'claim_ttl',
                'variable_2-field_type': 'integer',
                'variable_2-description': 'Description',
                'variable_2-field_display': 'TextField',
                'variable_2-id_value': '2',
                'data_object': '{\r\n    "ttl": "{claim_ttl}"\r\n}',
                'tested': 'y'
            }
            response = c.post(
                '/queues/manage/api/add',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            (
                'API Call was successfully added'
            ),
            response.data,
            'Bad message when submitting good call'
        )
        found_call = pitchfork.db.queues.find_one(
            {
                'title': 'Add Call'
            }
        )
        assert found_call, 'Could not find added api call'
        self.teardown_app_data()

    """ End Misc Tests """
