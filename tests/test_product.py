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
from datetime import datetime
from bson import ObjectId
from uuid import uuid4


import unittest
import urlparse
import json
import mock
import re


class ProductTests(unittest.TestCase):
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
        self.db.autoscale.remove()
        self.db.favorites.remove()
        self.db.feedback.remove()
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

    def setup_useable_api_call(self, tested=None):
        data = {
            'api_uri': '/v1.0/{ddi}/groups',
            'doc_url': 'http://docs.rackspace.com',
            'short_description': 'Test API Call',
            'title': 'Test Call',
            'verb': 'GET',
            'variables': [],
            'allow_filter': True,
            'group': 'scaling_group'
        }
        if tested:
            data['tested'] = 'True'

        insert = self.db.autoscale.insert(data)
        return insert

    def setup_useable_api_call_with_variables(self):
        data = {
            'api_uri': '{ddi}/groups',
            'doc_url': 'http://docs.rackspace.com',
            'short_description': 'Test API Call',
            'title': 'Test Call',
            'verb': 'GET',
            'use_data': True,
            'group': 'scaling_group',
            'data_object': "{\r\n    \"test_var\": \"{test_var_value}\"\r\n}",
            'variables': [
                {
                    'field_type': 'text',
                    'description': 'Test Variable',
                    'required': True,
                    'duplicate': True,
                    'field_display_data': '',
                    'id_value': 0,
                    'field_display': 'TextField',
                    'variable_name': 'test_var_value'
                }
            ]
        }
        insert = self.db.autoscale.insert(data)
        return insert

    def setup_useable_feedback(self):
        data = {
            'category': 'deprecated',
            'feedback': 'test feedback info',
            'submitted': datetime.now(),
            'call_id': '528e098b192a8b99f956e5e7',
            'product_url': '/autoscale',
            'product_db': 'autoscale',
            'complete': False
        }
        return self.db.feedback.insert(data)

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

    def test_pf_autoscale_manage_admin_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/autoscale/manage')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Manage Settings',
            response.data,
            'Did not find correct HTML on page'
        )

    def test_pf_autoscale_manage_admin_perms_no_settings(self):
        self.db.api_settings.remove()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/autoscale/manage')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Manage Settings',
            response.data,
            'Did not find correct HTML on page'
        )

    def test_pf_autoscale_manage_user_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/autoscale/manage')

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

    """ Functional Tests """

    def test_pf_autoscale_manage_add_update(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/autoscale/manage')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'title': 'Test',
                'app_url': '/test',
                'us_api': 'http://us.test.com',
                'uk_api': 'http://uk.test.com',
                'doc_url': 'http://doc.test.com',
                'require_dc': True,
                'active': True
            }
            response = c.post(
                '/autoscale/manage',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Product was successfully updated',
            response.data,
            'Incorrect flash message after add data'
        )
        api_settings = self.db.api_settings.find_one()
        autoscale = api_settings.get('autoscale')
        updated = False
        if autoscale.get('title') == 'Test':
            updated = True

        assert updated, 'Product was not updated successfully'

    def test_pf_autoscale_manage_add_update_disable(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/autoscale/manage')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'title': 'Test',
                'app_url': '/test',
                'us_api': 'http://us.test.com',
                'uk_api': 'http://us.test.com',
                'doc_url': 'http://doc.test.com',
                'require_dc': True
            }
            response = c.post(
                '/autoscale/manage',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Product was successfully updated',
            response.data,
            'Incorrect flash message after data update'
        )
        api_settings = self.db.api_settings.find_one()
        autoscale = api_settings.get('autoscale')
        updated = False
        if autoscale.get('title') == 'Test':
            updated = True

        assert updated, 'Product was not updated successfully'
        active_products = api_settings.get('active_products')
        not_active = False
        if 'autoscale' not in active_products:
            not_active = True

        assert not_active, 'Product was not removed from active products'

    def test_pf_autoscale_manage_add_bad_data(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'title': 'Test',
                'app_url': '/test',
                'us_api': 'http://us.test.com',
                'uk_api': 'http://us.test.com',
                'doc_url': 'http://doc.test.com',
                'require_dc': True,
                'active': True
            }
            response = c.post(
                '/autoscale/manage',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Form was not saved successfully',
            response.data,
            'Incorrect flash message after add bad data'
        )
        calls = self.db.autoscale.find()
        assert calls.count() == 0, 'Call added when it should not have been'

    def test_pf_autoscale_reorder_groups_demote(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            before = self.db.api_settings.find_one(
                {'autoscale.groups.slug': 'scaling_groups'},
                {'autoscale.groups.$': 1}
            )
            response = c.get(
                '/autoscale/groups/scaling_groups/demote',
            )

        assert response.status_code == 200, 'Incorrect status code returned'
        after = self.db.api_settings.find_one(
            {'autoscale.groups.slug': 'scaling_groups'},
            {'autoscale.groups.$': 1}
        )
        before_group = before.get('autoscale').get('groups')[0].get('order')
        after_group = after.get('autoscale').get('groups')[0].get('order')
        assert before_group + 1 == after_group, 'Incorrect order after demote'

    def test_pf_autoscale_reorder_groups_promote(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            before = self.db.api_settings.find_one(
                {'autoscale.groups.slug': 'configurations'},
                {'autoscale.groups.$': 1}
            )
            response = c.get(
                '/autoscale/groups/configurations/promote',
            )

        assert response.status_code == 200, 'Incorrect status code returned'
        after = self.db.api_settings.find_one(
            {'autoscale.groups.slug': 'configurations'},
            {'autoscale.groups.$': 1}
        )
        before_group = before.get('autoscale').get('groups')[0].get('order')
        after_group = after.get('autoscale').get('groups')[0].get('order')
        assert before_group - 1 == after_group, 'Incorrect order after demote'

    def test_pf_autoscale_reorder_groups_bad_product(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/bad_product/groups/configurations/promote',
            )

        assert response.status_code == 400, 'Incorrect status code returned'

    """ Product API Management Autoscale - Perms Test """

    def test_pf_autoscale_manage_api_admin_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            c.get('/')
            response = c.get('/autoscale/manage/api')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Autoscale - API Calls',
            response.data,
            'Did not find correct HTML on page'
        )

    def test_pf_autoscale_manage_api_user_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/autoscale/manage/api')

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

    """ API Add """

    def test_pf_autoscale_manage_api_add_admin_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/autoscale/manage/api/add')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Add API Call',
            response.data,
            'Did not find correct HTML on page'
        )

    def test_pf_autoscale_manage_api_add_user_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/autoscale/manage/api/add')

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

    def test_pf_autoscale_manage_api_add_admin_post_dupe_title(self):
        self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/autoscale/manage/api/add')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'title': 'Test Call',
                'doc_url': 'http://docs.rackspace.com',
                'verb': 'GET',
                'api_uri': '{ddi}/groups'
            }
            response = c.post('/autoscale/manage/api/add', data=data)

        self.assertIn(
            'Form validation error, please check the form and try again',
            response.data,
            'Could not find error alert on page'
        )
        self.assertIn(
            'Duplicate title found',
            response.data,
            'Bad message when submitting duplicate title'
        )
        calls = self.db.autoscale.find()
        assert calls.count() == 1, 'Found to many calls in database'

    def test_pf_autoscale_manage_api_add_admin_post_dupe_url(self):
        self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/autoscale/manage/api/add')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'title': 'Dupe Call',
                'doc_url': 'http://docs.rackspace.com',
                'verb': 'GET',
                'api_uri': '/v1.0/{ddi}/groups'
            }
            response = c.post('/autoscale/manage/api/add', data=data)

        self.assertIn(
            'Form validation error, please check the form and try again',
            response.data,
            'Could not find error alert on page'
        )
        self.assertIn(
            'Duplicate URI, Verb, and Doc combination',
            response.data,
            'Bad message when submitting duplicate url and verb'
        )
        calls = self.db.autoscale.find()
        assert calls.count() == 1, 'Found to many calls in database'

    def test_pf_autoscale_manage_api_add_admin_post_good(self):
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
                'api_uri': '/v1.0/{ddi}/groups',
                'group': 'add_new_group',
                'new_group': 'Test Group',
                'product': 'autoscale'
            }
            response = c.post(
                '/autoscale/manage/api/add',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'API Call was added successfully',
            response.data,
            'Bad message when submitting good call'
        )
        calls = self.db.autoscale.find()
        found = self.db.autoscale.find_one()
        assert calls.count() == 1, 'Incorrect count of calls'
        assert found.get('group') == 'test_group', (
            'Group not find or incorrect group'
        )
        group = self.db.api_settings.find_one(
            {'autoscale.groups.slug': 'test_group'}
        )
        assert group, 'Could not find added group'

    def test_pf_autoscale_manage_api_add_admin_post_no_db(self):
        self.db.autoscale.remove()
        self.db.api_settings.update(
            {}, {
                '$set': {'autoscale.db_name': None}
            }
        )
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
                'api_uri': '{ddi}/groups'
            }
            response = c.post(
                '/autoscale/manage/api/add',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'There was an issue storing the API Call. Check '
            'the product and ensure the db_name is specified',
            response.data,
            'Bad message when submitting call without DB'
        )
        found_call = self.db.autoscale.find()
        assert found_call.count() == 0, 'No calls should have been found'

    def test_pf_autoscale_manage_api_add_post_with_vars(self):
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
                'api_uri': '/v1.0/{ddi}/groups',
                'group': 'add_new_group',
                'new_group': 'Test Group',
                'product': 'autoscale',
                'variable_0-description': 'Test variable',
                'variable_0-duplicate': 'y',
                'variable_0-field_display': 'TextField',
                'variable_0-field_type': 'text',
                'variable_0-variable_name': 'test_var',
                'variable_0-field_display_data': '',
                'variable_0-required': 'y'
            }
            response = c.post(
                '/autoscale/manage/api/add',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'API Call was added successfully',
            response.data,
            'Bad message when submitting good call'
        )
        calls = self.db.autoscale.find()
        found = self.db.autoscale.find_one()
        assert calls.count() == 1, 'Incorrect count of calls'
        assert found.get('group') == 'test_group', (
            'Group not find or incorrect group'
        )
        group = self.db.api_settings.find_one(
            {'autoscale.groups.slug': 'test_group'}
        )
        assert group, 'Could not find added group'

        assert len(found.get('variables')) == 1, 'Incorrect variable length'
        variable = found.get('variables')[0]
        assert variable.get('required'), 'Variable should be required'
        assert variable.get('duplicate'), 'Variable should be a duplicate'

    """ Edit API Call """

    def test_pf_autoscale_manage_api_edit_user_perms(self):
        api_id = self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get(
                '/autoscale/manage/api/edit/%s' % api_id
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

    def test_pf_autoscale_manage_api_edit_admin_perms(self):
        api_id = self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/autoscale/manage/api/edit/%s' % api_id
            )

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Edit API Call',
            response.data,
            'Invalid HTML found when browsing to edit'
        )

    def test_pf_autoscale_manage_api_edit_admin_perms_with_vars(self):
        self.setup_useable_api_call_with_variables()
        call = self.db.autoscale.find_one()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/autoscale/manage/api/edit/%s' % call.get('_id')
            )

        self.assertIn(
            'Edit API Call',
            response.data,
            'Invalid HTML found when browsing to edit'
        )
        self.assertIn(
            call.get('title'),
            response.data,
            'Could not find correct title in edit form'
        )
        self.assertIn(
            call.get('doc_url'),
            response.data,
            'Could not find correct Document URL in edit form'
        )

    def test_pf_autoscale_manage_api_edit_admin_bad_post(self):
        self.setup_useable_api_call()
        call = self.db.autoscale.find_one()
        with self.app as c:
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
                '/autoscale/manage/api/edit/%s' % call.get('_id'),
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Form validation error, please check the form and try again',
            response.data,
            'Incorrect flash message after add bad data'
        )
        self.assertIn(
            'Edit API Call',
            response.data,
            'Invalid HTML found when browsing to edit'
        )
        check_call = self.db.autoscale.find_one()
        assert call == check_call, (
            'Call was edited when it was not supposed to'
        )

    def test_pf_autoscale_manage_api_edit_admin_good_post(self):
        api_id = self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/autoscale/manage/api/edit/%s' % api_id
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
                '/autoscale/manage/api/edit/%s' % api_id,
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'API Call was successfully updated',
            response.data,
            'Incorrect flash message after successful edit'
        )
        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        calls = self.db.autoscale.find_one(
            {
                'title': 'Test Update Call'
            }
        )
        assert calls, 'Could not find updated call'

    """ Set testing for API Call """

    def test_pf_autoscale_manage_api_mark_tested(self):
        api_id = self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/autoscale/manage/api/confirm/%s' % api_id,
                follow_redirects=True
            )

        self.assertIn(
            'API call was successfully updated',
            response.data,
            'Invalid response found after marking tested'
        )
        check_call = self.db.autoscale.find_one({'_id': ObjectId(api_id)})
        assert check_call.get('tested'), 'API call was not saved as tested'

    def test_pf_autoscale_manage_api_mark_untested(self):
        api_id = self.setup_useable_api_call(True)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/autoscale/manage/api/unconfirm/%s' % api_id,
                follow_redirects=True
            )

        self.assertIn(
            'API call was successfully updated',
            response.data,
            'Invalid response found after marking untested'
        )
        check_call = self.db.autoscale.find_one({'_id': ObjectId(api_id)})
        assert not check_call.get('tested'), (
            'API call was not marked as untested'
        )

    """ Delete Call """

    def test_pf_autoscale_manage_api_delete_valid(self):
        api_id = self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/autoscale/manage/api/delete/%s' % api_id,
                follow_redirects=True
            )

        self.assertIn(
            'API call was successfully removed',
            response.data,
            'Invalid response found after deleting call'
        )
        api_call = self.db.autoscale.find()
        self.assertEquals(
            api_call.count(),
            0,
            'Invalid api count found %d and should be 0' % api_call.count()
        )

    def test_pf_autoscale_manage_api_delete_invalid(self):
        api_id = self.setup_useable_api_call()
        self.db.autoscale.remove()
        self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/autoscale/manage/api/delete/%s' % api_id,
                follow_redirects=True
            )

        self.assertIn(
            'API call was not found and nothing removed',
            response.data,
            'Invalid response found after invalid deletion'
        )
        api_call = self.db.autoscale.find()
        self.assertEquals(
            api_call.count(),
            1,
            'Invalid api count found %d and should be 1' % api_call.count()
        )

    """ Testing Product front """

    def test_pf_autoscale_api_admin_perms_testing(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/autoscale/testing')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Autoscale - Testing API Calls',
            response.data,
            'Did not find correct HTML on page'
        )

    def test_pf_autoscale_api_admin_perms_testing_no_settings(self):
        self.db.api_settings.remove()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/autoscale/testing')
            assert response._status_code == 302, (
                'Invalid response code %s' % response._status_code
            )
            response = c.get(
                '/autoscale/testing',
                follow_redirects=True
            )

        self.assertIn(
            'Product not found, please check the URL and try again',
            response.data,
            'Did not find correct error message on page'
        )

    def test_pf_autoscale_api_user_perms_testing(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/autoscale/testing')

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

    """ Front product View """

    def test_pf_autoscale_api_admin_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/autoscale/')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Autoscale',
            response.data,
            'Did not find correct HTML on page'
        )

    def test_pf_autoscale_api_not_active(self):
        temp = {
            'app_url': '/autoscale',
            'db_name': 'autoscale',
            'doc_url': (
                'http://docs.rackspace.com/cas/api/v1.0/autosca'
                'le-devguide/content/Overview.html'
            ),
            'title': 'Autoscale',
            'active': False,
            'require_region': True,
            'uk_api': 'https://{region}.autoscale.api.rackspacecloud.com',
            'us_api': 'https://{region}.autoscale.api.rackspacecloud.com'
        }
        self.db.api_settings.update({}, {'$set': {'autoscale': temp}})
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/autoscale/')
            assert response.status_code == 302, (
                'Invalid response code %s' % response.status_code
            )
            response = c.get(
                '/autoscale/',
                follow_redirects=True
            )

        assert response.status_code == 200, (
            'Invalid response code %s' % response.status_code
        )
        self.assertIn(
            'Product is not active and cannot be used at this time',
            response.data.decode('utf-8'),
            'Did not find correct HTML on page'
        )

    def test_pf_autoscale_api_user_perms(self):
        self.setup_useable_api_call_with_variables()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/autoscale/')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Autoscale',
            response.data,
            'Did not find correct HTML on page'
        )
        self.assertIn(
            'duplicate-field',
            response.data.decode('utf-8'),
            'Could not find expected class on page'
        )

    def test_pf_autoscale_api_admin_perms_no_settings(self):
        self.db.api_settings.remove()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/autoscale/')
            assert response._status_code == 302, (
                'Invalid response code %s' % response._status_code
            )
            response = c.get('/autoscale/', follow_redirects=True)

        self.assertIn(
            'Product not found, please check the URL and try again',
            response.data,
            'Did not find correct HTML on page'
        )

    def test_pf_autoscale_api_user_perms_no_settings(self):
        self.db.api_settings.remove()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/autoscale/')
            assert response._status_code == 302, (
                'Invalid response code %s' % response._status_code
            )
            response = c.get('/autoscale/', follow_redirects=True)

        self.assertIn(
            'Product not found, please check the URL and try again',
            response.data,
            'Did not find correct HTML on page'
        )

    """ Send Request to process """

    def test_pf_autoscale_post_call(self):
        api_id = self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'api_verb': 'GET',
                'testing': False,
                'api_url': '/v1.0/{ddi}/groups',
                'api_token': 'test_token',
                'api_id': str(api_id),
                'ddi': '123456',
                'data_center': 'dfw',
                'add_filter': 'limit=100'
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
        self.assertIn(
            '.autoscale.api.rackspacecloud.com/v1.0/123456/groups?limit=100',
            data.get('api_url'),
            'Did not find the limit attached to the end of the URI'
        )

    def test_pf_autoscale_post_call_testing(self):
        api_id = self.setup_useable_api_call()
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

    def test_pf_autoscale_post_call_testing_uk(self):
        api_id = self.setup_useable_api_call()
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
        assert data.get('response_code'), (
            'No response status code was received'
        )

    def test_pf_autoscale_post_call_bad_response(self):
        api_id = self.setup_useable_api_call()
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
        assert data.get('response_code'), (
            'No response status code was received'
        )

    def test_pf_autoscale_post_call_with_data(self):
        api_id = self.setup_useable_api_call_with_variables()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'api_verb': 'POST',
                'testing': 'false',
                'api_url': '{ddi}/groups',
                'api_token': 'test_token',
                'api_id': str(api_id),
                'ddi': '123456',
                'data_center': 'dfw',
                'test_var_value': 'Test Group'
            }
            with mock.patch('requests.post') as ppost:
                type(ppost.return_value).content = mock.PropertyMock(
                    return_value='{"groups_links": [], "groups": []}'
                )
                type(ppost.return_value).status_code = mock.PropertyMock(
                    return_value=200
                )
                type(ppost.return_value).headers = mock.PropertyMock(
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
        assert data.get('response_code'), (
            'No response status code was received'
        )
        assert data.get('data_package'), (
            'No response data package was received'
        )
        assert self.db.history.count() == 1, (
            'Could not find call logged in history'
        )

    def test_pf_mark_favorite_add(self):
        api_id = self.setup_useable_api_call(True)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            data = {'call_id': str(api_id)}
            response = c.post(
                '/autoscale/favorites/add',
                data=json.dumps(data),
                content_type='application/json'
            )
            fav_response = c.get('/favorites')
            prod_response = c.get('/autoscale/')

        data = json.loads(response.data)
        assert data.get('code') == 200, 'Incorrect response code received'
        favorites = self.db.favorites.find_one({'username': 'test'})
        assert favorites, 'No favorites found'
        assert favorites.get('favorites')[0].get('call_id') == str(api_id), (
            'Did not find call ID in favorites'
        )
        assert fav_response.status_code == 200, 'Incorrect status returned'
        self.assertIn(
            'Test Call',
            fav_response.data,
            'Could not find call title in favorites'
        )
        assert prod_response.status_code == 200, 'Incorrect status found'

    def test_pf_mark_favorite_remove(self):
        api_id = self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            data = {'call_id': str(api_id)}
            response = c.post(
                '/autoscale/favorites/add',
                data=json.dumps(data),
                content_type='application/json'
            )
            response = c.post(
                '/autoscale/favorites/remove',
                data=json.dumps(data),
                content_type='application/json'
            )

        data = json.loads(response.data)
        assert data.get('code') == 200, 'Incorrect response code received'
        favorites = self.db.favorites.find_one({'username': 'test'})
        assert favorites, 'No favorites found'
        assert len(favorites.get('favorites')) == 0, (
            'Favorites not empty'
        )

    def test_pf_mark_favorite_remove_no_prior(self):
        api_id = self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            data = {'call_id': str(api_id)}
            response = c.post(
                '/autoscale/favorites/remove',
                data=json.dumps(data),
                content_type='application/json'
            )

        data = json.loads(response.data)
        assert data.get('code') == 200, 'Incorrect response code received'
        favorites = self.db.favorites.find_one({'username': 'test'})
        assert favorites is None, 'No favorites found'

    def test_pf_mark_favorite_bad_action(self):
        api_id = self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            data = {'call_id': str(api_id)}
            response = c.post(
                '/autoscale/favorites/bad_action',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response.status_code == 404, 'Incorrect response code received'
        favorites = self.db.favorites.find_one({'username': 'test'})
        assert favorites is None, 'No favorites found'

    def test_pf_mark_favorite_bad_call(self):
        api_id = self.setup_useable_api_call()
        self.db.autoscale.remove()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            data = {'call_id': str(api_id)}
            response = c.post(
                '/autoscale/favorites/add',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response.status_code == 404, 'Incorrect response code received'
        favorites = self.db.favorites.find_one({'username': 'test'})
        assert favorites is None, 'No favorites found'

    def test_pf_mark_favorite_bad_product(self):
        api_id = self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            data = {'call_id': str(api_id)}
            response = c.post(
                '/bad_product/favorites/add',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response.status_code == 404, 'Incorrect response code received'
        favorites = self.db.favorites.find_one({'username': 'test'})
        assert favorites is None, 'No favorites found'

    """ Feedback """

    def test_pf_feedback_add(self):
        api_id = self.setup_useable_api_call()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            data = {
                'call_id': str(api_id),
                'category': 'doc_link',
                'feedback': 'Testing feedback',
                'product_db': 'autoscale'
            }
            response = c.post(
                '/feedback/',
                data=json.dumps(data),
                content_type='application/json'
            )

        data = json.loads(response.data)
        assert data.get('code') == 200, 'Incorrect response code received'
        feedback = self.db.feedback.find_one()
        assert feedback, 'No feedback items found'
        assert feedback.get('call_id') == str(api_id), (
            'Did not find call ID in feedback'
        )

    def test_pf_feedback_mark_invalid_item(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {'feedback_id': 'bad_id'}
            response = c.put(
                '/feedback/',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response.status_code == 400, 'Incorrect response code received'

    def test_pf_feedback_user_permissions_check(self):
        feedback_id = self.setup_useable_feedback()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            data = {'feedback_id': str(feedback_id)}
            response = c.put(
                '/feedback/',
                data=json.dumps(data),
                content_type='application/json'
            )

        assert response.status_code == 404, 'Incorrect response code received'
        feedback = self.db.feedback.find_one()
        assert feedback, 'No feedback items found'
        assert feedback.get('_id') == feedback_id, (
            'Did not find correct feedback item'
        )
        assert feedback.get('complete') is False, (
            'Feedback marked complete when it should not have been'
        )

    def test_pf_feedback_mark_complete(self):
        feedback_id = self.setup_useable_feedback()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {'feedback_id': str(feedback_id)}
            response = c.put(
                '/feedback/',
                data=json.dumps(data),
                content_type='application/json',
            )

        data = json.loads(response.data)
        assert data.get('code') == 200, 'Incorrect response code received'
        feedback = self.db.feedback.find_one()
        assert feedback, 'No feedback items found'
        assert feedback.get('_id') == feedback_id, (
            'Did not find correct feedback item'
        )
        assert feedback.get('complete'), (
            'Feedback not marked complete as expected'
        )

    def test_pf_feedback_view(self):
        self.setup_useable_feedback()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/feedback/')

        self.assertIn(
            'Submitted Feedback',
            response.data,
            'Could not load page with feedback'
        )
        feedback = self.db.feedback.find_one()
        self.assertIn(
            'data-feedback_id="%s"' % feedback.get('_id'),
            response.data,
            'Could not find feedback item'
        )

    def test_pf_feedback_view_user(self):
        self.setup_useable_feedback()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/feedback/')
            assert response.status_code == 302, 'Invalid status code'
            response = c.get('/feedback/', follow_redirects=True)

        self.assertIn(
            'You do not have the correct permissions to access this page',
            response.data,
            'Could not find error message on bad permissions'
        )
