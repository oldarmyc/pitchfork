import pitchfork
import flask
import unittest
import happymongo
import json
import urlparse
import re
import mock


from flask import session
from datetime import datetime, timedelta
from dateutil import tz
from uuid import uuid4
from bson.objectid import ObjectId


class PitchforkTests(unittest.TestCase):
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

    def setup_useable_admin(self):
        pitchfork.db.settings.update(
            {}, {
                '$push': {
                    'administrators': {
                        'admin': 'test1234',
                        'admin_name': 'Test Admin'
                    }
                }
            }
        )

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

    """ Basic tests """

    def test_ui_index(self):
        result = self.app.get('/')
        self.assertEqual(
            result._status_code,
            200,
            'Invalid response code %s' % result._status_code
        )
        self.teardown_app_data()

    def test_ui_login_get(self):
        result = self.app.get('/admin/login')
        self.assertEquals(
            result._status_code,
            200,
            'Invalid response code %s, expected 200' % result._status_code
        )
        self.teardown_app_data()

    def test_context_processor_slugify_for_app(self):
        response = self.app.get('/admin/login')
        self.assertIn(
            'Slug_this_PHRASE',
            response.data,
            'Slugify data was not correct'
        )
        self.teardown_app_data()

    def test_context_processor_unslug_for_app(self):
        result = self.app.get('/admin/login')
        self.assertIn(
            'Unslug Test: unslug this value',
            result.data,
            'Unslug data was not correct'
        )
        self.teardown_app_data()

    def test_admin_no_login_redirect(self):
        with pitchfork.app.test_client() as c:
            result = c.get('/admin/settings/general')

        assert result._status_code == 302, \
            'Invalid response code %s' % result._status_code

        location = result.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/admin/login',
            'Invalid redirect location %s, expected "/"' % o.path
        )
        self.teardown_app_data()

    def test_ui_login_post_bad_data(self):
        with pitchfork.app.test_client() as c:
            response = c.get('/admin/login')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'username': 'pitchfork'
            }
            response = c.post('/admin/login', data=data)

        self.assertIn(
            'Form validation error, please check the form and try again',
            response.data,
            'Invalid response in flash message'
        )
        self.teardown_app_data()

    def test_ui_login_post(self):
        today = datetime.now()
        tomorrow = '%s-%s-%s' % (today.year, today.month, today.day + 1)
        with pitchfork.app.test_client() as c:
            response = c.get('/admin/login')
            token = self.retrieve_csrf_token(response.data)
            with mock.patch('requests.post') as patched_post:
                type(patched_post.return_value).content = mock.PropertyMock(
                    return_value=(
                        '{"access": {"token": {"RAX-AUTH:authenticatedBy": '
                        '["APIKEY"], "expires": "%sT04:17:18.880Z", '
                        '"id": "a359c49c0e6f4b2db32618cc98137a8d", "tenant": '
                        '{"id": "123456","name": "123456"}}}}' % tomorrow
                    )
                )
                data = {
                    'csrf_token': token,
                    'username': 'pitchfork',
                    'password': '12345'
                }
                response = c.post(
                    '/admin/login',
                    data=data,
                    follow_redirects=True
                )
                self.assertEquals(
                    response._status_code,
                    200,
                    'Invalid response code %s, expected 200' % (
                        response._status_code
                    )
                )
                result = c.post('/admin/forms')
                assert result._status_code == 302, (
                    'Invalid response code %s' % result._status_code
                )
        self.teardown_app_data()

    def test_ui_login_post_admin(self):
        today = datetime.now()
        tomorrow = '%s-%s-%s' % (today.year, today.month, today.day + 1)
        with pitchfork.app.test_client() as c:
            response = c.get('/admin/login')
            token = self.retrieve_csrf_token(response.data)
            with mock.patch('requests.post') as patched_post:
                type(patched_post.return_value).content = mock.PropertyMock(
                    return_value=(
                        '{"access": {"token": {"RAX-AUTH:authenticatedBy": '
                        '["APIKEY"], "expires": "%sT04:17:18.880Z", '
                        '"id": "a359c49c0e6f4b2db32618cc98137a8d", "tenant": '
                        '{"id": "123456","name": "123456"}}}}' % tomorrow
                    )
                )
                data = {
                    'csrf_token': token,
                    'username': 'oldarmyc',
                    'password': '12345'
                }
                response = c.post(
                    '/admin/login',
                    data=data,
                    follow_redirects=True
                )
                self.assertEquals(
                    response._status_code,
                    200,
                    'Invalid response code %s, expected 200' % (
                        response._status_code
                    )
                )
                result = c.post('/admin/forms')
                assert result._status_code == 200, (
                    'Invalid response code %s' % result._status_code
                )
        self.teardown_app_data()

    def test_ui_logout(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            result = self.app.get(
                '/admin/logout/',
                follow_redirects=True
            )

        self.assertIn(
            '<a href="/admin/login">Log In</a>',
            result.data,
            'User was not logged out correctly'
        )
        self.teardown_app_data()

    def test_login_page_placeholder(self):
        with pitchfork.app.test_client() as c:
            response = self.app.get('/admin/login')

        self.assertIn(
            'placeholder="API Key"',
            response.data,
            'Placeholder for login is incorrect'
        )
        self.teardown_app_data()

    """ Admin Manage - Permissions Tests """

    def test_ui_admin_perms_admins(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            result = c.get('/admin/settings/admins')

        assert result._status_code == 200, (
            'Invalid response code %s' % result._status_code
        )
        self.teardown_app_data()

    def test_ui_user_perms_admins(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)
            result = c.get('/admin/settings/admins')

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

    """ Function admin tests """

    def test_admin_add(self):
        admin_to_add = 'test_user'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/admins')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'administrator': admin_to_add,
                'full_name': 'Test Admin',
                'admin': 'Add Admin'
            }
            response = c.post(
                '/admin/settings/admins',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'User has been added as an Administrator',
            response.data,
            'Did not find or incorrect flash message after update'
        )

        settings = pitchfork.db.settings.find_one()
        admins = settings.get('administrators')
        assert len(admins) == 2, (
            'Incorrect numbers of admins, expected 2 and got %d' % len(admins)
        )

        found_admin = False
        for admin in admins:
            if admin.get('admin') == admin_to_add:
                found_admin = True

        assert found_admin, 'Could not find admin that was added to system'
        self.teardown_app_data()

    def test_admin_duplicate_user(self):
        self.setup_useable_admin()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/admins')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'administrator': 'test1234',
                'full_name': 'Test User',
                'admin': 'Add Admin'
            }

            response = c.post(
                '/admin/settings/admins',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'User is already in the Administrators List',
            response.data,
            'Did not find or incorrect flash message after duplicate data'
        )
        self.teardown_app_data()

    def test_admin_form_validation_error(self):
        admin_to_add = ''
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/admin/settings/admins')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'administrator': admin_to_add,
                'admin': 'Add Admin'
            }

            response = c.post(
                '/admin/settings/admins',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Form validation failed. Please check the form and try again',
            response.data,
            'Did not find or incorrect flash message after invalid data'
        )
        self.teardown_app_data()

    def test_admin_successfull_remove(self):
        self.setup_useable_admin()
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            user_to_remove = 'test1234'
            response = c.get(
                '/admin/settings/remove/admin/%s' % user_to_remove,
                follow_redirects=True
            )

        self.assertIn(
            'Administrator has been removed',
            response.data,
            'Did not find or incorrect flash message after removal'
        )
        settings = pitchfork.db.settings.find_one()
        admins = settings.get('administrators')
        assert len(admins) == 1, (
            'Incorrect numbers of admins, expected 1 and got %d' % len(admins)
        )
        settings = pitchfork.db.settings.find_one()
        updated_admins = settings.get('administrators')
        found_admin = True
        for admin in updated_admins:
            if admin.get('admin_sso') == 'test1234':
                found_admin = False
        assert found_admin, 'Found admin that should have been removed'
        self.teardown_app_data()

    """ General Settings """

    def test_ui_admin_perms_settings(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            result = c.get('/admin/settings/general')

        assert result._status_code == 200, \
            'Invalid response code %s' % result._status_code
        self.teardown_app_data()

    def test_ui_user_perms_settings(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)
            result = c.get('/admin/settings/general')

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

    def test_settings_successful_update(self):
        update_title = 'test title'
        update_email = 'test@test.com'
        update_footer = 'test footer'
        update_intro = 'test intro'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            response = c.get('/admin/settings/general')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'application_title': update_title,
                'application_email': update_email,
                'application_footer': update_footer,
                'application_well': update_intro,
                'settings': 'Apply Settings'
            }
            response = c.post(
                '/admin/settings/general',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'General Settings have been updated',
            response.data,
            'Did not find or incorrect flash message after update'
        )
        settings = pitchfork.db.settings.find_one()
        assert settings.get('application_title') == update_title, (
            'Title was not set correctly on update'
        )
        assert settings.get('application_email') == update_email, (
            'Email was not set correctly on update'
        )
        assert settings.get('application_footer') == update_footer, (
            'Footer was not set correctly on update'
        )
        assert settings.get('application_well') == update_intro, (
            'Intro was not set correctly on update'
        )
        self.teardown_app_data()

    """ Manage Roles - Permissions Tests """

    def test_ui_admin_perms_roles(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            result = c.get('/admin/settings/roles')

        assert result._status_code == 200, \
            'Invalid response code %s' % result._status_code
        self.teardown_app_data()

    def test_ui_user_perms_roles(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)
            result = c.get('/admin/settings/roles')

        assert result._status_code == 302, (
            'Invalid response code %s' % result._status_code
        )
        location = result.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )
        self.teardown_app_data()

    """ Functional Tests """

    def test_roles_disable(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            toggle_role = 'all'
            response = c.get(
                '/admin/settings/roles/toggle/disable/%s' % toggle_role,
                follow_redirects=True
            )

        self.assertIn(
            "Role %s status was changed" % toggle_role,
            response.data,
            'Did not find or incorrect flash message after disable'
        )

        settings = pitchfork.db.settings.find_one()
        roles = settings.get('roles')
        disabled = False
        for role in roles:
            if role.get('name') == toggle_role:
                if not role.get('active'):
                    disabled = True
                    break

        assert disabled, 'Role was not disabled as expected'
        self.teardown_app_data()

    def test_roles_enable(self):
        toggle_role = 'all'
        pitchfork.db.settings.update(
            {
                'roles.name': toggle_role
            }, {
                '$set': {
                    'roles.$.active': False
                }
            }
        )
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/settings/roles/toggle/enable/%s' % toggle_role,
                follow_redirects=True
            )

        self.assertIn(
            "Role %s status was changed" % toggle_role,
            response.data,
            'Did not find or incorrect flash message after disable'
        )

        settings = pitchfork.db.settings.find_one()
        roles = settings.get('roles')
        enabled = False
        for role in roles:
            if role.get('name') == toggle_role:
                if role.get('active'):
                    enabled = True
                    break

        assert enabled, 'Role was not enabled as expected'
        self.teardown_app_data()

    def test_roles_add_role(self):
        add_role = 'Test Role'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/roles')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'display_name': add_role,
                'status': 'y'
            }

            response = c.post(
                '/admin/settings/roles',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Role successfully Added',
            response.data,
            'Did not find or incorrect flash message after add'
        )

        settings = pitchfork.db.settings.find_one()
        roles = settings.get('roles')
        found = False
        for role in roles:
            if role.get('display_name') == add_role:
                found = True

        assert found, 'Role added was not found in database'
        self.teardown_app_data()

    def test_roles_add_role_existing(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/roles')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'display_name': 'All',
                'active': 'y'
            }

            response = c.post(
                '/admin/settings/roles',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Role already exists, please check the name and try again',
            response.data,
            'Did not find or incorrect flash message after add existing'
        )
        self.teardown_app_data()

    def test_roles_add_role_bad_data(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {'display_name': 'Test Invalid'}
            response = c.post(
                '/admin/settings/roles',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Form validation failed',
            response.data,
            'Did not find or incorrect flash message after add invalid'
        )
        self.teardown_app_data()

    def test_roles_delete_role(self):
        remove_role = 'all'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/settings/roles/remove/%s' % remove_role,
                follow_redirects=True
            )

        self.assertIn(
            'Role has been removed',
            response.data,
            'Did not find or incorrect flash message after delete'
        )
        settings = pitchfork.db.settings.find_one()
        roles = settings.get('roles')
        role_removed = True
        for role in roles:
            if role.get('name') == remove_role:
                role_removed = False
                break

        assert role_removed, 'Role was found and not removed as expected'
        self.teardown_app_data()

    """ Manage Permissions - Permissions Tests """

    def test_ui_admin_perms_roles_set(self):
        using_role = 'all'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            result = c.get(
                '/admin/settings/permissions/%s' % using_role
            )

        assert result._status_code == 200, \
            'Invalid response code %s' % result._status_code
        self.teardown_app_data()

    def test_ui_user_perms_roles_set(self):
        using_role = 'all'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)
            result = c.get(
                '/admin/settings/permissions/%s' % using_role
            )

        assert result._status_code == 302, (
            'Invalid response code %s' % result._status_code
        )
        location = result.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )
        self.teardown_app_data()

    """ Functional Tests """

    def test_roles_all_add_permissions(self):
        using_role = 'all'
        add_permission = ' /admin/forms'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/settings/permissions/%s' % using_role
            )
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                '/': 'y',
                '/admin/login': 'y',
                add_permission: 'y'
            }

            response = c.post(
                '/admin/settings/permissions/%s' % using_role,
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Permissions have been updated for %s' % using_role.title(),
            response.data,
            'Did not find or incorrect flash message after submit'
        )
        settings = pitchfork.db.settings.find_one()
        roles = settings.get('roles')
        has_perm = False
        for role in roles:
            if role.get('name') == using_role:
                perms = role.get('perms')
                if add_permission in perms:
                    has_perm = True
                    break

        assert has_perm, 'Permission path was not foundwith role'
        self.teardown_app_data()

    def test_roles_all_add_bad_data(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            using_role = 'all'
            data = {
                '/': 'y',
                '/admin/login': 'y'
            }
            response = c.post(
                '/admin/settings/permissions/%s' % using_role,
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Form validation failed, please check the form and try again',
            response.data,
            'Did not find or incorrect flash message after bad submit'
        )
        self.teardown_app_data()

    """ Manage Forms - Permissions Tests """

    def test_ui_admin_perms_forms(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            result = c.get('/admin/forms')

        assert result._status_code == 200, (
            'Invalid response code %s' % result._status_code
        )
        self.teardown_app_data()

    def test_ui_user_perms_forms(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)
            result = c.get('/admin/forms')

        assert result._status_code == 302, (
            'Invalid response code %s' % result._status_code
        )
        location = result.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )
        self.teardown_app_data()

    """ Functional Tests """

    def test_custom_forms_render_edit(self):
        using_form = 'login_form'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            form_element = pitchfork.db.forms.find_one({'name': using_form})
            response = c.get(
                '/admin/forms/%s' % form_element.get('_id')
            )

        self.assertIn(
            'value="login_form"',
            response.data,
            'Incorrect info when editing custom form'
        )
        self.teardown_app_data()

    def test_custom_forms_deactivate_form(self):
        using_form = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': using_form})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/forms/deactivate/%s' % form_element.get('_id'),
                follow_redirects=True
            )

        self.assertIn(
            'Successfully deactivated Custom Form',
            response.data,
            'Did not find or incorrect flash message after deactivation'
        )
        form_element = pitchfork.db.forms.find_one({'name': using_form})
        deactivated = False
        if not form_element.get('active'):
            deactivated = True

        assert deactivated, 'Form was not deactivated as expected.'
        self.teardown_app_data()

    def test_custom_forms_activate_form(self):
        using_form = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': using_form})
        pitchfork.db.forms.update(
            {
                '_id': form_element.get('_id')
            }, {
                '$set': {
                    'active': False
                }
            }
        )
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/forms/activate/%s' % form_element.get('_id'),
                follow_redirects=True
            )

        self.assertIn(
            'Successfully activated Custom Form',
            response.data,
            'Did not find or incorrect flash message after activation'
        )
        form_element = pitchfork.db.forms.find_one({'name': using_form})
        activated = False
        if form_element.get('active'):
            activated = True

        assert activated, 'Form was not activated as expected.'
        self.teardown_app_data()

    def test_custom_forms_add_new(self):
        form_name = 'Test Form'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/forms')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'submission_url': '/test',
                'active': 'y',
                'name': form_name,
            }
            response = c.post(
                'admin/forms',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Successfully added Custom Form',
            response.data,
            'Did not find or incorrect flash message after attempted add'
        )

        found_form = pitchfork.db.forms.find_one({'display_name': form_name})
        assert found_form, 'New form not found after add'
        self.teardown_app_data()

    def test_custom_forms_add_dup_name(self):
        dupe_form = 'login_form'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/forms')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'submission_url': 'y',
                'active': 'y',
                'name': dupe_form,
            }
            response = c.post(
                'admin/forms',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Form name already exists, please check the name and try again',
            response.data,
            (
                'Did not find or incorrect flash message '
                'after attempted add dup. name'
            )
        )
        self.teardown_app_data()

    def test_custom_forms_add_dup_route(self):
        dupe_route = '/admin/login'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/forms')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'submission_url': dupe_route,
                'active': 'y',
                'name': 'test',
            }
            response = c.post(
                'admin/forms',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            (
                'Another form posts to the same URL. '
                'Please check the URL and try again'
            ),
            response.data,
            (
                'Did not find or incorrect flash message '
                'after attempted add dup. route'
            )
        )
        self.teardown_app_data()

    def test_custom_forms_add_bad_data(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.post(
                'admin/forms',
                data={},
                follow_redirects=True
            )

        self.assertIn(
            'Form Validation failed',
            response.data,
            'Did not find or incorrect flash message after add with bad data'
        )
        self.teardown_app_data()

    def test_custom_forms_delete_system_form(self):
        delete_form = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': delete_form})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/forms/delete/%s' % form_element.get('_id'),
                follow_redirects=True
            )

        self.assertIn(
            'System form cannot be removed',
            response.data,
            'Did not find or incorrect flash message after attempted delete'
        )
        form_element = pitchfork.db.forms.find_one({'name': delete_form})
        assert form_element, 'Form was deleted when it should not have been'
        self.teardown_app_data()

    def test_custom_forms_delete_form(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            pitchfork.db.forms.insert(
                {
                    'display_name': 'Test',
                    'name': 'test',
                    'system_form': False,
                    'submission_url': '/test',
                    'active': True
                }
            )
            form_element = pitchfork.db.forms.find_one({'name': 'test'})
            response = c.get(
                '/admin/forms/delete/%s' % form_element.get('_id'),
                follow_redirects=True
            )

        self.assertIn(
            'Successfully removed Custom Form',
            response.data,
            'Did not find or incorrect flash message after attempted delete'
        )

        form_deleted = True
        form_element = pitchfork.db.forms.find_one({'name': 'test'})
        if form_element:
            form_deleted = False

        assert form_deleted, 'Form not deleted as expected'
        self.teardown_app_data()

    def test_custom_forms_edit(self):
        edit_form = 'login_form'
        change_name = 'Edit Form'
        form_element = pitchfork.db.forms.find_one({'name': edit_form})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/forms')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'name': 'edit_form',
                'submission_url': '/admin/login',
                'csrf_token': token,
                'active': 'y',
                'system_form': 'y'
            }

            response = c.post(
                '/admin/forms/%s' % form_element.get('_id'),
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Successfully updated Custom Form',
            response.data,
            'Did not find or incorrect flash message after edit login form'
        )

        form_element = pitchfork.db.forms.find_one(
            {
                'display_name': change_name
            }
        )
        assert form_element, 'Form was not edited as expected'
        self.teardown_app_data()

    def test_custom_forms_edit_dup_name(self):
        edit_form = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': edit_form})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/forms')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'name': 'manage_roles',
                'submission_url': '/admin/login',
                'csrf_token': token,
                'active': 'y',
                'system_form': 'y'
            }
            response = c.post(
                '/admin/forms/%s' % form_element.get('_id'),
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Form name already exists, please check the name and try again',
            response.data,
            'Did not find or incorrect flash message after edit login dup name'
        )

        form_element = pitchfork.db.forms.find_one({'name': edit_form})
        assert form_element, 'Form name was changed when it should not have'
        self.teardown_app_data()

    def test_custom_forms_edit_dup_submit_url(self):
        edit_form = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': edit_form})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/forms')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'name': edit_form,
                'submission_url': '/admin/settings/general',
                'csrf_token': token,
                'active': 'y',
                'system_form': 'y'
            }
            response = c.post(
                '/admin/forms/%s' % form_element.get('_id'),
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            (
                'Another form posts to the same URL. '
                'Please check the URL and try again'
            ),
            response.data,
            (
                'Did not find or incorrect flash message '
                'after edit login dup route'
            )
        )

        form_element = pitchfork.db.forms.find_one({'name': edit_form})
        form_url = False
        if form_element.get('submission_url') == '/admin/login':
            form_url = True

        assert form_url, 'Form route was updated when it was not supposed to'
        self.teardown_app_data()

    """ Manage Form Fields - Permissions Tests """

    def test_ui_admin_perms_form_fields(self):
        first_form = pitchfork.db.forms.find_one()
        form_id = first_form.get('_id')
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            result = c.get('/admin/forms/fields/%s' % form_id)

        assert result._status_code == 200, (
            'Invalid response code %s' % result._status_code
        )
        self.teardown_app_data()

    def test_ui_user_perms_form_fields(self):
        first_form = pitchfork.db.forms.find_one()
        form_id = first_form.get('_id')
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            result = c.get('/admin/forms/fields/%s' % form_id)

        assert result._status_code == 302, (
            'Invalid response code %s' % result._status_code
        )
        location = result.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )
        self.teardown_app_data()

    """ Functional Tests """

    def test_custom_form_fields_activate(self):
        field_to_use = 'username'
        form_to_use = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        pitchfork.db.forms.update(
            {
                '_id': form_element.get('_id'),
                'fields.name': field_to_use
            }, {
                '$set': {
                    'fields.$.active': False
                }
            }
        )
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/forms/fields/activate/%s/%s' % (
                    form_element.get('_id'),
                    field_to_use
                ),
                follow_redirects=True
            )

        self.assertIn(
            'Successfully activated Custom Field',
            response.data,
            'Did not find or incorrect flash message after activate'
        )
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        fields = form_element.get('fields')
        active_field = False
        for field in fields:
            if field.get('name') == field_to_use:
                if field.get('active'):
                    active_field = True
                    break

        assert active_field, 'Field was not activated as expected'
        self.teardown_app_data()

    def test_custom_form_fields_dedeactivate(self):
        field_to_use = 'username'
        form_to_use = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/forms/fields/deactivate/%s/%s' % (
                    form_element.get('_id'),
                    field_to_use
                ),
                follow_redirects=True
            )

        self.assertIn(
            'Successfully deactivated Custom Field',
            response.data,
            'Did not find or incorrect flash message after deactivated'
        )
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        fields = form_element.get('fields')
        active_field = False
        for field in fields:
            if field.get('name') == field_to_use:
                if not field.get('active'):
                    active_field = True
                    break

        assert active_field, 'Field was not deactivated as expected'
        self.teardown_app_data()

    def test_custom_form_fields_delete(self):
        field_to_use = 'username'
        form_to_use = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            form_element = pitchfork.db.forms.find_one({'name': form_to_use})
            response = c.get(
                '/admin/forms/fields/delete/%s/%s' % (
                    form_element.get('_id'),
                    field_to_use
                ),
                follow_redirects=True
            )

        self.assertIn(
            'Custom field was removed successfully',
            response.data,
            'Did not find or incorrect flash message after delete'
        )
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        fields = form_element.get('fields')
        deleted = True
        for field in fields:
            if field.get('name') == field_to_use:
                deleted = False
                break

        assert deleted, 'Field was not deleted as expected'
        self.teardown_app_data()

    def test_custom_form_fields_delete_bad_field(self):
        field_to_use = 'this-is-bad-field'
        form_to_use = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            form_element = pitchfork.db.forms.find_one({'name': form_to_use})
            response = c.get(
                '/admin/forms/fields/delete/%s/%s' % (
                    form_element.get('_id'),
                    field_to_use
                ),
                follow_redirects=True
            )

        self.assertIn(
            'Custom field was not found, and not removed',
            response.data,
            'Did not find or incorrect flash message after bad field delete'
        )
        self.teardown_app_data()

    def test_custom_form_fields_promote(self):
        field_to_use = 'password'
        form_to_use = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'field_name': field_to_use,
                'form_id': str(form_element.get('_id'))
            }
            response = c.post(
                '/admin/forms/fields/promote',
                data=json.dumps(data),
                content_type='application/json'
            )

        self.assertIn(
            'Password field has been promoted',
            json.loads(response.data).get('message'),
            'Did not find or incorrect flash message after promoting field'
        )
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        fields = form_element.get('fields')
        promoted = False
        for field in fields:
            if field.get('name') == field_to_use:
                if field.get('order') == 1:
                    promoted = True
                    break

        assert promoted, 'Field was not promoted as expected'
        self.teardown_app_data()

    def test_custom_form_fields_demote(self):
        field_to_use = 'username'
        form_to_use = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'field_name': field_to_use,
                'form_id': str(form_element.get('_id'))
            }
            response = c.post(
                '/admin/forms/fields/demote',
                data=json.dumps(data),
                content_type='application/json'
            )

        self.assertIn(
            'Username field has been demoted',
            json.loads(response.data).get('message'),
            'Did not find or incorrect flash message after demoting field'
        )

        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        fields = form_element.get('fields')
        demoted = False
        for field in fields:
            if field.get('name') == field_to_use:
                if field.get('order') == 2:
                    demoted = True
                    break

        assert demoted, 'Field was not demoted as expected'
        self.teardown_app_data()

    def test_custom_form_fields_add(self):
        field_to_use = 'field_test'
        form_to_use = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/forms/fields/%s' % form_element.get('_id')
            )
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': field_to_use,
                'label': 'testing add',
                'required': 'n',
                'active': 'y',
                'field_type': 'TextField',
                'form_id': str(form_element.get('_id'))
            }
            response = c.post(
                '/admin/forms/fields/%s' % form_element.get('_id'),
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Field successfully added to form',
            response.data,
            'Did not find or incorrect flash message after adding field'
        )
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        fields = form_element.get('fields')
        added = False
        for field in fields:
            if field.get('name') == field_to_use:
                added = True
                break

        assert added, 'Field was not added as expected'
        self.teardown_app_data()

    def test_custom_form_fields_add_dup_name(self):
        field_to_use = 'username'
        form_to_use = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/forms/fields/%s' % form_element.get('_id')
            )
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': field_to_use,
                'label': 'testing add',
                'required': 'n',
                'active': 'y',
                'field_type': 'TextField',
                'form_id': str(form_element.get('_id')),
            }
            response = c.post(
                '/admin/forms/fields/%s' % form_element.get('_id'),
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Field name already exists, please check the name and try again',
            response.data,
            'Did not find or incorrect flash message after adding field'
        )
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        fields = form_element.get('fields')
        added = True
        if len(fields) > 3:
            added = False

        assert added, 'Field was added when it was not supposed to be'
        self.teardown_app_data()

    def test_custom_form_fields_edit_render(self):
        field_to_use = 'username'
        form_to_use = 'login_form'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            form_element = pitchfork.db.forms.find_one({'name': form_to_use})
            response = c.get(
                '/admin/forms/fields/%s/%s' % (
                    form_element.get('_id'),
                    field_to_use
                )
            )

        self.assertIn(
            'value="username"',
            response.data,
            'Did not find or incorrect flash message after edit field render'
        )
        self.teardown_app_data()

    def test_custom_form_fields_edit_submit(self):
        field_to_use = 'username'
        form_to_use = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/forms/fields/%s' % form_element.get('_id')
            )
            token = self.retrieve_csrf_token(response.data)
            data = {
                'form_id': str(form_element.get('_id')),
                'name': 'username_test_edit',
                'required': 'y',
                'label': 'Username:',
                'field_type': 'TextField',
                'csrf_token': token,
                'active': 'y',
                'order': 1
            }
            response = c.post(
                '/admin/forms/fields/%s/%s' % (
                    form_element.get('_id'),
                    field_to_use
                ),
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Field successfully updated',
            response.data,
            'Did not find or incorrect flash message after edit'
        )
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        fields = form_element.get('fields')
        edited = False
        for field in fields:
            if field.get('name') == 'username_test_edit':
                edited = True
                break

        assert edited, 'Field was not edited correctly'
        self.teardown_app_data()

    def test_custom_form_fields_edit_dup_field_name(self):
        field_to_use = 'username'
        form_to_use = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/forms/fields/%s' % form_element.get('_id')
            )
            token = self.retrieve_csrf_token(response.data)
            data = {
                'form_id': str(form_element.get('_id')),
                'name': 'password',
                'required': 'y',
                'label': 'Username:',
                'field_type': 'TextField',
                'csrf_token': token,
                'active': 'y',
                'order': 1
            }
            response = c.post(
                '/admin/forms/fields/%s/%s' % (
                    form_element.get('_id'),
                    field_to_use
                ),
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Field name already exists, please check the name and try again',
            response.data,
            'Did not find or incorrect flash message after edit duplicate'
        )
        form_element = pitchfork.db.forms.find(
            {
                'name': form_to_use,
                'fields.name': field_to_use
            }
        )
        edited = True
        if form_element.count() != 1:
            edited = False

        assert edited, 'Field was edited when it was not supposed to'
        self.teardown_app_data()

    def test_custom_form_fields_edit_invalid_data(self):
        field_to_use = 'username'
        form_to_use = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/forms/fields/%s' % form_element.get('_id')
            )
            token = self.retrieve_csrf_token(response.data)
            data = {
                'form_id': str(form_element.get('_id')),
                'name': '',
                'required': 'y',
                'label': 'Username:',
                'field_type': 'TextField',
                'csrf_token': token,
                'active': 'y',
                'order': 1
            }
            response = c.post(
                '/admin/forms/fields/%s/%s' % (
                    form_element.get('_id'),
                    field_to_use
                ),
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Form validation error',
            response.data,
            'Did not find or incorrect flash message after edit with bad data'
        )
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        fields = form_element.get('fields')
        added = True
        if len(fields) > 3:
            added = False

        assert added, 'Field was added with bad data'
        self.teardown_app_data()

    def test_custom_form_fields_edit_render_select(self):
        field_to_use = 'menu_permissions'
        form_to_use = 'menu_items_form'
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/forms/fields/%s/%s' % (
                    form_element.get('_id'),
                    field_to_use
                )
            )

        self.assertIn(
            'value="menu_permissions"',
            response.data,
            (
                'Did not find or incorrect flash message '
                'after edit select field render'
            )
        )
        self.teardown_app_data()

    def test_custom_form_fields_add_choices(self):
        field_to_use = 'field_test'
        form_to_use = 'login_form'
        form_element = pitchfork.db.forms.find_one({'name': form_to_use})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/forms/fields/%s' % form_element.get('_id')
            )
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': field_to_use,
                'label': 'testing add',
                'field_choices': 'test,test1,test2',
                'required': 'n',
                'active': 'y',
                'field_type': 'SelectField',
                'form_id': str(form_element.get('_id'))
            }
            response_add = c.post(
                '/admin/forms/fields/%s' % form_element.get('_id'),
                data=data,
                follow_redirects=True
            )
            response_view = c.get(
                '/admin/login'
            )

        self.assertIn(
            'Field successfully added to form',
            response_add.data,
            'Did not find or incorrect flash message after adding field'
        )
        self.assertIn(
            (
                '<select id="field_test" name="field_test"><option value='
                '"test">test</option><option value="test1">test1</option>'
                '<option value="test2">test2</option></select>'
            ),
            response_view.data,
            'Did not find or incorrect select field in html'
        )
        self.teardown_app_data()

    """ Manage Menus - Permissions Tests """

    def test_ui_admin_perms_menus(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)
            result = c.get('/admin/settings/menu')

        assert result._status_code == 200, (
            'Invalid response code %s' % result._status_code
        )
        self.teardown_app_data()

    def test_ui_user_perms_menus(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)
            result = c.get('/admin/settings/menu')

        assert result._status_code == 302, (
            'Invalid response code %s' % result._status_code
        )
        location = result.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )
        self.teardown_app_data()

    """ Functional Tests """

    def test_menu_items_add_no_parent(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/menu')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'new_parent': '',
                'parent_menu': '',
                'menu_item_url': '/test',
                'menu_display_name': 'Test',
                'db_name': 'test',
                'menu_item_status': 'y',
                'menu_permissions': 'administrators'
            }
            response = c.post(
                '/admin/settings/menu',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Menu Item successfully Added',
            response.data,
            'Did not find or incorrect flash message after add'
        )
        db_menu_item = pitchfork.db.settings.find(
            {
                'menu.display_name': 'Test'
            }
        )
        self.assertEquals(
            db_menu_item.count(),
            1,
            'DB menu item count is incorrect after add'
        )
        db_top_menu = pitchfork.db.settings.find(
            {
                'top_level_menu.slug': 'test'
            }
        )
        self.assertEquals(
            db_top_menu.count(),
            1,
            'DB top level menu count is incorrect after add'
        )
        self.teardown_app_data()

    def test_menu_items_add_new_parent(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/menu')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'new_parent': 'parent name',
                'parent_menu': 'Add New Parent',
                'menu_item_url': '/test',
                'menu_display_name': 'Test',
                'db_name': 'test',
                'menu_item_status': 'y',
                'menu_permissions': 'administrators'
            }
            response = c.post(
                '/admin/settings/menu',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Menu Item successfully Added',
            response.data,
            'Did not find or incorrect flash message after add with parent'
        )
        db_menu_item = pitchfork.db.settings.find(
            {
                'menu.display_name': 'Test'
            }
        )
        self.assertEquals(
            db_menu_item.count(),
            1,
            'DB menu item count is incorrect after add with parent'
        )
        db_top_menu = pitchfork.db.settings.find(
            {
                'top_level_menu.slug': 'parent_name'
            }
        )
        self.assertEquals(
            db_top_menu.count(),
            1,
            'DB top level menu count is incorrect after add with parent'
        )
        self.teardown_app_data()

    def test_menu_items_add_existing_parent(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/menu')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'new_parent': '',
                'parent_menu': 'administrators',
                'menu_item_url': '/test',
                'menu_display_name': 'Test',
                'db_name': 'test',
                'menu_item_status': 'y',
                'menu_permissions': 'administrators'
            }
            response = c.post(
                '/admin/settings/menu',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Menu Item successfully Added',
            response.data,
            (
                'Did not find or incorrect flash message '
                'after add with existing parent'
            )
        )
        db_menu_item = pitchfork.db.settings.find(
            {
                'menu.display_name': 'Test'
            }
        )
        self.assertEquals(
            db_menu_item.count(),
            1,
            'DB menu item count is incorrect after add with existing parent'
        )
        db_top_menu = pitchfork.db.settings.find_one({})
        self.assertEquals(
            len(db_top_menu.get('top_level_menu')),
            7,
            (
                'DB top level menu length is incorrect '
                'after add with existing parent'
            )
        )
        self.teardown_app_data()

    def test_menu_items_add_missing_data(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'new_parent': '',
                'parent_menu': 'administrators',
                'menu_item_url': '/test',
                'menu_display_name': '',
                'db_name': 'test',
                'menu_item_status': 'y',
                'menu_permissions': 'administrators'
            }
            response = c.post(
                '/admin/settings/menu',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Form validation failed. Please check the form and try again',
            response.data,
            (
                'Did not find or incorrect flash message '
                'after add with missing data'
            )
        )
        found = pitchfork.db.settings.find(
            {
                'menu.db_name': 'test'
            }
        )
        self.assertEquals(
            found.count(),
            0,
            'Menu item count is incorrect after bad data add'
        )
        self.teardown_app_data()

    def test_menu_items_add_duplicate_name(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/menu')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'new_parent': '',
                'parent_menu': '',
                'menu_item_url': '/test',
                'menu_display_name': 'Test',
                'db_name': 'general_settings',
                'menu_item_status': 'y',
                'menu_permissions': 'administrators'
            }
            response = c.post(
                '/admin/settings/menu',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Name already exists, please choose another name',
            response.data,
            (
                'Did not find or incorrect flash message '
                'after add with duplicate name'
            )
        )
        found = pitchfork.db.settings.find(
            {'menu.db_name': 'general_settings'}
        )
        self.assertEquals(
            found.count(),
            0,
            'Menu item count is incorrect after duplicate db name'
        )
        self.teardown_app_data()

    def test_menu_items_add_duplicate_parent(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/menu')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'new_parent': 'Administrators',
                'parent_menu': 'Add New Parent',
                'menu_item_url': '/test',
                'menu_display_name': 'Test',
                'db_name': 'test_duplicate',
                'menu_item_status': 'y',
                'menu_permissions': 'administrators'
            }
            response = c.post(
                '/admin/settings/menu',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Parent is already in use, please check the value and try again',
            response.data,
            (
                'Did not find or incorrect flash message '
                'after add with duplicate parent'
            )
        )
        settings = pitchfork.db.settings.find_one()
        top_menu = settings.get('top_level_menu')
        count = 0
        for menu in top_menu:
            if menu.get('slug') == 'administrators':
                count += 1
        only_one = True
        if count > 1:
            only_one = False

        assert only_one, 'To many top parents were found'
        self.teardown_app_data()

    def test_menu_items_add_duplicate_url(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/menu')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'new_parent': '',
                'parent_menu': '',
                'menu_item_url': '/admin/forms',
                'menu_display_name': 'Test',
                'db_name': 'test_duplicate',
                'menu_item_status': 'y',
                'menu_permissions': 'administrators'
            }
            response = c.post(
                '/admin/settings/menu',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'URL is already being used, please check the URL and try again',
            response.data,
            (
                'Did not find or incorrect flash message '
                'after add with duplicate URL'
            )
        )
        settings = pitchfork.db.settings.find_one()
        top_menu = settings.get('menu')
        count = 0
        for menu in top_menu:
            if menu.get('url') == 'admin/forms':
                count += 1
        only_one = True
        if count > 1:
            only_one = False

        assert only_one, 'To many menu items with the same url were found'
        self.teardown_app_data()

    def test_menu_items_add_blank_parent(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/menu')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'new_parent': '',
                'parent_menu': 'Add New Parent',
                'menu_item_url': '/test_url',
                'menu_display_name': 'Test',
                'db_name': 'test_duplicate',
                'menu_item_status': 'y',
                'menu_permissions': 'administrators'
            }
            response = c.post(
                '/admin/settings/menu',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'New Parent cannot be blank when adding a new Parent Item',
            response.data,
            (
                'Did not find or incorrect flash message '
                'after add with blank parent'
            )
        )
        menu_item = pitchfork.db.settings.find({'menu.name': 'test'})
        self.assertEquals(
            menu_item.count(),
            0,
            'Menu item count is incorrect after blank parent name'
        )
        self.teardown_app_data()

    def test_menu_items_edit_render(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/settings/menu/general_settings',
                follow_redirects=True
            )

        self.assertIn(
            'value="General Settings"',
            response.data,
            'Did not find or incorrect flash message after edit menu render'
        )
        self.teardown_app_data()

    def test_menu_items_edit_render_bad_menu(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/settings/menu/do_not_exist',
                follow_redirects=True
            )

        self.assertIn(
            'Manage Application Menus',
            response.data,
            'Did not find or incorrect flash message after edit menu render'
        )
        self.teardown_app_data()

    def test_menu_items_edit_menu(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/menu')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'new_parent': '',
                'parent_menu': 'system',
                'menu_item_url': '/admin/settings/admins',
                'menu_display_name': 'Menu Edit',
                'db_name': ' manage_admins',
                'menu_item_status': 'y',
                'menu_permissions': 'administrators'
            }
            response = c.post(
                '/admin/settings/menu/manage_admins',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Menu Item was edited successfully',
            response.data,
            'Did not find or incorrect flash message after edit menu item'
        )
        found = pitchfork.db.settings.find({'menu.display_name': 'Menu Edit'})
        self.assertEquals(
            found.count(),
            1,
            'Menu item count is incorrect after edit'
        )
        self.teardown_app_data()

    def test_menu_items_edit_menu_duplicate_name(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/menu')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'new_parent': '',
                'parent_menu': '',
                'menu_item_url': '/',
                'menu_display_name': 'Home',
                'db_name': 'general_settings',
                'menu_item_status': 'y',
                'menu_permissions': 'administrators'
            }
            response = c.post(
                '/admin/settings/menu/home',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Name already exists, please choose another name',
            response.data,
            'Did not find or incorrect flash message after edit dupe name'
        )
        settings = pitchfork.db.settings.find_one()
        menus = settings.get('menu')
        count = 0
        for menu in menus:
            if menu.get('name') == 'general_settings':
                count += 1

        self.assertEquals(
            count,
            1,
            'Menu item count is incorrect after duplicate name'
        )
        self.teardown_app_data()

    def test_menu_items_edit_menu_duplicate_url(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/menu')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'new_parent': '',
                'parent_menu': '',
                'menu_item_url': '/admin/settings/admins',
                'menu_display_name': 'Test',
                'db_name': 'test',
                'menu_item_status': 'y',
                'menu_permissions': 'administrators'
            }
            response = c.post(
                '/admin/settings/menu/home',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'URL is already being used, please check the URL and try again',
            response.data,
            'Did not find or incorrect flash message after edit dup url'
        )
        settings = pitchfork.db.settings.find_one()
        menus = settings.get('menu')
        count = 0
        for menu in menus:
            if menu.get('url') == '/admin/settings/admins':
                count += 1

        self.assertEquals(
            count,
            1,
            'Menu item count is incorrect after duplicate url'
        )
        self.teardown_app_data()

    def test_menu_items_edit_menu_new_parent(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/menu')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'new_parent': 'Test Parent',
                'parent_menu': 'Add New Parent',
                'menu_item_url': '/',
                'menu_display_name': 'General Settings',
                'db_name': 'general_settings',
                'menu_item_status': 'y',
                'menu_permissions': 'administrators'
            }
            response = c.post(
                '/admin/settings/menu/general_settings',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Menu Item was edited successfully',
            response.data,
            'Did not find or incorrect flash message after edit new parent'
        )
        found = pitchfork.db.settings.find(
            {
                'top_level_menu.slug': 'test_parent'
            }
        )
        self.assertEquals(
            found.count(),
            1,
            'Menu item count is incorrect after adding new parent on edit'
        )
        self.teardown_app_data()

    def test_menu_items_edit_menu_duplicate_parent(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/menu')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'new_parent': 'Administrators',
                'parent_menu': 'Add New Parent',
                'menu_item_url': '/',
                'menu_display_name': 'Home',
                'db_name': 'home',
                'menu_item_status': 'y',
                'menu_permissions': 'administrators'
            }
            response = c.post(
                '/admin/settings/menu/home',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Parent is already in use, please check the value and try again',
            response.data,
            'Did not find or incorrect flash message after edit dup parent'
        )
        settings = pitchfork.db.settings.find_one()
        menus = settings.get('top_level_menu')
        count = 0
        for menu in menus:
            if menu.get('slug') == 'administrators':
                count += 1

        self.assertEquals(
            count,
            1,
            'Top Menu item count is incorrect after duplicate parent'
        )
        self.teardown_app_data()

    def test_menu_items_edit_menu_blank_parent(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/menu')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'new_parent': '',
                'parent_menu': 'Add New Parent',
                'menu_item_url': '/',
                'menu_display_name': 'Home',
                'db_name': 'home',
                'menu_item_status': 'y',
                'menu_permissions': 'administrators'
            }
            response = c.post(
                '/admin/settings/menu/home',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'New Parent cannot be blank when adding a new Parent Item',
            response.data,
            'Did not find or incorrect flash message after edit blank parent'
        )
        settings = pitchfork.db.settings.find_one()
        menus = settings.get('top_level_menu')
        self.assertEquals(
            len(menus),
            7,
            'Top Menu item count is incorrect after blank parent'
        )
        self.teardown_app_data()

    def test_menu_items_edit_menu_promote_top_level(self):
        to_use = 'Administrators'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {'name': to_use}
            response = c.post(
                '/admin/settings/menu/top_level/promote',
                data=json.dumps(data),
                content_type='application/json',
                follow_redirects=True
            )

        self.assertIn(
            'Top Level Menu Item has been promoted',
            response.data,
            'Did not find or incorrect flash message after top level promote'
        )
        settings = pitchfork.db.settings.find_one()
        menus = settings.get('top_level_menu')
        order = False
        for menu in menus:
            if menu.get('name') == to_use:
                if menu.get('order') == 6:
                    order = True

        assert order, 'Parent order is not correct after promote'
        self.teardown_app_data()

    def test_menu_items_edit_menu_demote_top_level(self):
        to_use = 'System'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {'name': to_use}
            response = c.post(
                '/admin/settings/menu/top_level/demote',
                data=json.dumps(data),
                content_type='application/json',
                follow_redirects=True
            )

        self.assertIn(
            'Top Level Menu Item has been demoted',
            response.data,
            'Did not find or incorrect flash message after top level demote'
        )
        settings = pitchfork.db.settings.find_one()
        menus = settings.get('top_level_menu')
        order = False
        for menu in menus:
            if menu.get('name') == to_use:
                if menu.get('order') == 7:
                    order = True

        assert order, 'Parent order is not correct after demote'
        self.teardown_app_data()

    def test_menu_items_edit_menu_promote_menu_item(self):
        to_use = 'manage_roles'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {'name': to_use}
            response = c.post(
                '/admin/settings/menu/promote',
                data=json.dumps(data),
                content_type='application/json',
                follow_redirects=True
            )

        self.assertIn(
            'Menu Item has been promoted',
            response.data,
            'Did not find or incorrect flash message after top level promote'
        )
        settings = pitchfork.db.settings.find_one()
        menus = settings.get('menu')
        order = False
        for menu in menus:
            if menu.get('name') == to_use:
                if menu.get('order') == 2:
                    order = True

        assert order, 'Menu order is not correct after promote'
        self.teardown_app_data()

    def test_menu_items_edit_menu_demote_menu_item(self):
        to_use = 'manage_roles'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {'name': to_use}
            response = c.post(
                '/admin/settings/menu/demote',
                data=json.dumps(data),
                content_type='application/json',
                follow_redirects=True
            )

        self.assertIn(
            'Menu Item has been demoted',
            response.data,
            'Did not find or incorrect flash message after top level demote'
        )
        settings = pitchfork.db.settings.find_one()
        menus = settings.get('menu')
        order = False
        for menu in menus:
            if menu.get('name') == to_use:
                if menu.get('order') == 4:
                    order = True

        assert order, 'Menu order is not correct after promote'
        self.teardown_app_data()

    def test_menu_items_edit_menu_enable_menu_item(self):
        to_use = 'manage_roles'
        pitchfork.db.settings.update(
            {
                'menu.name': to_use
            }, {
                '$set': {
                    'menu.$.active': False
                }
            }
        )
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/settings/menu/toggle/enable/%s' % to_use,
                follow_redirects=True
            )

        self.assertIn(
            'Menu Item %s status was changed' % to_use,
            response.data,
            'Did not find or incorrect flash message after menu item enable'
        )
        settings = pitchfork.db.settings.find_one()
        menus = settings.get('menu')
        enabled = False
        for menu in menus:
            if menu.get('name') == to_use:
                if menu.get('active'):
                    enabled = True

        assert enabled, 'Menu was not enabled'
        self.teardown_app_data()

    def test_menu_items_edit_menu_disable_menu_item(self):
        to_use = 'manage_roles'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/settings/menu/toggle/disable/%s' % to_use,
                follow_redirects=True
            )

        self.assertIn(
            'Menu Item %s status was changed' % to_use,
            response.data,
            'Did not find or incorrect flash message after menu item enable'
        )
        settings = pitchfork.db.settings.find_one()
        menus = settings.get('menu')
        enabled = False
        for menu in menus:
            if menu.get('name') == to_use:
                if not menu.get('active'):
                    enabled = True

        assert enabled, 'Menu was not disabled'
        self.teardown_app_data()

    def test_menu_items_edit_menu_delete_menu_item(self):
        to_use = 'manage_roles'
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/settings/menu/remove/%s' % to_use,
                follow_redirects=True
            )

        self.assertIn(
            'Menu Item %s was successfully removed' % to_use,
            response.data,
            'Did not find or incorrect flash message after menu item enable'
        )
        found = pitchfork.db.settings.find({'menu.name': to_use})
        self.assertEquals(
            found.count(),
            0,
            'Menu item count is incorrect after deletes'
        )
        self.teardown_app_data()

    def test_top_menu_display_html(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/settings/menu/top_level/html'
            )

        self.assertIn(
            'Administrators',
            response.data,
            'Did not find top level menu in returned HTML'
        )
        self.teardown_app_data()

    def test_child_menu_display_html(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/admin/settings/menu/child/html'
            )
        self.assertIn(
            'administrators',
            response.data,
            'Did not find child level menu in returned HTML'
        )
        self.teardown_app_data()

    def test_menu_items_delete_child_with_parent(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/menu')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'new_parent': 'parent name',
                'parent_menu': 'Add New Parent',
                'menu_item_url': '/test',
                'menu_display_name': 'Test',
                'db_name': 'test',
                'menu_item_status': 'y',
                'menu_permissions': 'administrators'
            }
            add_response = c.post(
                '/admin/settings/menu',
                data=data,
                follow_redirects=True
            )
            response = c.get(
                '/admin/settings/menu/remove/test',
                follow_redirects=True
            )

        self.assertIn(
            'Menu Item test was successfully removed',
            response.data,
            (
                'Did not find or incorrect flash message '
                'after delete child with parent'
            )
        )
        db_menu_item = pitchfork.db.settings.find(
            {
                'menu.display_name': 'Test'
            }
        )
        self.assertEquals(
            db_menu_item.count(),
            0,
            (
                'DB menu item count is incorrect after'
                ' remove child and parent'
            )
        )
        db_top_menu = pitchfork.db.settings.find(
            {
                'top_level_menu.slug': 'parent_name'
            }
        )
        self.assertEquals(
            db_top_menu.count(),
            0,
            (
                'DB top level menu count is incorrect '
                'after remove child with parent'
            )
        )
        self.teardown_app_data()

    def test_menu_items_delete_child_with_parent_order_is_front(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/menu')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'new_parent': 'parent name',
                'parent_menu': 'Add New Parent',
                'menu_item_url': '/test',
                'menu_display_name': 'Test',
                'db_name': 'test',
                'menu_item_status': 'y',
                'menu_permissions': 'administrators'
            }
            add_response = c.post(
                '/admin/settings/menu',
                data=data,
                follow_redirects=True
            )
            data = {'name': 'test'}
            response_promote = c.post(
                '/admin/settings/menu/promote',
                data=json.dumps(data),
                content_type='application/json',
                follow_redirects=True
            )
            response_promote = c.post(
                '/admin/settings/menu/promote',
                data=json.dumps(data),
                content_type='application/json',
                follow_redirects=True
            )

            response = c.get(
                '/admin/settings/menu/remove/test',
                follow_redirects=True
            )

        self.assertIn(
            'Menu Item test was successfully removed',
            response.data,
            (
                'Did not find or incorrect flash message '
                'after delete child with parent'
            )
        )
        db_menu_item = pitchfork.db.settings.find(
            {
                'menu.display_name': 'Test'
            }
        )
        self.assertEquals(
            db_menu_item.count(),
            0,
            (
                'DB menu item count is incorrect after remove child and parent'
            )
        )
        db_top_menu = pitchfork.db.settings.find(
            {
                'top_level_menu.slug': 'parent_name'
            }
        )
        self.assertEquals(
            db_top_menu.count(),
            0,
            (
                'DB top level menu count is incorrect '
                'after remove child with parent'
            )
        )
        self.teardown_app_data()

    def test_menu_items_delete_top_with_parent_and_children_behind(self):
        settings = pitchfork.db.settings.find_one()
        top_level_add = [
            {
                'slug': 'test',
                'name': 'Test',
                'order': 8
            }, {
                'slug': 'test2',
                'name': 'Test2',
                'order': 9
            }
        ]
        for item in top_level_add:
            pitchfork.db.settings.update(
                {
                    '_id': settings.get('_id')
                }, {
                    '$push': {
                        'top_level_menu': item
                    }
                }
            )

        add_menus = [
            {
                'active': True,
                'display_name': 'Test',
                'name': 'test',
                'parent': '',
                'url': '/test',
                'parent_order': 8,
                'order': 1,
                'view_permissions': 'administrators'
            }, {
                'active': True,
                'display_name': 'Test2',
                'name': 'test2',
                'parent': 'test2',
                'url': '/test2',
                'parent_order': 9,
                'order': 1,
                'view_permissions': 'administrators'
            }, {
                'active': True,
                'display_name': 'Test3',
                'name': 'test3',
                'parent': 'test2',
                'url': '/test3',
                'parent_order': 9,
                'order': 2,
                'view_permissions': 'administrators'
            }
        ]
        for item in add_menus:
            pitchfork.db.settings.update(
                {
                    '_id': settings.get('_id')
                }, {
                    '$push': {
                        'menu': item
                    }
                }
            )

        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/admin/settings/menu')
            token = self.retrieve_csrf_token(response.data)
            response = c.get(
                '/admin/settings/menu/remove/test',
                follow_redirects=True
            )

        self.assertIn(
            'Menu Item test was successfully removed',
            response.data,
            (
                'Did not find or incorrect flash message '
                'after delete child with parent'
            )
        )
        settings = pitchfork.db.settings.find_one()
        top_level_menu = settings.get('top_level_menu')
        menus = settings.get('menu')
        db_top_order = pitchfork.db.settings.find_one(
            {
                'top_level_menu.order': 9
            }
        )
        top_level_find = True
        if db_top_order:
            top_level_find = False

        assert top_level_find, (
            'Found wrong order in top levels as it should be eight'
        )
        db_menu_order = pitchfork.db.settings.find_one(
            {
                'menu.parent_order': 9
            }
        )
        menu_find = True
        if db_menu_order:
            menu_find = False

        assert menu_find, (
            'Found wrong parent order as it should be eight in menus'
        )

        parent_count = 0
        for menu in menus:
            if menu.get('parent_order') == 8:
                parent_count += 1

        parent_find = True
        if parent_count != 2:
            parent_find = False

        assert parent_find, (
            'Wrong number of child items '
            'found. Should be 2 found %d' % parent_count
        )

        self.teardown_app_data()

    """ Misc API Browse tests """

    def test_pf_history(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/history')

        self.assertIn(
            'API Call History',
            response.data,
            'Did not find correct HTML on page'
        )
        self.teardown_app_data()

    def test_pf_search(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            data = {
                'search_string': 'List'
            }
            response = c.post(
                '/search',
                data=json.dumps(data),
                content_type='application/json'
            )

        self.assertIn(
            'No API calls were found to display',
            response.data,
            'Did not find correct HTML on page'
        )
        self.teardown_app_data()

    """ End Browse """

    """ Datacenters Management - Perms Test """

    def test_pf_manage_dcs_admin_perms(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/dcs')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Manage Data Centers',
            response.data,
            'Did not find correct HTML on page'
        )
        self.teardown_app_data()

    def test_pf_manage_dcs_user_perms(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            result = c.get('/manage/dcs')

        assert result._status_code == 302, (
            'Invalid response code %s' % result._status_code
        )
        location = result.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )
        self.teardown_app_data()

    """ Functional Tests """

    def test_pf_manage_dcs_add(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/dcs')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': 'Test',
                'abbreviation': 'TEST'
            }
            response = c.post(
                '/manage/dcs',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'DC successfully added to system',
            response.data,
            'Incorrect flash message after add'
        )
        found_add = pitchfork.db.api_settings.find_one(
            {
                'dcs.name': 'Test'
            }
        )
        assert found_add, 'DC not found after add'
        self.teardown_app_data()

    def test_pf_manage_dcs_add_no_dcs(self):
        pitchfork.db.api_settings.update({}, {'$unset': {'dcs': 1}})
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/dcs')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': 'Test',
                'abbreviation': 'TEST'
            }
            response = c.post(
                '/manage/dcs',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'DC successfully added to system',
            response.data,
            'Incorrect flash message after add'
        )
        found_add = pitchfork.db.api_settings.find_one(
            {
                'dcs.name': 'Test'
            }
        )
        assert found_add, 'DC not found after add'
        self.teardown_app_data()

    def test_pf_manage_dcs_add_dupe(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/dcs')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': 'Dallas',
                'abbreviation': 'DFW'
            }

            response = c.post(
                '/manage/dcs',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'DC Dallas is already setup, no need to add it again',
            response.data,
            'Incorrect flash message after add duplicate'
        )
        api_settings = pitchfork.db.api_settings.find_one()
        dcs = api_settings.get('dcs')
        count = 0
        for dc in dcs:
            if dc.get('name') == 'Dallas':
                count += 1

        self.assertEquals(
            count,
            1,
            'Incorrect count after dupe add found %d instead of 1' % count
        )
        self.teardown_app_data()

    def test_pf_manage_dcs_add_bad_data(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/dcs')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'name': 'Test',
                'abbreviation': 'TEST'
            }
            response = c.post(
                '/manage/dcs',
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
        self.teardown_app_data()

    def test_pf_manage_dcs_remove(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/dcs/delete/Dallas',
                follow_redirects=True
            )

        self.assertIn(
            'Dallas was deleted successfully',
            response.data,
            'Incorrect flash message after remove'
        )
        api_settings = pitchfork.db.api_settings.find_one()
        dcs = api_settings.get('dcs')
        count = 0
        for dc in dcs:
            if dc.get('name') == 'Dallas':
                count += 1

        self.assertEquals(
            count,
            0,
            'Incorrect count after remove, found %d instead of 0' % count
        )
        self.teardown_app_data()

    """ Verbs Management - Perms Test """

    def test_pf_verbs_admin_perms(self):
        with pitchfork.app.test_client() as c:
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
        self.teardown_app_data()

    def test_pf_verbs_user_perms(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            result = c.get('/manage/verbs')

        assert result._status_code == 302, (
            'Invalid response code %s' % result._status_code
        )
        location = result.headers.get('Location')
        o = urlparse.urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )
        self.teardown_app_data()

    """ Functional Tests """

    def test_pf_verbs_add(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/dcs')
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
        found_add = pitchfork.db.api_settings.find_one(
            {
                'verbs.name': 'TEST'
            }
        )
        assert found_add, 'Verb not found after add'
        self.teardown_app_data()

    def test_pf_verbs_add_dupe(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/dcs')
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
            'Verb GET is already setup, no need to add it again',
            response.data,
            'Incorrect flash message after add duplicate'
        )
        api_settings = pitchfork.db.api_settings.find_one()
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
        self.teardown_app_data()

    def test_pf_verbs_add_bad_data(self):
        with pitchfork.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/dcs')
            token = self.retrieve_csrf_token(response.data)
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
        self.teardown_app_data()

    def test_pf_verbs_remove(self):
        with pitchfork.app.test_client() as c:
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
        api_settings = pitchfork.db.api_settings.find_one()
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
        self.teardown_app_data()

    def test_pf_verbs_deactivate(self):
        with pitchfork.app.test_client() as c:
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
        api_settings = pitchfork.db.api_settings.find_one()
        verbs = api_settings.get('verbs')
        deactivated = False
        for verb in verbs:
            if verb.get('name') == 'GET':
                if not verb.get('active'):
                    deactivated = True

        assert deactivated, 'Verb was not deactivated'
        self.teardown_app_data()

    def test_pf_verbs_activate(self):
        pitchfork.db.api_settings.update(
            {
                'verbs.name': 'GET'
            }, {
                '$set': {
                    'verbs.$.active': False
                }
            }
        )
        with pitchfork.app.test_client() as c:
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
        api_settings = pitchfork.db.api_settings.find_one()
        verbs = api_settings.get('verbs')
        activated = False
        for verb in verbs:
            if verb.get('name') == 'GET':
                if verb.get('active'):
                    activated = True

        assert activated, 'Verb was not activated'
        self.teardown_app_data()

    def test_pf_bad_key_for_actions(self):
        with pitchfork.app.test_client() as c:
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
        api_settings = pitchfork.db.api_settings.find_one()
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
        self.teardown_app_data()

    def test_pf_bad_action_for_actions(self):
        with pitchfork.app.test_client() as c:
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
        api_settings = pitchfork.db.api_settings.find_one()
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
        self.teardown_app_data()

    def test_pf_bad_dat_element_for_actions(self):
        with pitchfork.app.test_client() as c:
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
        api_settings = pitchfork.db.api_settings.find_one()
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
        self.teardown_app_data()

if __name__ == '__main__':
    unittest.main()
