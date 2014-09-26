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

from flask import g, current_app


def check_and_initialize():
    settings = g.db.settings.find_one()
    forms = g.db.forms.find_one()
    reporting = g.db.reporting.find_one()
    api_settings = g.db.api_settings.find_one()
    if settings is None:
        current_app.logger.debug('Settings are empty...initializing')
        g.db.settings.insert(
            {
                'application_title': current_app.config.get(
                    'APP_NAME', 'Pitchfork'
                ),
                'application_email': current_app.config.get('APP_EMAIL'),
                'application_well': (
                    '<p class="lead">Rackspace Cloud - API Interactive Website'
                    ' Application</p><div class="center">'
                    'For improvements or suggestions please go to GitHub and '
                    'submit an <a href="https://github.com/rackerlabs/'
                    'pitchfork/issues/new" class="tooltip-title" '
                    'target="_blank" title="Submit a GitHub issue">issue</a>'
                    '</div><div id="issue_feedback" class="center"></div>'
                ),
                'application_footer': (
                    'This site is not officially supported by Rackspace. '
                    'Source is available on <a href="https://github.com/'
                    'rackerlabs/pitchfork/" class="tooltip-title" '
                    'target="_blank" title="Pitchfork Repository">github</a>'
                ),
                'administrators': [
                    {
                        'admin': current_app.config.get(
                            'ADMIN', 'oldarmyc'
                        ),
                        'admin_name': current_app.config.get(
                            'ADMIN_NAME', 'Dave Kludt'
                        )
                    }
                ],
                'menu': [
                    {
                        'url': '/history',
                        'display_name': 'My History',
                        'name': 'my_history',
                        'parent': '',
                        'active': True,
                        'parent_order': 1,
                        'order': 1,
                        'view_permissions': 'logged_in'
                    }, {
                        'url': '/autoscale',
                        'display_name': 'Autoscale',
                        'name': 'autoscale',
                        'parent': 'cloud_products',
                        'active': True,
                        'parent_order': 2,
                        'order': 1,
                        'view_permissions': 'all'
                    }, {
                        'url': '/cloud_backup',
                        'display_name': 'Backup',
                        'name': 'backup',
                        'parent': 'cloud_products',
                        'active': True,
                        'parent_order': 2,
                        'order': 2,
                        'view_permissions': 'all'
                    }, {
                        'url': '/big_data',
                        'display_name': 'Big Data',
                        'name': 'big_data',
                        'parent': 'cloud_products',
                        'active': True,
                        'parent_order': 2,
                        'order': 3,
                        'view_permissions': 'all'
                    }, {
                        'url': '/block_storage',
                        'display_name': 'Block Storage',
                        'name': 'block_storage',
                        'parent': 'cloud_products',
                        'active': True,
                        'parent_order': 2,
                        'order': 4,
                        'view_permissions': 'all'
                    }, {
                        'url': '/databases',
                        'display_name': 'Databases',
                        'name': 'databases',
                        'parent': 'cloud_products',
                        'active': True,
                        'parent_order': 2,
                        'order': 5,
                        'view_permissions': 'all'
                    }, {
                        'url': '/dns',
                        'display_name': 'DNS',
                        'name': 'dns',
                        'parent': 'cloud_products',
                        'active': True,
                        'parent_order': 2,
                        'order': 6,
                        'view_permissions': 'all'
                    }, {
                        'url': '/cloud_feeds',
                        'display_name': 'Feeds',
                        'name': 'cloud_feeds',
                        'parent': 'cloud_products',
                        'active': True,
                        'parent_order': 2,
                        'order': 7,
                        'view_permissions': 'all'
                    }, {
                        'url': '/fg_servers',
                        'display_name': 'First Gen Servers',
                        'name': 'first_gen_servers',
                        'parent': 'cloud_products',
                        'active': True,
                        'parent_order': 2,
                        'order': 8,
                        'view_permissions': 'all'
                    }, {
                        'url': '/identity',
                        'display_name': 'Identity',
                        'name': 'identity',
                        'parent': 'cloud_products',
                        'active': True,
                        'parent_order': 2,
                        'order': 9,
                        'view_permissions': 'all'
                    }, {
                        'url': '/images',
                        'display_name': 'Images',
                        'name': 'images',
                        'parent': 'cloud_products',
                        'active': True,
                        'parent_order': 2,
                        'order': 10,
                        'view_permissions': 'all'
                    }, {
                        'url': '/load_balancers',
                        'display_name': 'Load Balancers',
                        'name': 'load_balancers',
                        'parent': 'cloud_products',
                        'active': True,
                        'parent_order': 2,
                        'order': 11,
                        'view_permissions': 'all'
                    }, {
                        'url': '/monitoring',
                        'display_name': 'Monitoring',
                        'name': 'monitoring',
                        'parent': 'cloud_products',
                        'active': True,
                        'parent_order': 2,
                        'order': 12,
                        'view_permissions': 'all'
                    }, {
                        'url': '/networks',
                        'display_name': 'Networks',
                        'name': 'networks',
                        'parent': 'cloud_products',
                        'active': True,
                        'parent_order': 2,
                        'order': 13,
                        'view_permissions': 'all'
                    }, {
                        'url': '/ng_servers',
                        'display_name': 'Next Gen Servers',
                        'name': 'next_gen_servers',
                        'parent': 'cloud_products',
                        'active': True,
                        'parent_order': 2,
                        'order': 14,
                        'view_permissions': 'all'
                    }, {
                        'url': '/orchestration',
                        'display_name': 'Orchestration',
                        'name': 'orchestration',
                        'parent': 'cloud_products',
                        'active': True,
                        'parent_order': 2,
                        'order': 15,
                        'view_permissions': 'all'
                    }, {
                        'url': '/queues',
                        'display_name': 'Queues',
                        'name': 'queues',
                        'parent': 'cloud_products',
                        'active': True,
                        'parent_order': 2,
                        'order': 16,
                        'view_permissions': 'all'
                    }, {
                        'url': '/autoscale/manage',
                        'display_name': 'Autoscale',
                        'name': 'autoscale_manage',
                        'parent': 'manage_products',
                        'active': True,
                        'parent_order': 3,
                        'order': 1,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/cloud_backup/manage',
                        'display_name': 'Backup',
                        'name': 'backup_setup',
                        'parent': 'manage_products',
                        'active': True,
                        'parent_order': 3,
                        'order': 2,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/big_data/manage',
                        'display_name': 'Big Data',
                        'name': 'big_data_setup',
                        'parent': 'manage_products',
                        'active': True,
                        'parent_order': 3,
                        'order': 3,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/block_storage/manage',
                        'display_name': 'Block Storage',
                        'name': 'block_storage_setup',
                        'parent': 'manage_products',
                        'active': True,
                        'parent_order': 3,
                        'order': 4,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/databases/manage',
                        'display_name': 'Databases',
                        'name': 'databases_setup',
                        'parent': 'manage_products',
                        'active': True,
                        'parent_order': 3,
                        'order': 5,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/dns/manage',
                        'display_name': 'DNS',
                        'name': 'dns_setup',
                        'parent': 'manage_products',
                        'active': True,
                        'parent_order': 3,
                        'order': 6,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/cloud_feeds/manage',
                        'display_name': 'Feeds',
                        'name': 'manage_feeds',
                        'parent': 'manage_products',
                        'active': True,
                        'parent_order': 3,
                        'order': 7,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/fg_servers/manage',
                        'display_name': 'FG Servers',
                        'name': 'fg_servers_setup',
                        'parent': 'manage_products',
                        'active': True,
                        'parent_order': 3,
                        'order': 8,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/identity/manage',
                        'display_name': 'Identity',
                        'name': 'identity_setup',
                        'parent': 'manage_products',
                        'active': True,
                        'parent_order': 3,
                        'order': 9,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/images/manage',
                        'display_name': 'Images',
                        'name': 'images_manage',
                        'parent': 'manage_products',
                        'active': True,
                        'parent_order': 3,
                        'order': 10,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/load_balancers/manage',
                        'display_name': 'Load Balancers',
                        'name': 'lb_setup',
                        'parent': 'manage_products',
                        'active': True,
                        'parent_order': 3,
                        'order': 11,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/monitoring/manage',
                        'display_name': 'Monitoring',
                        'name': 'monitoring_manage',
                        'parent': 'manage_products',
                        'active': True,
                        'parent_order': 3,
                        'order': 12,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/networks/manage',
                        'display_name': 'Networks',
                        'name': 'networks_setup',
                        'parent': 'manage_products',
                        'active': True,
                        'parent_order': 3,
                        'order': 13,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/ng_servers/manage',
                        'display_name': 'NG Servers',
                        'name': 'ng_server_setup',
                        'parent': 'manage_products',
                        'active': True,
                        'parent_order': 3,
                        'order': 14,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/orchestration/manage',
                        'display_name': 'Orchestration',
                        'name': 'orchestration_manage',
                        'parent': 'manage_products',
                        'active': True,
                        'parent_order': 3,
                        'order': 15,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/queues/manage',
                        'display_name': 'Queues',
                        'name': 'queues_manage',
                        'parent': 'manage_products',
                        'active': True,
                        'parent_order': 3,
                        'order': 16,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/autoscale/manage/api',
                        'display_name': 'Autoscale',
                        'name': 'autoscale_api',
                        'parent': 'api_settings',
                        'active': True,
                        'parent_order': 4,
                        'order': 1,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/cloud_backup/manage/api',
                        'display_name': 'Backup',
                        'name': 'backup_api',
                        'parent': 'api_settings',
                        'active': True,
                        'parent_order': 4,
                        'order': 2,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/big_data/manage/api',
                        'display_name': 'Big Data',
                        'name': 'big_data_api',
                        'parent': 'api_settings',
                        'active': True,
                        'parent_order': 4,
                        'order': 3,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/block_storage/manage/api',
                        'display_name': 'Block Storage',
                        'name': 'block_storage_api',
                        'parent': 'api_settings',
                        'active': True,
                        'parent_order': 4,
                        'order': 4,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/databases/manage/api',
                        'display_name': 'Databases',
                        'name': 'databases_api',
                        'parent': 'api_settings',
                        'active': True,
                        'parent_order': 4,
                        'order': 5,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/dns/manage/api',
                        'display_name': 'DNS',
                        'name': 'dns_api',
                        'parent': 'api_settings',
                        'active': True,
                        'parent_order': 4,
                        'order': 6,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/cloud_feeds/manage/api',
                        'display_name': 'Feeds',
                        'name': 'feeds_api',
                        'parent': 'api_settings',
                        'active': True,
                        'parent_order': 4,
                        'order': 7,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/fg_servers/manage/api',
                        'display_name': 'FG Servers',
                        'name': 'fg_servers_api',
                        'parent': 'api_settings',
                        'active': True,
                        'parent_order': 4,
                        'order': 8,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/identity/manage/api',
                        'display_name': 'Identity',
                        'name': 'identity_api',
                        'parent': 'api_settings',
                        'active': True,
                        'parent_order': 4,
                        'order': 9,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/images/manage/api',
                        'display_name': 'Images',
                        'name': 'images_api',
                        'parent': 'api_settings',
                        'active': True,
                        'parent_order': 4,
                        'order': 10,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/load_balancers/manage/api',
                        'display_name': 'Load Balancers',
                        'name': 'load_balancers_api',
                        'parent': 'api_settings',
                        'active': True,
                        'parent_order': 4,
                        'order': 11,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/monitoring/manage/api',
                        'display_name': 'Monitoring',
                        'name': 'monitoring_api',
                        'parent': 'api_settings',
                        'active': True,
                        'parent_order': 4,
                        'order': 12,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/networks/manage/api',
                        'display_name': 'Networks',
                        'name': 'networks_api',
                        'parent': 'api_settings',
                        'active': True,
                        'parent_order': 4,
                        'order': 13,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/ng_servers/manage/api',
                        'display_name': 'NG Servers',
                        'name': 'ng_servers_api',
                        'parent': 'api_settings',
                        'active': True,
                        'parent_order': 4,
                        'order': 14,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/orchestration/manage/api',
                        'display_name': 'Orchestration',
                        'name': 'orchestration_api',
                        'parent': 'api_settings',
                        'active': True,
                        'parent_order': 4,
                        'order': 15,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/queues/manage/api',
                        'display_name': 'Queues',
                        'name': 'queues_api',
                        'parent': 'api_settings',
                        'active': True,
                        'parent_order': 4,
                        'order': 16,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Generate Report',
                        'name': 'engine',
                        'parent': '',
                        'url': '/engine/',
                        'parent_order': 5,
                        'divider': False,
                        'order': 3,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/admin/settings/admins',
                        'display_name': 'Manage Admins',
                        'name': 'manage_admins',
                        'parent': 'system',
                        'active': True,
                        'parent_order': 6,
                        'order': 1,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Manage Engine',
                        'divider': True,
                        'name': 'engine_setup',
                        'order': 2,
                        'parent': 'system',
                        'parent_order': 6,
                        'url': '/engine/setup',
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/manage/dcs',
                        'display_name': 'Data Centers',
                        'name': 'manage_dcs',
                        'parent': 'system',
                        'active': True,
                        'parent_order': 6,
                        'order': 3,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/manage/verbs',
                        'display_name': 'API Verbs',
                        'name': 'manage_verbs',
                        'parent': 'system',
                        'active': True,
                        'parent_order': 6,
                        'order': 4,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/admin/settings/general',
                        'display_name': 'General Settings',
                        'name': 'general_settings',
                        'parent': 'administrators',
                        'active': True,
                        'parent_order': 7,
                        'order': 1,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/admin/settings/menu',
                        'display_name': 'Menu Settings',
                        'name': 'menu_settings',
                        'parent': 'administrators',
                        'active': True,
                        'parent_order': 7,
                        'order': 2,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/admin/settings/roles',
                        'display_name': 'Manage Roles',
                        'name': 'manage_roles',
                        'parent': 'administrators',
                        'active': True,
                        'parent_order': 7,
                        'order': 3,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Manage Forms',
                        'name': 'manage_forms',
                        'parent': 'administrators',
                        'url': '/admin/forms',
                        'parent_order': 7,
                        'order': 4,
                        'view_permissions': 'administrators'
                    }
                ],
                'reporting': {
                    'enabled': True,
                    'description': (
                        'History of all calls submitted on the '
                        'site since launch'
                    ),
                    'collection': 'history'
                },
                'top_level_menu': [
                    {
                        'order': 1,
                        'slug': 'my_history',
                        'name': 'My History'
                    }, {
                        'order': 2,
                        'slug': 'cloud_products',
                        'name': 'Cloud Products'
                    }, {
                        'order': 3,
                        'slug': 'manage_products',
                        'name': 'Manage Products'
                    }, {
                        'order': 4,
                        'slug': 'api_settings',
                        'name': 'API Settings'
                    }, {
                        'order': 5,
                        'name': 'Generate Report',
                        'slug': 'generate_report'
                    }, {
                        'order': 6,
                        'name': 'System',
                        'slug': 'system'
                    }, {
                        'order': 7,
                        'name': 'Administrators',
                        'slug': 'administrators'
                    }
                ],
                'roles': [
                    {
                        'active': True,
                        'display_name': 'Administrators',
                        'name': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Logged In',
                        'name': 'logged_in',
                        'perms': [
                            '/',
                            '/history',
                            '/search',
                            '/<product>/',
                            '/<product>/api/call/process',
                            '/admin/logout/'
                        ]
                    }, {
                        'active': True,
                        'display_name': 'All',
                        'name': 'all',
                        'perms': [
                            '/',
                            '/search',
                            '/<product>/',
                            '/<product>/api/call/process',
                            '/admin/login'
                        ]
                    },
                ]
            }
        )
        settings = g.db.settings.find_one({}, {'_id': 0})

    if api_settings is None:
        g.db.api_settings.insert(
            {
                'active_products': [
                    'autoscale',
                    'cloud_backup',
                    'big_data',
                    'block_storage',
                    'databases',
                    'dns',
                    'cloud_feeds',
                    'fg_servers',
                    'identity',
                    'images',
                    'load_balancers',
                    'monitoring',
                    'ng_servers',
                    'networks',
                    'orchestration',
                    'queues'
                ],
                'autoscale': {
                    'app_url': '/autoscale',
                    'title': 'Autoscale',
                    'db_name': 'autoscale',
                    'require_dc': True,
                    'us_api': (
                        'https://{data_center}.autoscale.api.'
                        'rackspacecloud.com/v1.0/'
                    ),
                    'uk_api': (
                        'https://{data_center}.autoscale.api.'
                        'rackspacecloud.com/v1.0/'
                    ),
                    'active': True,
                    'doc_url': (
                        'http://docs.rackspace.com/cas/api/v1.0/'
                        'autoscale-devguide/content/Overview.html'
                    )
                },
                'big_data': {
                    'app_url': '/big_data',
                    'title': 'Big Data',
                    'db_name': 'big_data',
                    'require_dc': True,
                    'us_api': (
                        'https://{data_center}.bigdata.api.'
                        'rackspacecloud.com/v1.0/{ddi}'
                    ),
                    'uk_api': (
                        'https://{data_center}.bigdata.api.'
                        'rackspacecloud.com/v1.0/{ddi}'
                    ),
                    'active': True,
                    'doc_url': (
                        'http://docs.rackspace.com/cbd/api/v1.0/'
                        'cbd-devguide/content/overview.html'
                    )
                },
                'block_storage': {
                    'app_url': '/block_storage',
                    'title': 'Block Storage',
                    'db_name': 'cbs',
                    'require_dc': True,
                    'us_api': (
                        'https://{data_center}.blockstorage.api.'
                        'rackspacecloud.com/v1/{ddi}'
                    ),
                    'uk_api': (
                        'https://{data_center}.blockstorage.api.'
                        'rackspacecloud.com/v1/{ddi}'
                    ),
                    'active': True,
                    'doc_url': (
                        'http://docs.rackspace.com/cbs/api/'
                        'v1.0/cbs-devguide/content/overview.html'
                    )
                },
                'cloud_backup': {
                    'app_url': '/cloud_backup',
                    'title': 'Backup',
                    'db_name': 'cloud_backup',
                    'require_dc': True,
                    'us_api': (
                        'https://{data_center}.backup.api.'
                        'rackspacecloud.com/v1.0/{ddi}'
                    ),
                    'uk_api': (
                        'https://{data_center}.backup.api.'
                        'rackspacecloud.com/v1.0/{ddi}'
                    ),
                    'active': True,
                    'doc_url': (
                        'http://docs.rackspace.com/rcbu/api/v1.0/'
                        'rcbu-devguide/content/overview.html'
                    )
                },
                'databases': {
                    'app_url': '/databases',
                    'title': 'Databases',
                    'db_name': 'cloud_db',
                    'require_dc': True,
                    'us_api': (
                        'https://{data_center}.databases.api.'
                        'rackspacecloud.com/v1.0/{ddi}'
                    ),
                    'uk_api': (
                        'https://{data_center}.databases.api.'
                        'rackspacecloud.com/v1.0/{ddi}'
                    ),
                    'active': True,
                    'doc_url': (
                        'http://docs.rackspace.com/cdb/api/'
                        'v1.0/cdb-devguide/content/overview.html'
                    )
                },
                'dns': {
                    'app_url': '/dns',
                    'title': 'DNS',
                    'db_name': 'cloud_dns',
                    'require_dc': True,
                    'us_api': (
                        'https://dns.api.rackspacecloud.com/v1.0/{ddi}'
                    ),
                    'uk_api': (
                        'https://lon.dns.api.rackspacecloud.com/v1.0/{ddi}'
                    ),
                    'active': True,
                    'doc_url': (
                        'http://docs.rackspace.com/cdns/api/'
                        'v1.0/cdns-devguide/content/overview.html'
                    )
                },
                'identity': {
                    'app_url': '/identity',
                    'title': 'Identity',
                    'db_name': 'cloud_identity',
                    'require_dc': True,
                    'us_api': (
                        'https://identity.api.rackspacecloud.com/v2.0'
                    ),
                    'uk_api': (
                        'https://lon.identity.api.rackspacecloud.com/v2.0'
                    ),
                    'active': True,
                    'doc_url': (
                        'http://docs.rackspace.com/auth/api/v2.0/'
                        'auth-client-devguide/content/Overview-d1e65.html'
                    )
                },
                'cloud_feeds': {
                    'app_url': '/cloud_feeds',
                    'title': 'Cloud Feeds',
                    'db_name': 'cloud_feeds',
                    'require_dc': True,
                    'us_api': (
                        'https://{data_center}.feeds.api.rackspacecloud.com'
                    ),
                    'uk_api': (
                        'https://{data_center}.feeds.api.rackspacecloud.com'
                    ),
                    'active': True,
                    'doc_url': (
                        'http://docs.rackspace.com/cloud-feeds/api/'
                        'v1.0/feeds-devguide/content/overview.html'
                    )
                },
                'networks': {
                    'app_url': '/networks',
                    'title': 'Networks',
                    'db_name': 'cloud_networks',
                    'require_dc': True,
                    'us_api': (
                        'https://{data_center}.servers.api.'
                        'rackspacecloud.com/v2/{ddi}'
                    ),
                    'uk_api': (
                        'https://{data_center}.servers.api.'
                        'rackspacecloud.com/v2/{ddi}'
                    ),
                    'active': True,
                    'doc_url': (
                        'http://docs.rackspace.com/networks/api/'
                        'v2/cn-devguide/content/ch_preface.html'
                    )
                },
                'fg_servers': {
                    'app_url': '/fg_servers',
                    'title': 'First Gen Servers',
                    'db_name': 'fg_servers',
                    'require_dc': True,
                    'us_api': (
                        'https://servers.api.rackspacecloud.com/v1.0/{ddi}'
                    ),
                    'uk_api': (
                        'https://lon.servers.api.rackspacecloud.com/v1.0/{ddi}'
                    ),
                    'active': True,
                    'doc_url': (
                        'http://docs.rackspace.com/servers/api/v1.0/'
                        'cs-devguide/content/Overview-d1e70.html'
                    )
                },
                'images': {
                    'app_url': '/images',
                    'title': 'Images',
                    'db_name': 'images',
                    'require_dc': True,
                    'us_api': (
                        'https://{data_center}.images.api.'
                        'rackspacecloud.com/v2/{ddi}'
                    ),
                    'uk_api': (
                        'https://{data_center}.images.api.'
                        'rackspacecloud.com/v2/{ddi}'
                    ),
                    'active': True,
                    'doc_url': (
                        'http://docs.rackspace.com/images/api/v2/ci-'
                        'devguide/content/ch_image-service-dev-overview.html'
                    )
                },
                'load_balancers': {
                    'app_url': '/load_balancers',
                    'title': 'Load Balancers',
                    'db_name': 'load_balancers',
                    'require_dc': True,
                    'us_api': (
                        'https://{data_center}.loadbalancers.api.'
                        'rackspacecloud.com/v1.0/{ddi}'
                    ),
                    'uk_api': (
                        'https://{data_center}.loadbalancers.api.'
                        'rackspacecloud.com/v1.0/{ddi}'
                    ),
                    'active': True,
                    'doc_url': (
                        'http://docs.rackspace.com/loadbalancers/api/'
                        'v1.0/clb-devguide/content/Overview-d1e82.html'
                    )
                },
                'monitoring': {
                    'app_url': '/monitoring',
                    'title': 'Monitoring',
                    'db_name': 'monitoring',
                    'us_api': (
                        'https://monitoring.api.rackspacecloud.com/v1.0/{ddi}'
                    ),
                    'uk_api': (
                        'https://monitoring.api.rackspacecloud.com/v1.0/{ddi}'
                    ),
                    'active': True,
                    'doc_url': (
                        'http://docs.rackspace.com/cm/api/v1.0/'
                        'cm-devguide/content/overview.html'
                    )
                },
                'ng_servers': {
                    'app_url': '/ng_servers',
                    'title': 'Next Gen Servers',
                    'db_name': 'ng_servers',
                    'require_dc': True,
                    'us_api': (
                        'https://{data_center}.servers.api.'
                        'rackspacecloud.com/v2/{ddi}'
                    ),
                    'uk_api': (
                        'https://{data_center}.servers.api.'
                        'rackspacecloud.com/v2/{ddi}'
                    ),
                    'active': True,
                    'doc_url': (
                        'http://docs.rackspace.com/servers/api/v2/'
                        'cs-devguide/content/ch_preface.html'
                    )
                },
                'orchestration': {
                    'app_url': '/orchestration',
                    'title': 'Orchestration',
                    'db_name': 'orchestration',
                    'require_dc': True,
                    'us_api': (
                        'https://{data_center}.orchestration.api.'
                        'rackspacecloud.com/v1/{ddi}'
                    ),
                    'uk_api': (
                        'https://{data_center}.orchestration.api.'
                        'rackspacecloud.com/v1/{ddi}'
                    ),
                    'active': True,
                    'doc_url': (
                        'http://docs.rackspace.com/orchestration/'
                        'api/v1/orchestration-devguide/content/overview.html'
                    )
                },
                'queues': {
                    'app_url': '/queues',
                    'title': 'Queues',
                    'db_name': 'queues',
                    'require_dc': True,
                    'us_api': (
                        'https://{data_center}.queues.api.'
                        'rackspacecloud.com/v1'
                    ),
                    'uk_api': (
                        'https://{data_center}.queues.api.'
                        'rackspacecloud.com/v1'
                    ),
                    'active': True,
                    'doc_url': (
                        'http://docs.rackspace.com/queues/api/v1.0/'
                        'cq-devguide/content/overview.html'
                    )
                },
                'dcs': [
                    {
                        'abbreviation': 'DFW',
                        'name': 'Dallas'
                    }, {
                        'abbreviation': 'ORD',
                        'name': 'Chicago'
                    }, {
                        'abbreviation': 'IAD',
                        'name': 'Virginia'
                    }, {
                        'abbreviation': 'SYD',
                        'name': 'Sydney'
                    }, {
                        'abbreviation': 'LON',
                        'name': 'London'
                    }, {
                        'abbreviation': 'HKG',
                        'name': 'Hong Kong'
                    }
                ],
                'verbs': [
                    {
                        'active': True,
                        'name': 'GET'
                    }, {
                        'active': True,
                        'name': 'PUT'
                    }, {
                        'active': True,
                        'name': 'POST'
                    }, {
                        'active': True,
                        'name': 'HEAD'
                    }, {
                        'active': True,
                        'name': 'DELETE'
                    }, {
                        'active': True,
                        'name': 'PATCH'
                    }
                ]
            }
        )

    if forms is None:
        g.db.forms.insert(
            {
                'active': True,
                'display_name': 'Login Form',
                'fields': [
                    {
                        'active': True,
                        'default': False,
                        'default_value': '',
                        'field_choices': '',
                        'field_type': 'TextField',
                        'label': 'Username:',
                        'name': 'username',
                        'order': 1,
                        'required': True
                    }, {
                        'default_value': '',
                        'field_type': 'PasswordField',
                        'field_choices': '',
                        'name': 'password',
                        'default': False,
                        'required': True,
                        'active': True,
                        'order': 2,
                        'label': 'API Key or Password:'
                    }, {
                        'default_value': '',
                        'field_type': 'SubmitField',
                        'field_choices': '',
                        'name': 'submit',
                        'default': False,
                        'required': False,
                        'active': True,
                        'order': 3,
                        'label': 'Submit'
                    }
                ],
                'name': 'login_form',
                'submission_url': '/admin/login',
                'system_form': True
            }
        )
        g.db.forms.insert(
            {
                'active': True,
                'display_name': 'Manage Administrators',
                'fields': [
                    {
                        'default_value': '',
                        'field_type': 'TextField',
                        'field_choices': '',
                        'name': 'administrator',
                        'default': False,
                        'required': True,
                        'active': True,
                        'order': 1,
                        'label': 'Username:'
                    }, {
                        'default_value': '',
                        'field_type': 'TextField',
                        'field_choices': '',
                        'name': 'full_name',
                        'default': False,
                        'required': True,
                        'active': True,
                        'order': 2,
                        'label': 'Full Name:'
                    }, {
                        'default_value': '',
                        'field_type': 'SubmitField',
                        'field_choices': '',
                        'name': 'admin',
                        'default': False,
                        'required': False,
                        'active': True,
                        'order': 3,
                        'label': 'Add Admin'
                    }
                ],
                'name': 'add_administrator',
                'submission_url': '/admin/settings/admins',
                'system_form': True
            }
        )
        g.db.forms.insert(
            {
                'active': True,
                'display_name': 'Manage Roles',
                'fields': [
                    {
                        'default_value': '',
                        'field_type': 'TextField',
                        'field_choices': '',
                        'name': 'display_name',
                        'default': False,
                        'required': True,
                        'active': True,
                        'order': 1,
                        'label': 'Name:'
                    }, {
                        'default_value': '',
                        'field_type': 'BooleanField',
                        'field_choices': '',
                        'name': 'status',
                        'default': False,
                        'required': False,
                        'active': True,
                        'order': 2,
                        'label': 'Active?:'
                    }, {
                        'default_value': '',
                        'field_type': 'SubmitField',
                        'field_choices': '',
                        'name': 'submit',
                        'default': False,
                        'required': False,
                        'active': True,
                        'order': 3,
                        'label': 'Submit'
                    }
                ],
                'name': 'manage_roles',
                'submission_url': '/admin/settings/roles',
                'system_form': True
            }
        )
        g.db.forms.insert(
            {
                'active': True,
                'display_name': 'Suggestions',
                'fields': [
                    {
                        'default_value': '',
                        'field_type': 'TextField',
                        'field_choices': '',
                        'name': 'suggestion',
                        'default': False,
                        'required': False,
                        'active': True,
                        'order': 1,
                        'label': 'Suggestion:'
                    }, {
                        'default_value': '',
                        'field_type': 'SubmitField',
                        'field_choices': '',
                        'name': 'submit',
                        'default': False,
                        'required': False,
                        'active': True,
                        'order': 2,
                        'label': 'Send'
                    }
                ],
                'name': 'suggestion_form',
                'submission_url': '/admin/submit_feedback',
                'system_form': True
            }
        )
        g.db.forms.insert(
            {
                'active': True,
                'display_name': 'General Settings',
                'fields': [
                    {
                        'active': True,
                        'default': False,
                        'default_value': '',
                        'field_choices': '',
                        'field_type': 'TextField',
                        'label': 'Application Title:',
                        'name': 'application_title',
                        'order': 1,
                        'required': False,
                        'style_id': ''
                    }, {
                        'active': True,
                        'default': False,
                        'default_value': '',
                        'field_choices': '',
                        'field_type': 'TextField',
                        'label': 'Application Email:',
                        'name': 'application_email',
                        'order': 2,
                        'required': False,
                        'style_id': ''
                    }, {
                        'active': True,
                        'default': False,
                        'default_value': '',
                        'field_choices': '',
                        'field_type': 'TextAreaField',
                        'label': 'Application Intro:',
                        'name': 'application_well',
                        'order': 3,
                        'required': False,
                        'style_id': ''
                    }, {
                        'default_value': '',
                        'field_type': 'TextAreaField',
                        'field_choices': '',
                        'name': 'application_footer',
                        'default': False,
                        'style_id': '',
                        'required': False,
                        'active': True,
                        'order': 4,
                        'label': 'Application Footer:'
                    }, {
                        'default_value': '',
                        'field_type': 'SubmitField',
                        'field_choices': '',
                        'name': 'settings',
                        'default': False,
                        'style_id': '',
                        'required': False,
                        'active': True,
                        'order': 5,
                        'label': 'Apply Settings'
                    }
                ],
                'name': 'application_settings',
                'submission_url': '/admin/settings/general',
                'system_form': True
            }
        )
        g.db.forms.insert(
            {
                'active': True,
                'display_name': 'Menu Items',
                'fields': [
                    {
                        'active': True,
                        'default': False,
                        'default_value': '',
                        'field_choices': '',
                        'field_type': 'SelectField',
                        'label': 'Parent Menu:',
                        'name': 'parent_menu',
                        'order': 1,
                        'required': False,
                        'style_id': ''
                    }, {
                        'active': True,
                        'default': False,
                        'default_value': '',
                        'field_choices': '',
                        'field_type': 'TextField',
                        'label': 'New Parent:',
                        'name': 'new_parent',
                        'order': 2,
                        'required': False,
                        'style_id': ''
                    }, {
                        'default_value': '',
                        'field_type': 'TextField',
                        'field_choices': '',
                        'name': 'db_name',
                        'default': False,
                        'style_id': '',
                        'required': True,
                        'active': True,
                        'order': 3,
                        'label': 'DB Name:'
                    }, {
                        'default_value': '',
                        'field_type': 'TextField',
                        'field_choices': '',
                        'name': 'menu_display_name',
                        'default': False,
                        'style_id': '',
                        'required': True,
                        'active': True,
                        'order': 4,
                        'label': 'Display Name:'
                    }, {
                        'default_value': '',
                        'field_type': 'TextField',
                        'field_choices': '',
                        'name': 'menu_item_url',
                        'default': False,
                        'style_id': '',
                        'required': True,
                        'active': True,
                        'order': 5,
                        'label': 'URL:'
                    }, {
                        'default_value': '',
                        'field_type': 'SelectField',
                        'field_choices': '',
                        'name': 'menu_permissions',
                        'default': False,
                        'style_id': '',
                        'required': True,
                        'active': True,
                        'order': 6,
                        'label': 'Permissions:'
                    }, {
                        'default_value': '',
                        'field_type': 'BooleanField',
                        'field_choices': '',
                        'name': 'menu_item_status',
                        'default': False,
                        'style_id': '',
                        'required': False,
                        'active': True,
                        'order': 7,
                        'label': 'Active?:'
                    }, {
                        'default_value': '',
                        'field_type': 'BooleanField',
                        'field_choices': '',
                        'name': 'menu_item_divider',
                        'default': False,
                        'style_id': '',
                        'required': False,
                        'active': True,
                        'order': 8,
                        'label': 'Add Divider?:'
                    }, {
                        'default_value': '',
                        'field_type': 'SubmitField',
                        'field_choices': '',
                        'name': 'menu',
                        'default': False,
                        'style_id': '',
                        'required': False,
                        'active': True,
                        'order': 9,
                        'label': 'Submit'
                    }
                ],
                'name': 'menu_items_form',
                'submission_url': '/admin/settings/menu',
                'system_form': True
            }
        )

    if reporting is None:
        g.db.reporting.insert(
            {
                'data_type': 'text',
                'description': 'Full name of user who ran call ',
                'field_display': 'TextField',
                'field_display_data': '',
                'field_display_label': '',
                'field_name': 'name',
                'graphable': False,
                'searchable': True
            }
        )
        g.db.reporting.insert(
            {
                'data_type': 'text',
                'description': 'Account Number used to make call ',
                'field_display': 'TextField',
                'field_display_data': '',
                'field_display_label': 'DDI',
                'field_name': 'ddi',
                'graphable': False,
                'searchable': True
            }
        )
        g.db.reporting.insert(
            {
                'data_type': 'text',
                'description': 'Data Center where call was made',
                'field_display': 'SelectField',
                'field_display_data': '',
                'field_display_label': '',
                'field_name': 'data_center',
                'graphable': True,
                'searchable': True
            }
        )
        g.db.reporting.insert(
            {
                'data_type': 'text',
                'description': 'Verb used for generating call',
                'field_display': 'SelectField',
                'field_display_data': '',
                'field_display_label': 'Verb',
                'field_name': 'request.verb',
                'graphable': True,
                'searchable': True
            }
        )
        g.db.reporting.insert(
            {
                'data_type': 'text',
                'description': 'Product call was generated for',
                'field_display': 'SelectField',
                'field_display_data': '',
                'field_display_label': '',
                'field_name': 'product',
                'graphable': False,
                'searchable': True
            }
        )
        g.db.reporting.insert(
            {
                'data_type': 'datetime',
                'field_display_label': '',
                'description': 'Timestamp when call was executed',
                'searchable': True,
                'field_display_data': '',
                'field_name': 'completed_at',
                'field_display': 'TextField',
                'graphable': False
            }
        )

    return settings
