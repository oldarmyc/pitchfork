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
from uuid import uuid4


import unittest
import urlparse
import re


class PitchforkManageTests(unittest.TestCase):
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
        self.db.api_settings.remove()
        self.db.history.remove()
        self.db.forms.remove()

    def setup_user_login(self, session):
        session['username'] = 'skeletor'
        session['csrf_token'] = uuid4().hex
        session['role'] = 'logged_in'
        session['email'] = 'skeletor@res.rackspace.com'
        session['_permanent'] = True
        session['name'] = 'Skeletor'
        session['token'] = uuid4().hex

    def setup_admin_login(self, session):
        session['username'] = 'bob.richards'
        session['csrf_token'] = uuid4().hex
        session['role'] = 'administrators'
        session['email'] = 'admin@res.rackspace.com'
        session['_permanent'] = True
        session['name'] = 'Default Admin'
        session['token'] = uuid4().hex

    def setup_useable_admin(self):
        self.db.settings.update(
            {}, {
                '$push': {
                    'administrators': {
                        'admin_sso': 'test1234',
                        'admin_name': 'Test Admin',
                        'admin_email': 'test@test.com'
                    }
                }
            }
        )

    def setup_useable_history(self):
        history = {
            'username': 'skeletor',
            'ddi': '1234567',
            'details': {
                'description': 'Resizes the specified server',
                'doc_url': 'http://docs.rackspace.com/servers',
                'title': 'Resize Server'
            },
            'data_center': 'ord',
            'completed_at': datetime.now(),
            'product': 'Load Balancers',
            'request': {
                'url': (
                    'https://iad.loadbalancers.api.rackspacecloud.com/v1.0'
                    '/1234567/loadbalancers/9999999/ssltermination/'
                    'certificatemappings'
                ),
                'verb': 'POST',
                'data': {
                    'certificateMapping': {
                        'hostName': 'test.com',
                        'privateKey': (
                            '-----BEGIN RSA PRIVATE KEY-----\\nPrivate '
                            'Key Data\\n-----END RSA PRIVATE KEY-----\\n'
                        ),
                        'certificate': (
                            '-----BEGIN CERTIFICATE-----\\nCertificate '
                            'Data\\n-----END CERTIFICATE-----\\n'
                        ),
                        'intermediateCertificate': (
                            '-----BEGIN CERTIFICATE-----\\nIntermediate '
                            'Cert Data\\n-----END CERTIFICATE-----\\n'
                        )
                    }
                }
            },
            'response': {
                'body': {
                    'certificateMapping': {
                        'hostName': 'test.com',
                        'id': 9999999,
                        'certificate': (
                            '-----BEGIN CERTIFICATE-----\n'
                            'Certificate Data\n-----END CERTIFICATE-----'
                        ),
                        'intermediateCertificate': (
                            '-----BEGIN CERTIFICATE-----\n'
                            'Intermediate Cert Data\n-----END CERTIFICATE-----'
                        )
                    }
                },
                'headers': {
                    'content-length': '0',
                    'via': '1.1 Repose (Repose/2.8.0.2), 1.1 varnish',
                    'age': '0',
                    'server': 'Jetty(8.0.y.z-SNAPSHOT)',
                    'connection': 'keep-alive',
                    'cache-control': 'no-cache',
                    'content-type': 'text/xml'
                },
                'code': 202
            },
            'name': 'Skeletor'
        }
        self.db.history.insert(history)

    def setup_default_field(self, form_name):
        data = {
            'description': '',
            'active': True,
            'default_value': 'Test',
            'field_type': 'TextField',
            'field_choices': '',
            'name': 'test',
            'default': True,
            'style_id': None,
            'required': False,
            'label': 'test',
            'order': 5
        }
        self.db.forms.update(
            {'name': form_name},
            {'$push': {'fields': data}}
        )

    def retrieve_csrf_token(self, data):
        temp = re.search('id="csrf_token"(.+?)>', data)
        if temp:
            token = re.search('value="(.+?)"', temp.group(1))
            if token:
                return token.group(1)
        return 'UNK'

    """ History """

    def test_pf_history(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/history')

        self.assertIn(
            'Call History',
            response.data,
            'Did not find correct HTML on page'
        )
        self.assertIn(
            'No API calls have been executed as of yet.',
            response.data,
            'Did not find correct no call message'
        )

    def test_pf_history_scrub(self):
        self.setup_useable_history()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get(
                '/history/scrub',
                follow_redirects=True
            )

        self.assertIn(
            'Call History',
            response.data,
            'Did not find correct HTML on page'
        )
        self.assertIn(
            'History has been scrubbed successfully',
            response.data,
            'Did not find correct message after scrub'
        )
        history = self.db.history.find_one({'request.data': 'SCRUBBED'})
        assert history, 'Could not find scrubbed request data after scrub'

    def test_pf_history_scrub_no_history(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get(
                '/history/scrub',
                follow_redirects=True
            )

        self.assertIn(
            'Call History',
            response.data,
            'Did not find correct HTML on page'
        )
        self.assertIn(
            'There was an issue scrubbing the history data',
            response.data,
            'Did not find correct message after scrub'
        )

    def test_pf_favorites(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/favorites')

        self.assertIn(
            'My Favorites',
            response.data,
            'Did not find correct HTML on page'
        )

    """ Datacenters Management """

    def test_pf_manage_dcs_admin_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/regions')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Manage Regions',
            response.data,
            'Did not find correct HTML on page'
        )

    def test_pf_manage_dcs_user_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            result = c.get('/manage/regions')

        assert result._status_code == 302, (
            'Invalid response code %s' % result._status_code
        )
        request_path = urlparse.urlparse(result.headers.get('Location')).path
        self.assertEqual(
            request_path,
            '/',
            'Invalid redirect location %s, expected "/"' % request_path
        )

    """ Functional Tests """

    def test_pf_manage_dcs_add(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/regions')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': 'Test',
                'abbreviation': 'TEST'
            }
            response = c.post(
                '/manage/regions',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Region successfully added to system',
            response.data,
            'Incorrect flash message after add'
        )
        found_add = self.db.api_settings.find_one(
            {
                'regions.name': 'Test'
            }
        )
        assert found_add, 'DC not found after add'

    def test_pf_manage_dcs_add_no_dcs(self):
        self.db.api_settings.update({}, {'$unset': {'dcs': 1}})
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/regions')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': 'Test',
                'abbreviation': 'TEST'
            }
            response = c.post(
                '/manage/regions',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Region successfully added to system',
            response.data,
            'Incorrect flash message after add'
        )
        found_add = self.db.api_settings.find_one(
            {
                'regions.name': 'Test'
            }
        )
        assert found_add, 'DC not found after add'

    def test_pf_manage_dcs_add_dupe(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/regions')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': 'Dallas',
                'abbreviation': 'DFW'
            }

            response = c.post(
                '/manage/regions',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Duplicate name',
            response.data,
            'Incorrect error message after add duplicate'
        )
        self.assertIn(
            'Duplicate abbreviation',
            response.data,
            'Incorrect error message after add duplicate'
        )
        api_settings = self.db.api_settings.find_one()
        dcs = api_settings.get('regions')
        count = 0
        for dc in dcs:
            if dc.get('name') == 'Dallas':
                count += 1

        self.assertEquals(
            count,
            1,
            'Incorrect count after dupe add found %d instead of 1' % count
        )

    def test_pf_manage_dcs_add_bad_data(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/regions')
            data = {
                'name': 'Test',
                'abbreviation': 'TEST'
            }
            response = c.post(
                '/manage/regions',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            (
                'There was a form validation error, please check '
                'the required values and try again.'
            ),
            response.data,
            'Incorrect flash message after add bad data'
        )

    def test_pf_manage_dcs_remove(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/regions/delete/DFW',
                follow_redirects=True
            )

        self.assertIn(
            'Dfw was deleted successfully',
            response.data,
            'Incorrect flash message after remove'
        )
        api_settings = self.db.api_settings.find_one()
        dcs = api_settings.get('regions')
        count = 0
        for dc in dcs:
            if dc.get('name') == 'Dallas':
                count += 1

        self.assertEquals(
            count,
            0,
            'Incorrect count after remove, found %d instead of 0' % count
        )

    """ Verbs Management - Perms Test """

    def test_pf_verbs_admin_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/verbs')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Manage API Verbs',
            response.data,
            'Did not find correct HTML on page'
        )

    def test_pf_verbs_user_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            result = c.get('/manage/verbs')

        assert result._status_code == 302, (
            'Invalid response code %s' % result._status_code
        )
        request_path = urlparse.urlparse(result.headers.get('Location')).path
        self.assertEqual(
            request_path,
            '/',
            'Invalid redirect location %s, expected "/"' % request_path
        )

    """ Functional Tests """

    def test_pf_verbs_add(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/verbs')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': 'Test',
                'active': True
            }
            response = c.post(
                '/manage/verbs',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Verb successfully added to system',
            response.data,
            'Incorrect flash message after add'
        )
        found_add = self.db.api_settings.find_one(
            {
                'verbs.name': 'TEST'
            }
        )
        assert found_add, 'Verb not found after add'

    def test_pf_verbs_add_dupe(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/verbs')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': 'GET',
                'active': True
            }
            response = c.post(
                '/manage/verbs',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Duplicate verb',
            response.data,
            'Incorrect error message after add duplicate'
        )
        api_settings = self.db.api_settings.find_one()
        verbs = api_settings.get('verbs')
        count = 0
        for verb in verbs:
            if verb.get('name') == 'GET':
                count += 1

        self.assertEquals(
            count,
            1,
            'Incorrect count after dupe add found %d instead of 1' % count
        )

    def test_pf_verbs_add_bad_data(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/verbs')
            data = {
                'name': 'GET',
                'active': True
            }

            response = c.post(
                '/manage/verbs',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            (
                'There was a form validation error, please check '
                'the required values and try again.'
            ),
            response.data,
            'Incorrect flash message after add bad data'
        )

    def test_pf_verbs_remove(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/verbs/delete/GET',
                follow_redirects=True
            )

        self.assertIn(
            'Get was deleted successfully',
            response.data,
            'Incorrect flash message after remove'
        )
        api_settings = self.db.api_settings.find_one()
        verbs = api_settings.get('verbs')
        count = 0
        for verb in verbs:
            if verb.get('name') == 'GET':
                count += 1

        self.assertEquals(
            count,
            0,
            'Incorrect count after remove, found %d instead of 0' % count
        )

    def test_pf_verbs_deactivate(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/verbs/deactivate/GET',
                follow_redirects=True
            )

        self.assertIn(
            'Get was deactivated successfully',
            response.data,
            'Incorrect flash message after deactivate'
        )
        api_settings = self.db.api_settings.find_one()
        verbs = api_settings.get('verbs')
        deactivated = False
        for verb in verbs:
            if verb.get('name') == 'GET':
                if not verb.get('active'):
                    deactivated = True

        assert deactivated, 'Verb was not deactivated'

    def test_pf_verbs_activate(self):
        self.db.api_settings.update(
            {
                'verbs.name': 'GET'
            }, {
                '$set': {
                    'verbs.$.active': False
                }
            }
        )
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/verbs/activate/GET',
                follow_redirects=True
            )

        self.assertIn(
            'Get was activated successfully',
            response.data,
            'Incorrect flash message after activate'
        )
        api_settings = self.db.api_settings.find_one()
        verbs = api_settings.get('verbs')
        activated = False
        for verb in verbs:
            if verb.get('name') == 'GET':
                if verb.get('active'):
                    activated = True

        assert activated, 'Verb was not activated'

    def test_pf_bad_key_for_actions(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/BAD_KEY/delete/GET',
                follow_redirects=True
            )

        self.assertIn(
            'Invalid data key given so no action taken',
            response.data,
            'Incorrect flash message after bad key'
        )
        api_settings = self.db.api_settings.find_one()
        verbs = api_settings.get('verbs')
        count = 0
        for verb in verbs:
            if verb.get('name') == 'GET':
                count += 1

        self.assertEquals(
            count,
            1,
            'Incorrect count after bad key, found %d instead of 1' % count
        )

    def test_pf_bad_action_for_actions(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/verbs/BAD_ACTION/GET',
                follow_redirects=True
            )

        self.assertIn(
            'Invalid action given so no action taken',
            response.data,
            'Incorrect flash message after bad action'
        )
        api_settings = self.db.api_settings.find_one()
        verbs = api_settings.get('verbs')
        count = 0
        for verb in verbs:
            if verb.get('name') == 'GET':
                count += 1

        self.assertEquals(
            count,
            1,
            'Incorrect count after bad key, found %d instead of 1' % count
        )

    def test_pf_bad_dat_element_for_actions(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/verbs/delete/BAD_DATA',
                follow_redirects=True
            )

        self.assertIn(
            'Bad_Data was not found so no action taken',
            response.data,
            'Incorrect flash message after bad data'
        )
        api_settings = self.db.api_settings.find_one()
        verbs = api_settings.get('verbs')
        count = 0
        for verb in verbs:
            if verb.get('name') == 'GET':
                count += 1

        self.assertEquals(
            count,
            1,
            'Incorrect count after bad key, found %d instead of 1' % count
        )
