from selenium import webdriver
from selenium.webdriver.support.ui import Select
from pitchfork import setup_application
from datetime import datetime


import unittest
import threading
import time
import uuid
import mock
import os


class SeleniumTests(unittest.TestCase):
    client, db = None, None

    @classmethod
    def setUpClass(cls):
        try:
            cls.client = webdriver.PhantomJS(service_log_path=os.path.devnull)
            # cls.client = webdriver.Firefox()
        except:
            pass

        if cls.client:
            cls.app, cls.db = setup_application.create_app(True)
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")

            test_thread = threading.Thread(target=cls.app.run)
            test_thread.setDaemon(True)
            test_thread.start()

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            cls.client.close()
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('PhantomJS not available to run browser tests')
        else:
            self.client.get('http://localhost:5000')
            self.client.get('http://localhost:5000')

    def setup_database(self, tested=None, variables=None):
        data = {
            'api_uri': '{ddi}/groups',
            'doc_url': 'http://docs.rackspace.com',
            'short_description': 'Test API Call',
            'title': 'Test Call',
            'verb': 'GET',
            'use_data': False,
            'variables': []
        }
        if tested:
            data['tested'] = True

        if variables:
            data['api_uri'] += '/{test_var_value}'
            data['variables'] = [{
                'field_type': 'text',
                'description': 'Test Variable',
                'required': True,
                'field_display_data': '',
                'id_value': 0,
                'field_display': 'TextField',
                'variable_name': 'test_var_value'
            }]

        self.db.autoscale.insert(data)

    def setup_call_history(self):
        data = {
            'username': 'rusty.shackelford',
            'completed_at': datetime.now(),
            'ddi': '123456',
            'details': {
                'description': 'List public virtual machine images',
                'doc_url': 'https://doc_url.com',
                'title': 'List Groups'
            },
            'data_center': 'dfw',
            'product': 'Images',
            'request': {
                'url': (
                    'https://dfw.autoscale.api.rackspace.com/v1/123456/groups'
                ),
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
                    'x-newrelic-app-data': 'newrelic-data',
                    'server': 'Jetty(8.y.z-SNAPSHOT)',
                    'last-modified': 'Tue, 29 Jul 2014 17:17:46 GMT',
                    'connection': 'Keep-Alive',
                    'etag': 'W/\'5406-1406654266000\'',
                    'date': 'Fri, 08 Aug 2014 19:48:27 GMT',
                    'content-type': 'application/xml;charset=UTF-8'
                },
                'code': 200
            },
            'name': None
        }
        self.db.history.insert(data)

    def setup_user_logged_in(self, admin=None):
        today = datetime.now()
        tomorrow = '%s-%s-%s' % (today.year, today.month, today.day + 1)
        self.client.get('http://localhost:5000/admin/login')
        username = self.client.find_element_by_id('username')
        password = self.client.find_element_by_id('password')
        if admin:
            username.send_keys('rusty.shackelford')
        else:
            username.send_keys('bob.richards')

        password.send_keys('%s' % uuid.uuid4().hex)
        with mock.patch('requests.post') as patched_post:
            type(patched_post.return_value).content = mock.PropertyMock(
                return_value=(
                    '{"access": {"token": {"RAX-AUTH:authenticatedBy": '
                    '["APIKEY"], "expires": "%sT04:17:18.880Z", '
                    '"id": "a359c49c0e6f4b2db32618cc98137a8d", "tenant": '
                    '{"id": "123456","name": "123456"}}}}' % tomorrow
                )
            )
            login_button = self.client.find_element_by_id('submit')
            login_button.click()

    def tearDown(self):
        self.db.autoscale.remove()
        self.db.history.remove()
        self.client.get('http://localhost:5000/admin/logout')

    def test_pf_front_not_logged_in(self):
        self.client.get('http://localhost:5000')
        self.assertIn('Pitchfork', self.client.title)
        self.assertTrue(
            'title="Login to Application" href="/admin/login">'
            'Login to Application</a>',
            self.client.page_source
        )

    def test_pf_login_page(self):
        self.client.get('http://localhost:5000/admin/login')
        self.assertIn(
            'Login to Application',
            self.client.page_source,
            'Could not find correct log in page title'
        )

    def test_pf_product_browse_nli_no_calls(self):
        self.client.get('http://localhost:5000/autoscale')
        self.assertIn(
            '<li class="navbar-header">API Calls</li>',
            self.client.page_source,
            'Did not find correct side menu header on autoscale'
        )
        self.assertIn(
            'Autoscale - API Calls',
            self.client.page_source,
            'Did not find correct title for Autoscale'
        )

    def test_pf_product_browse_nli_with_calls(self):
        self.setup_database(True)
        self.client.get('http://localhost:5000/autoscale/')
        toc = self.client.find_element_by_class_name('toc')
        assert toc.text == 'Test Call', 'Did not find link on side menu'
        self.assertIn(
            'Test API Call',
            self.client.page_source,
            'Did not find correct title for Autoscale in panel view'
        )
        self.assertIn(
            (
                'data-content="http://localhost:5000/autoscale'
                '/#test_call-autoscale"'
            ),
            self.client.page_source,
            'Did not find correct link data for test call'
        )

    def test_pf_product_nli_interaction_with_call_display(self):
        self.setup_database(True)
        self.client.get('http://localhost:5000/autoscale/')
        self.client.find_element_by_class_name('prod-popover').click()
        self.assertTrue(
            self.client.find_element_by_class_name(
                'popover-content'
            ).is_displayed(),
            'Link popover was not displayed correctly after click'
        )
        self.client.find_element_by_class_name('prod-popover').click()
        try:
            self.client.find_element_by_class_name('popover-content')
            assert False, (
                'Popover was found and should have been hidden by click'
            )
        except:
            pass

        details = self.client.find_element_by_id('api_call_inner')
        assert not details.is_displayed(), 'Details element should not be seen'
        details_button = self.client.find_element_by_class_name(
            'toggle-element-1'
        )
        details_button.click()
        time.sleep(1)
        self.assertEquals(
            details_button.text,
            'Hide Details',
            'Button text did not change after show'
        )
        assert details.is_displayed(), (
            'Details are not disaplayed as they should have been'
        )
        assert self.client.find_element_by_id(
            'test_call-autoscale_form'
        ).is_displayed(), 'Form not displayed properly'

    def test_pf_product_mock_call_not_logged_in(self):
        self.setup_database(True)
        self.client.get('http://localhost:5000/autoscale/')

        details_button = self.client.find_element_by_class_name(
            'toggle-element-1'
        )
        details_button.click()
        time.sleep(1)
        mock_button = self.client.find_element_by_name('test_call-autoscale')
        mock_results = self.client.find_element_by_class_name(
            'code-blocks-wrapper'
        )
        assert not mock_results.is_displayed(), (
            'Call results should not be displayed yet'
        )
        mock_button.click()
        time.sleep(1)
        assert mock_results.is_displayed(), (
            'Call results should be displayed and are not'
        )
        self.assertIn(
            'https://{data_center}',
            mock_results.text,
            'Could not find request URL in mock return'
        )
        self.assertIn(
            '"Content-Type": "application/json"',
            mock_results.text,
            'Could not find request headers content type'
        )
        hide_results = self.client.find_element_by_id('toggle_results')
        self.assertIn(
            hide_results.text,
            'Hide Results',
            'Incorrect wording on hide results button'
        )
        hide_results.click()
        time.sleep(1)
        assert not mock_results.is_displayed(), (
            'Call results should be displayed and are not'
        )

    def test_pf_product_mock_call_with_data_not_logged_in(self):
        self.setup_database(True, True)
        self.client.get('http://localhost:5000/autoscale/')
        details_button = self.client.find_element_by_class_name(
            'toggle-element-1'
        )
        details_button.click()
        time.sleep(1)
        mock_button = self.client.find_element_by_name('test_call-autoscale')
        mock_results = self.client.find_element_by_class_name(
            'code-blocks-wrapper'
        )
        assert not mock_results.is_displayed(), (
            'Call results should not be displayed yet'
        )
        mock_button.click()
        time.sleep(1)
        assert mock_results.is_displayed(), (
            'Call results should be displayed and are not'
        )
        self.assertIn(
            '{ddi}/groups/{test_var_value}',
            mock_results.text,
            'Could not find request URL in mock return'
        )
        self.assertIn(
            '"Content-Type": "application/json"',
            mock_results.text,
            'Could not find request headers content type'
        )

    def test_pf_front_product_manage_nli(self):
        self.client.get('http://localhost:5000/autoscale/manage')
        self.assertIn('Pitchfork', self.client.title)
        self.assertTrue(
            'Login to Application',
            self.client.page_source
        )
        self.assertTrue(
            'Error! Please login to the Application',
            self.client.page_source
        )

    def test_pf_front_product_manage_api_nli(self):
        self.client.get('http://localhost:5000/autoscale/manage/api')
        self.assertIn('Pitchfork', self.client.title)
        self.assertTrue(
            'Login to Application',
            self.client.page_source
        )
        self.assertTrue(
            'Error! Please login to the Application',
            self.client.page_source
        )

    """ Logged in Tests """

    def test_pf_user_front_login(self):
        self.setup_user_logged_in()
        self.assertIn(
            '<a href="/history">',
            self.client.page_source,
            'Could not find my history link after login'
        )
        self.assertIn(
            'Logged in as bob.richards',
            self.client.page_source,
            'Could not find logged in queue in header after login'
        )

    def test_pf_admin_front_login(self):
        self.setup_user_logged_in(True)
        self.assertIn(
            '<a href="/history">',
            self.client.page_source,
            'Could not find my history link after login'
        )
        self.assertIn(
            'Logged in as rusty.shackelford',
            self.client.page_source,
            'Could not find logged in queue in header after login'
        )
        self.assertIn(
            '/admin/settings/general',
            self.client.page_source,
            'Could not find admin menu item after login'
        )

    def test_pf_product_li_interaction_with_calls_mock(self):
        self.setup_user_logged_in()
        self.setup_database(True)
        self.client.get('http://localhost:5000/autoscale/')
        self.client.find_element_by_class_name('prod-popover').click()
        self.assertTrue(
            self.client.find_element_by_class_name(
                'popover-content'
            ).is_displayed(),
            'Link popover was not displayed correctly after click'
        )
        self.client.find_element_by_class_name('prod-popover').click()
        try:
            self.client.find_element_by_class_name('popover-content')
            assert False, (
                'Popover was found and should have been hidden by click'
            )
        except:
            pass

        details = self.client.find_element_by_id('api_call_inner')
        assert not details.is_displayed(), 'Details element should not be seen'
        details_button = self.client.find_element_by_class_name(
            'toggle-element-1'
        )
        details_button.click()
        time.sleep(1)
        self.assertEquals(
            details_button.text,
            'Hide Details',
            'Button text did not change after show'
        )
        assert details.is_displayed(), (
            'Details are not disaplayed as they should have been'
        )
        assert self.client.find_element_by_id(
            'test_call-autoscale_form'
        ).is_displayed(), 'Form not displayed properly'

        mock = self.client.find_element_by_xpath(
            "//form[@id='test_call-autoscale_form']/input[7]"
        )
        mock_results = self.client.find_element_by_class_name(
            'code-blocks-wrapper'
        )
        assert not mock_results.is_displayed(), (
            'Call results should not be displayed yet'
        )
        mock.click()
        time.sleep(1)
        assert mock_results.is_displayed(), (
            'Call results should be displayed and are not'
        )
        self.assertIn(
            'https://{data_center}',
            mock_results.text,
            'Could not find request URL in mock return'
        )
        self.assertIn(
            '"Content-Type": "application/json"',
            mock_results.text,
            'Could not find request headers content type'
        )
        hide_results = self.client.find_element_by_id('toggle_results')
        self.assertIn(
            hide_results.text,
            'Hide Results',
            'Incorrect wording on hide results button'
        )
        hide_results.click()
        time.sleep(1)
        assert not mock_results.is_displayed(), (
            'Call results should be displayed and are not'
        )

    def test_pf_product_li_interaction_with_calls_send_request(self):
        self.setup_user_logged_in()
        self.setup_database(True)
        self.client.get('http://localhost:5000/autoscale/')
        with mock.patch('requests.get') as patched_get:
            type(patched_get.return_value).content = mock.PropertyMock(
                return_value='{"groups_links": [], "groups": []}'
            )
            type(patched_get.return_value).status_code = mock.PropertyMock(
                return_value=200
            )
            type(patched_get.return_value).headers = mock.PropertyMock(
                return_value=(
                    '{"via": "1.1 Repose (Repose/2.12)", "x-response-id":'
                    ' "4a6b8431-5059-4bdd-ba33-ff6ddd6cd892", "transfer-'
                    'encoding": "chunked", "server": "Jetty(8.0.y.z-SNAPSHOT)"'
                    ', "date": "Fri, 26 Sep 2014 15:17:23 GMT", "content-type"'
                    ': "application/json"}'
                )
            )
            details_button = self.client.find_element_by_class_name(
                'toggle-element-1'
            )
            details_button.click()
            dc_select = Select(self.client.find_element_by_id('data_center'))
            dc_select.select_by_visible_text('Select Data Center')
            time.sleep(1)
            send = self.client.find_element_by_xpath(
                "//form[@id='test_call-autoscale_form']/input[6]"
            )
            send_results = self.client.find_element_by_class_name(
                'code-blocks-wrapper'
            )
            assert not send_results.is_displayed(), (
                'Call results should not be displayed yet'
            )
            send.click()
            time.sleep(1)
            self.assertIn(
                'You must provide the following data '
                'before the request can be sent',
                self.client.page_source,
                'Did not find correct error message displayed with no DC'
            )
            error_close = self.client.find_element_by_class_name(
                'bootbox-close-button'
            )
            error_close.click()
            dc_select.select_by_visible_text('DFW')
            send.click()
            time.sleep(1)
            assert send_results.is_displayed(), (
                'Call results should be displayed and are not'
            )
            self.assertIn(
                '123456/groups',
                send_results.text,
                'Could not find formatted request URI in mock return'
            )
            self.assertIn(
                '"Content-Type": "application/json"',
                send_results.text,
                'Could not find request headers content type'
            )
            hide_results = self.client.find_element_by_id('toggle_results')
            self.assertIn(
                hide_results.text,
                'Hide Results',
                'Incorrect wording on hide results button'
            )
            hide_results.click()
            time.sleep(1)
            assert not send_results.is_displayed(), (
                'Call results should be displayed and are not'
            )
            dc_select.select_by_visible_text('ORD')
            self.assertIn(
                'Responses have been cleared as the data '
                'does not apply to the new data center',
                self.client.page_source,
                'Did not DC clearing message as expected'
            )
            send.click()
            time.sleep(1)
            history = self.db.history.find()
            assert history.count() == 2, (
                'Did not find correct number of history items that were logged'
            )

    def test_pf_front_product_manage_li_user(self):
        self.setup_user_logged_in()
        self.client.get('http://localhost:5000/autoscale/manage')
        self.assertIn('Pitchfork', self.client.title)
        self.assertTrue(
            'Error! You do not have the correct '
            'permissions to access this page',
            self.client.page_source
        )

    def test_pf_front_product_manage_api_li_user(self):
        self.setup_user_logged_in()
        self.client.get('http://localhost:5000/autoscale/manage/api')
        self.assertIn('Pitchfork', self.client.title)
        self.assertTrue(
            'Error! You do not have the correct '
            'permissions to access this page',
            self.client.page_source
        )

    def test_pf_front_product_manage_li_admin(self):
        self.setup_user_logged_in(True)
        self.client.get('http://localhost:5000/autoscale/manage')
        self.assertIn(
            '<h4>Current Settings</h4>',
            self.client.page_source,
            'Could not find correct manage title on page'
        )
        self.assertIn(
            'https://{data_center}.autoscale',
            self.client.page_source,
            'Could not find URI for autoscale in manage'
        )

    def test_pf_front_product_manage_api_li_admin(self):
        self.setup_user_logged_in(True)
        self.setup_database()
        self.client.get('http://localhost:5000/autoscale/manage/api')
        self.assertIn(
            'Autoscale - API Calls',
            self.client.page_source,
            'Could not find appropriate title on page'
        )
        self.assertIn(
            'Test Call',
            self.client.page_source,
            'Could not find call title'
        )
        self.assertIn(
            '<span class="fa fa-ban">',
            self.client.page_source,
            'Could not find untested call icon'
        )

    def test_pf_front_generate_report_li_admin(self):
        self.setup_user_logged_in(True)
        self.setup_call_history()
        self.client.get('http://localhost:5000/engine/')
        self.assertIn(
            'Application Reporting',
            self.client.page_source,
            'Could not find appropriate title on page'
        )
        generate = self.client.find_element_by_id('generate_report')
        generate.click()
        time.sleep(1)
        self.assertIn(
            'Query Results - (1)',
            self.client.page_source,
            'Did not find correct results on page'
        )
        history_item = self.db.history.find_one()
        self.assertIn(
            '/engine/view/%s' % str(history_item.get('_id')),
            self.client.page_source,
            'Did not find appropriate link to view details for history'
        )
        work_details = self.client.find_element_by_id('view_work_details')
        assert not work_details.is_displayed(), (
            'Modal is shown for some reason and should not be'
        )
        info = self.client.find_element_by_xpath(
            '/html/body/div[2]/div[3]/div[1]/div[3]/'
            'table/tbody/tr[1]/td[9]/a[1]'
        )
        info.click()
        time.sleep(1)
        assert work_details.is_displayed(), (
            'Details for call should be shown and were not'
        )
        self.assertIn(
            'https://dfw.autoscale.api.rackspace.com/v1/123456/groups',
            self.client.page_source,
            'Could not find request URL in call details'
        )
        close_icon = self.client.find_element_by_class_name('close')
        close_icon.click()
        time.sleep(1)
        assert not work_details.is_displayed(), (
            'Modal is still seend after close was initiated'
        )

    def test_pf_user_login_search(self):
        self.setup_user_logged_in()
        self.setup_database(True)
        self.client.get('/')
        search = self.client.find_element_by_id('search_api')
        search_button = self.client.find_element_by_class_name('search-button')
        search.send_keys('test call')
        search_button.click()
        time.sleep(1)
        self.assertIn(
            'Autoscale - Test Call',
            self.client.page_source,
            'Could not find call after search for it'
        )

        self.client.find_element_by_class_name('prod-popover').click()
        self.assertTrue(
            self.client.find_element_by_class_name(
                'popover-content'
            ).is_displayed(),
            'Link popover was not displayed correctly after click'
        )
        self.client.find_element_by_class_name('prod-popover').click()
        try:
            self.client.find_element_by_class_name('popover-content')
            assert False, (
                'Popover was found and should have been hidden by click'
            )
        except:
            pass

        details = self.client.find_element_by_id('api_call_inner')
        assert not details.is_displayed(), 'Details element should not be seen'
        details_button = self.client.find_element_by_class_name(
            'toggle-element-1'
        )
        details_button.click()
        time.sleep(1)
        self.assertEquals(
            details_button.text,
            'Hide Details',
            'Button text did not change after show'
        )
        assert details.is_displayed(), (
            'Details are not disaplayed as they should have been'
        )
        assert self.client.find_element_by_id(
            'test_call-autoscale_form'
        ).is_displayed(), 'Form not displayed properly'

        mock = self.client.find_element_by_xpath(
            "//form[@id='test_call-autoscale_form']/input[7]"
        )
        mock_results = self.client.find_element_by_class_name(
            'code-blocks-wrapper'
        )
        assert not mock_results.is_displayed(), (
            'Call results should not be displayed yet'
        )
        mock.click()
        time.sleep(1)
        assert mock_results.is_displayed(), (
            'Call results should be displayed and are not'
        )
        self.assertIn(
            'https://{data_center}',
            mock_results.text,
            'Could not find request URL in mock return'
        )
        self.assertIn(
            '"Content-Type": "application/json"',
            mock_results.text,
            'Could not find request headers content type'
        )
        hide_results = self.client.find_element_by_id('toggle_results')
        self.assertIn(
            hide_results.text,
            'Hide Results',
            'Incorrect wording on hide results button'
        )
        hide_results.click()
        time.sleep(1)
        assert not mock_results.is_displayed(), (
            'Call results should be displayed and are not'
        )

if __name__ == "__main__":
    unittest.main()
