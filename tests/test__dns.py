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


class CloudDnsTests(unittest.TestCase):
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
        pitchfork.db.cloud_dns.remove()

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
            'variables': []
        }
        if tested:
            data['tested'] = 'True'

        insert = pitchfork.db.cloud_dns.insert(data)
        return insert

    def setup_useable_api_call_with_variables(self):
        data = {
            'api_uri': '{ddi}/groups',
            'doc_url': 'http://docs.rackspace.com',
            'short_description': 'Test API Call',
            'title': 'Test Call',
            'verb': 'GET',
            'use_data': True,
            'data_object': "{\r\n    \"test_var\": \"{test_var_value}\"\r\n}",
            'variables': [
                {
                    'field_type': 'text',
                    'description': 'Test Variable',
                    'required': True,
                    'field_display_data': '',
                    'id_value': 0,
                    'field_display': 'TextField',
                    'variable_name': 'test_var_value'
                }
            ]
        }

        insert = pitchfork.db.cloud_dns.insert(data)
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

    """ Product Management Autoscale - Perms Test """

    def test_pf_cloud_dns_manage_admin_perms(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/dns/manage')

        self.assertIn(
            'Manage Settings</h3>',
            response.data,
            'Did not find correct HTML on page'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_manage_admin_perms_no_settings(self):
        pitchfork.db.api_settings.remove()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/dns/manage')

        self.assertIn(
            'Manage Settings</h3>',
            response.data,
            'Did not find correct HTML on page'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_manage_user_perms(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            result = c.get('/dns/manage')

        assert result._status_code == 302, \
            'Invalid response code %s' % result._status_code

        location = result.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )
        self.teardown_app_data()

    """ Functional Tests """

    def test_pf_cloud_dns_manage_add_update(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/dcs')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'title': 'Test',
                'app_url': '/test',
                'url': 'http://us.test.com',
                'uk_url': 'http://us.test.com',
                'doc_url': 'http://doc.test.com',
                'require_dc': True,
                'active': True
            }
            response = c.post(
                '/dns/manage',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            (
                'Product variables successfully updated'
            ),
            response.data,
            'Incorrect flash message after add bad data'
        )
        api_settings = pitchfork.db.api_settings.find_one()
        cloud_dns = api_settings.get('cloud_dns')
        updated = False
        if cloud_dns.get('title') == 'Test':
            updated = True

        assert updated, 'Item was not updated successfully'
        self.teardown_app_data()

    def test_pf_cloud_dns_manage_add_update_disable(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/dcs')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'title': 'Test',
                'app_url': '/test',
                'url': 'http://us.test.com',
                'uk_url': 'http://us.test.com',
                'doc_url': 'http://doc.test.com',
                'require_dc': True
            }
            response = c.post(
                '/dns/manage',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            (
                'Product variables successfully updated'
            ),
            response.data,
            'Incorrect flash message after add bad data'
        )
        api_settings = pitchfork.db.api_settings.find_one()
        cloud_dns = api_settings.get('cloud_dns')
        updated = False
        if cloud_dns.get('title') == 'Test':
            updated = True

        assert updated, 'Item was not updated successfully'
        active_products = api_settings.get('active_products')
        not_active = False
        if not 'cloud_dns' in active_products:
            not_active = True

        assert not_active, 'Product was not removed from active products'
        self.teardown_app_data()

    def test_pf_cloud_dns_manage_add_bad_data(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'title': 'Test',
                'app_url': '/test',
                'url': 'http://us.test.com',
                'uk_url': 'http://us.test.com',
                'doc_url': 'http://doc.test.com',
                'require_dc': True,
                'active': True
            }
            response = c.post(
                '/dns/manage',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            (
                'Form validation error, please check the form and try again'
            ),
            response.data,
            'Incorrect flash message after add bad data'
        )
        self.teardown_app_data()

    """ Product API Management Autoscale - Perms Test """

    def test_pf_cloud_dns_manage_api_admin_perms(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/dns/manage/api')

        self.assertIn(
            '<h3>Manage API Calls</h3>',
            response.data,
            'Did not find correct HTML on page'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_manage_api_user_perms(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            result = c.get('/dns/manage/api')

        assert result._status_code == 302, \
            'Invalid response code %s' % result._status_code

        location = result.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )
        self.teardown_app_data()

    """ API Add """

    def test_pf_cloud_dns_manage_api_add_admin_perms(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/dns/manage/api/add')

        self.assertIn(
            '<h3>Add API Call</h3>',
            response.data,
            'Did not find correct HTML on page'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_manage_api_add_user_perms(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            result = c.get('/dns/manage/api/add')

        assert result._status_code == 302, \
            'Invalid response code %s' % result._status_code

        location = result.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_manage_api_add_admin_post_dupe_title(self):
        api_id = self.setup_useable_api_call()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/dns/manage/api/add'
            )
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'title': 'Test Call',
                'doc_url': 'http://docs.rackspace.com',
                'verb': 'GET',
                'api_uri': '{ddi}/groups'
            }
            response = c.post(
                '/dns/manage/api/add',
                data=data
            )

        self.assertIn(
            (
                'Duplicate title for API call already exists'
                ', please check the name and try again'
            ),
            response.data,
            'Bad message when submitting duplicate title'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_manage_api_add_admin_post_dupe_url(self):
        api_id = self.setup_useable_api_call()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/dns/manage/api/add'
            )
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'title': 'Dupe Call',
                'doc_url': 'http://docs.rackspace.com',
                'verb': 'GET',
                'api_uri': '{ddi}/groups'
            }
            response = c.post(
                '/dns/manage/api/add',
                data=data
            )

        self.assertIn(
            (
                'Duplicate API URI and Verb combination already exists, '
                'please check the URI and verb and try again'
            ),
            response.data,
            'Bad message when submitting duplicate url and verb'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_manage_api_add_admin_post_good(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/dns/manage/api/add'
            )
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'title': 'Add Call',
                'doc_url': 'http://docs.rackspace.com',
                'verb': 'GET',
                'api_uri': '{ddi}/groups'
            }
            response = c.post(
                '/dns/manage/api/add',
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
        found_call = pitchfork.db.cloud_dns.find_one(
            {
                'title': 'Add Call'
            }
        )
        assert found_call, 'Could not find added api call'
        self.teardown_app_data()

    """ Edit API Call """

    def test_pf_cloud_dns_manage_api_edit_user_perms(self):
        api_id = self.setup_useable_api_call()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            result = c.get(
                '/dns/manage/api/edit/%s' % api_id
            )

        assert result._status_code == 302, \
            'Invalid response code %s' % result._status_code

        location = result.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_manage_api_edit_admin_perms(self):
        api_id = self.setup_useable_api_call()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/dns/manage/api/edit/%s' % api_id
            )

        self.assertIn(
            '<h3>Edit API Call',
            response.data,
            'Invalid HTML found when browsing to edit'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_manage_api_edit_admin_perms_with_vars(self):
        api_id = self.setup_useable_api_call_with_variables()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/dns/manage/api/edit/%s' % api_id
            )

        self.assertIn(
            '<h3>Edit API Call',
            response.data,
            'Invalid HTML found when browsing to edit'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_manage_api_edit_admin_bad_post(self):
        api_id = self.setup_useable_api_call()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'api_uri': '{ddi}/groups',
                'doc_url': 'http://docs.rackspace.com',
                'short_description': 'Test API Call',
                'title': 'Test Call',
                'verb': 'GET',
                'variables': []
            }
            response = c.post(
                '/dns/manage/api/edit/%s' % api_id,
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Form validation error, please check the form and try again',
            response.data,
            'Incorrect flash message after add bad data'
        )
        self.assertIn(
            '<h3>Edit API Call',
            response.data,
            'Invalid HTML found when browsing to edit'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_manage_api_edit_admin_good_post(self):
        api_id = self.setup_useable_api_call()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/dns/manage/api/edit/%s' % api_id
            )
            token, var_token = self.retrieve_csrf_token(response.data, True)
            data = {
                'csrf_token': token,
                'title': 'Test Update Call',
                'short_description': 'Test Setup',
                'doc_url': 'http://docs.rackspace.com',
                'verb': 'GET',
                'api_uri': '{ddi}/groups'
            }
            response = c.post(
                '/dns/manage/api/edit/%s' % api_id,
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'API Call was successfully updated',
            response.data,
            'Incorrect flash message after successful edit'
        )
        self.assertIn(
            '<h3>Manage API Calls</h3>',
            response.data,
            'Invalid HTML found when browsing to edit'
        )
        calls = pitchfork.db.cloud_dns.find_one(
            {
                'title': 'Test Update Call'
            }
        )
        assert calls, 'Could not find updated call'
        self.teardown_app_data()

    """ Set testing for API Call """

    def test_pf_cloud_dns_manage_api_mark_tested(self):
        api_id = self.setup_useable_api_call()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/dns/manage/api/test/confirm/%s' % api_id,
                follow_redirects=True
            )

        self.assertIn(
            'API Call has been mark as tested',
            response.data,
            'Invalid response found after marking tested'
        )
        api_call = pitchfork.db.cloud_dns.find_one()
        tested = api_call.get('tested')
        assert tested, 'API call was not saved as tested'
        self.teardown_app_data()

    def test_pf_cloud_dns_manage_api_mark_untested(self):
        api_id = self.setup_useable_api_call(True)
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/dns/manage/api/test/unconfirm/%s' % api_id,
                follow_redirects=True
            )

        self.assertIn(
            'API Call has been mark as untested',
            response.data,
            'Invalid response found after marking untested'
        )
        api_call = pitchfork.db.cloud_dns.find_one()
        tested = api_call.get('tested')
        assert not tested, 'API call was not saved as untested'
        self.teardown_app_data()

    """ Delete Call """

    def test_pf_cloud_dns_manage_api_delete_valid(self):
        api_id = self.setup_useable_api_call()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/dns/manage/api/delete/%s' % api_id,
                follow_redirects=True
            )

        self.assertIn(
            'API call removed successfully',
            response.data,
            'Invalid response found after deleting call'
        )
        api_call = pitchfork.db.cloud_dns.find()
        self.assertEquals(
            api_call.count(),
            0,
            'Invalid api count found %d and should be 0' % api_call.count()
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_manage_api_delete_invalid(self):
        api_id = self.setup_useable_api_call()
        bogus_id = '528f5672192a8b3b2150c12b'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/dns/manage/api/delete/%s' % bogus_id,
                follow_redirects=True
            )

        self.assertIn(
            'API call was not found and nothing removed',
            response.data,
            'Invalid response found after invalid deletion'
        )
        api_call = pitchfork.db.cloud_dns.find()
        self.assertEquals(
            api_call.count(),
            1,
            'Invalid api count found %d and should be 1' % api_call.count()
        )
        self.teardown_app_data()

    """ Testing Product front """

    def test_pf_cloud_dns_api_admin_perms_testing(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/dns/testing')

        self.assertIn(
            '<h3>Cloud DNS - Testing API Calls</h3>',
            response.data,
            'Did not find correct HTML on page'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_api_admin_perms_testing_no_settings(self):
        pitchfork.db.api_settings.remove()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/dns/testing')

        self.assertIn(
            '<h3>Cloud DNS - Testing API Calls</h3>',
            response.data,
            'Did not find correct HTML on page'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_api_user_perms_testing(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/dns/testing')

        assert response._status_code == 302, \
            'Invalid response code %s' % response._status_code

        location = response.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )
        self.teardown_app_data()

    """ Front product View """

    def test_pf_cloud_dns_api_admin_perms(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/dns/')

        self.assertIn(
            '<h3>Cloud DNS</h3>',
            response.data,
            'Did not find correct HTML on page'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_api_user_perms(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/dns/')

        self.assertIn(
            '<h3>Cloud DNS</h3>',
            response.data,
            'Did not find correct HTML on page'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_api_admin_perms_no_settings(self):
        pitchfork.db.api_settings.remove()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/dns/')

        self.assertIn(
            '<h3>Cloud DNS</h3>',
            response.data,
            'Did not find correct HTML on page'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_api_user_perms_no_settings(self):
        pitchfork.db.api_settings.remove()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/dns/')

        self.assertIn(
            '<h3>Cloud DNS</h3>',
            response.data,
            'Did not find correct HTML on page'
        )
        self.teardown_app_data()

    """ Send Request to process """

    def test_pf_cloud_dns_post_call(self):
        api_id = self.setup_useable_api_call()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'api_verb': 'GET',
                'testing': False,
                'api_url': '{ddi}/groups',
                'api_token': 'test_token',
                'api_id': str(api_id),
                'ddi': '766030',
                'data_center': 'dfw'
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
                    '/dns/api_call/process',
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
        assert data.get('response_code'), (
            'No response status code was received'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_post_call_testing(self):
        api_id = self.setup_useable_api_call()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'api_verb': 'GET',
                'testing': False,
                'api_url': '{ddi}/groups',
                'api_token': 'test_token',
                'api_id': str(api_id),
                'ddi': '766030',
                'data_center': 'dfw',
                'testing': True
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
                    '/dns/api_call/process',
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
        assert data.get('response_code'), (
            'No response status code was received'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_post_call_testing_uk(self):
        api_id = self.setup_useable_api_call()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'api_verb': 'GET',
                'testing': False,
                'api_url': '{ddi}/groups',
                'api_token': 'test_token',
                'api_id': str(api_id),
                'ddi': '766030',
                'data_center': 'lon',
                'testing': True
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
                    '/dns/api_call/process',
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
        assert data.get('response_code'), (
            'No response status code was received'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_post_call_bad_response(self):
        api_id = self.setup_useable_api_call()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'api_verb': 'GET',
                'testing': False,
                'api_url': '{ddi}/groups',
                'api_token': 'test_token',
                'api_id': str(api_id),
                'ddi': '766030',
                'data_center': 'dfw'
            }
            with mock.patch('requests.get') as patched_get:
                type(patched_get.return_value).content = mock.PropertyMock(
                    return_value=''
                )
                type(patched_get.return_value).status_code = mock.PropertyMock(
                    return_value=401
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
                    '/dns/api_call/process',
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
        assert data.get('response_code'), (
            'No response status code was received'
        )
        self.teardown_app_data()

    def test_pf_cloud_dns_post_call_with_data(self):
        api_id = self.setup_useable_api_call_with_variables()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'api_verb': 'GET',
                'testing': False,
                'api_url': '{ddi}/groups',
                'api_token': 'test_token',
                'api_id': str(api_id),
                'ddi': '766030',
                'data_center': 'dfw',
                'test_var_value': 'Test Group'
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
                        '{"via": "1.1 Repose (Repose/2.12)",\
                        "x-response-id": "response_id",\
                        "transfer-encoding": "chunked",\
                        "server": "Jetty(8.0.y.z-SNAPSHOT)",\
                        "date": "Tue, 18 Mar 2014 19:52:26 GMT",\
                        "content-type": "application/json"}'
                    )
                )
                response = c.post(
                    '/dns/api_call/process',
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
        assert data.get('response_code'), (
            'No response status code was received'
        )
        assert data.get('data_package'), (
            'No response data package was received'
        )
        self.teardown_app_data()

    """ End Autoscale """
