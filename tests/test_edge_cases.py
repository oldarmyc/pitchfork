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


import unittest
import json
import urlparse
import re
import mock


class EdgeCasesTests(unittest.TestCase):
    def setUp(self):
        check_db = re.search('_test', config.MONGO_DATABASE)
        if not check_db:
            test_db = '%s_test' % config.MONGO_DATABASE
        else:
            test_db = config.MONGO_DATABASE

        self.pitchfork, self.db = create_app(test_db)
        self.app = self.pitchfork.test_client()
        self.app.get('/')

    def tearDown(self):
        self.db.sessions.remove()
        self.db.settings.remove()
        self.db.forms.remove()
        self.db.api_settings.remove()
        self.db.cloud_identity.remove()
        self.db.queues.remove()

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
            'change_content_type': 'True',
            'custom_content_type': 'application/octet-stream',
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

        insert = self.db.autoscale.insert(data)
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
                '[{"var_1": "{test_var_value}", "var_3": 1, "var_4": '
                '"test_value", "test_nest": {"var_2": "{test_var_value_2}"},'
                '"test_list_dict": [{"var_3": "{test_var_value_3}"}],'
                '"test_list": ["{test_var_value_4}","{test_var_value_7}",'
                '"{test_var_value_8}","{test_var_value_9}"],'
                '"test_list_key_value": [{"{test_var_value_6}": "{test_var_val'
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
        insert = self.db.autoscale.insert(data)
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

    def test_misc_post_call_complex_dict(self):
        api_id = self.setup_useable_api_call()
        with self.app as c:
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
                    '/autoscale/api/call/process',
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
        self.assertIn(
            'octet-stream',
            data.get('request_headers'),
            'Could not find appropriate custom headers'
        )

    def test_misc_post_call_complex_list(self):
        api_id = self.setup_useable_api_call_with_variables()
        with self.app as c:
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
                    '/autoscale/api/call/process',
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

    def test_misc_post_call_parse_through_html(self):
        api_id = self.setup_useable_api_call_with_variables()
        with self.app as c:
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
                    '/autoscale/api/call/process',
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

    def test_pf_add_call_with_variables(self):
        self.db.autoscale.remove()
        with self.app as c:
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
                '/autoscale/manage/api/add',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            (
                'API Call was added successfully'
            ),
            response.data,
            'Bad message when submitting good call'
        )
        found_call = self.db.autoscale.find_one(
            {
                'title': 'Add Call'
            }
        )
        assert found_call, 'Could not find added api call'

    def test_process_call_with_bad_call_id(self):
        api_id = self.setup_useable_api_call()
        self.db.autoscale.remove()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'api_verb': 'GET',
                'testing': False,
                'api_url': '{ddi}/groups',
                'api_token': 'test_token',
                'api_id': str(api_id),
                'ddi': '123456',
                'data_center': 'dfw',
                'testing': True
            }
            response = c.post(
                '/autoscale/api/call/process',
                data=json.dumps(data),
                content_type='application/json'
            )

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

    def test_process_call_with_bad_product(self):
        api_id = self.setup_useable_api_call()
        self.db.autoscale.remove()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'api_verb': 'GET',
                'testing': False,
                'api_url': '{ddi}/groups',
                'api_token': 'test_token',
                'api_id': str(api_id),
                'ddi': '123456',
                'data_center': 'dfw',
                'testing': True
            }
            response = c.post(
                '/BAD_PRODUCT/api/call/process',
                data=json.dumps(data),
                content_type='application/json'
            )

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

    def test_process_mock_call(self):
        api_id = self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'api_verb': 'GET',
                'api_url': '{ddi}/groups',
                'api_id': str(api_id),
                'ddi': '123456',
                'data_center': 'dfw',
                'mock': True
            }
            with mock.patch('requests.get') as patched_get:
                type(patched_get.return_value).content = mock.PropertyMock(
                    return_value='{"groups_links": [], "groups": []}'
                )
                type(patched_get.return_value).status_code = mock.PropertyMock(
                    return_value=200
                )
                type(patched_get.return_value).headers = mock.PropertyMock(
                    return_value=(
                        '{"via": "1.1 Repose (Repose/2.12)",'
                        '"x-response-id": "a10adb69-4d9f-4457-'
                        'bda4-e2429f334895",'
                        '"transfer-encoding": "chunked",'
                        '"server": "Jetty(8.0.y.z-SNAPSHOT)",'
                        '"date": "Tue, 18 Mar 2014 19:52:26 GMT",'
                        '"content-type": "application/json"}'
                    )
                )
                response = c.post(
                    '/autoscale/api/call/process',
                    data=json.dumps(data),
                    content_type='application/json'
                )

        data = json.loads(response.data)
        assert data.get('api_url'), 'API URL was not found'
        assert data.get('request_headers'), 'No request headers received'
        assert data.get('data_package'), 'No data package received'

    def test_manage_api_with_bad_product(self):
        self.setup_useable_api_call()
        self.db.autoscale.remove()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/BAD_PRODUCT/manage/api',)

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

    def test_manage_api_add_call_with_bad_product(self):
        self.setup_useable_api_call()
        self.db.autoscale.remove()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/BAD_PRODUCT/manage/api/add',)

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

    def test_manage_api_edit_call_with_bad_call_id(self):
        api_id = self.setup_useable_api_call()
        self.db.autoscale.remove()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/autoscale/manage/api/edit/%s' % api_id,
            )

        assert response._status_code == 302, (
            'Invalid response code %s' % response._status_code
        )
        location = response.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/autoscale/manage/api',
            'Invalid redirect location %s, expected "/"' % o.path
        )

    def test_manage_api_bad_action(self):
        api_id = self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/autoscale/manage/api/BAD_ACTION/%s' % api_id,
            )
            assert response._status_code == 302, (
                'Invalid response code %s' % response._status_code
            )
            response = c.get(
                '/autoscale/manage/api/BAD_ACTION/%s' % api_id,
                follow_redirects=True
            )

        self.assertIn(
            'Invalid action provided, so no action taken',
            response.data,
            'Found invalid message in return'
        )

    def test_manage_api_bad_product(self):
        api_id = self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/BAD_PRODUCT/manage/api/delete/%s' % api_id,
            )
            assert response._status_code == 302, (
                'Invalid response code %s' % response._status_code
            )
            response = c.get(
                '/BAD_PRODUCT/manage/api/delete/%s' % api_id,
                follow_redirects=True
            )

        self.assertIn(
            'Product was not found, so no action taken',
            response.data,
            'Found invalid message in return'
        )
