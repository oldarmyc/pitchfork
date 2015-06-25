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

from flask.ext.cloudadmin.defaults import check_and_initialize
from config import config


def application_initialize(db, app):
    settings = db.settings.find_one()
    reporting = db.reporting.find_one()
    api_settings = db.api_settings.find_one()
    if settings is None:
        # Initialize admin first then setup application
        settings = check_and_initialize(app, db)

    if settings.get('application_set') is None:
        app.logger.debug(
            'Application settings are empty...initializing'
        )
        db.settings.update(
            {},
            {
                '$set': {
                    'app_title': 'Pitchfork',
                    'app_well': (
                        '<p class="lead">Rackspace Cloud - API Interactive '
                        'Website Application</p><div>For improvements or '
                        'suggestions please go to GitHub and submit an '
                        '<a href="https://github.com/rackerlabs/pitchfork/'
                        'issues/new" class="tooltip-title" target="_blank" '
                        'title="Submit a GitHub issue">issue</a></div>'
                    ),
                    'app_footer': (
                        'This site is not officially supported by Rackspace. '
                        'Source is available on <a href="https://github.com/'
                        'rackerlabs/pitchfork/" class="tooltip-title" target='
                        '"_blank" title="Pitchfork Repository">github</a>'
                    ),
                    'admins': [
                        {
                            'username': config.ADMIN_USERNAME,
                            'active': True,
                            'name': config.ADMIN_NAME,
                            'email': config.ADMIN_EMAIL
                        }
                    ],
                    'menu': [
                        {
                            'url': '/history',
                            'name': 'History',
                            'db_name': 'history',
                            'parent': '',
                            'active': True,
                            'parent_order': 1,
                            'order': 1,
                            'permissions': 'logged_in'
                        }, {
                            'url': '/favorites',
                            'name': 'Favorites',
                            'db_name': 'favorites',
                            'parent': '',
                            'active': True,
                            'parent_order': 1,
                            'order': 1,
                            'permissions': 'logged_in'
                        }, {
                            'url': '/autoscale',
                            'name': 'Autoscale',
                            'db_name': 'autoscale',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 1,
                            'permissions': 'all'
                        }, {
                            'url': '/backups',
                            'name': 'Backup',
                            'db_name': 'backup',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 2,
                            'permissions': 'all'
                        }, {
                            'url': '/big_data',
                            'name': 'Big Data',
                            'db_name': 'big_data',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 3,
                            'permissions': 'all'
                        }, {
                            'url': '/cbs',
                            'name': 'Block Storage',
                            'db_name': 'block_storage',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 4,
                            'permissions': 'all'
                        }, {
                            'url': '/cdn',
                            'name': 'CDN',
                            'db_name': 'cdn',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 5,
                            'permissions': 'all'
                        }, {
                            'url': '/databases',
                            'name': 'Databases',
                            'db_name': 'databases',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 6,
                            'permissions': 'all'
                        }, {
                            'url': '/dns',
                            'name': 'DNS',
                            'db_name': 'dns',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 7,
                            'permissions': 'all'
                        }, {
                            'url': '/cloud_feeds',
                            'name': 'Feeds',
                            'db_name': 'cloud_feeds',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 8,
                            'permissions': 'all'
                        }, {
                            'url': '/fg_servers',
                            'name': 'First Gen Servers',
                            'db_name': 'first_gen_servers',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 9,
                            'permissions': 'all'
                        }, {
                            'url': '/identity',
                            'name': 'Identity',
                            'db_name': 'identity',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 10,
                            'permissions': 'all'
                        }, {
                            'url': '/images',
                            'name': 'Images',
                            'db_name': 'images',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 11,
                            'permissions': 'all'
                        }, {
                            'url': '/load_balancers',
                            'name': 'Load Balancers',
                            'db_name': 'load_balancers',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 12,
                            'permissions': 'all'
                        }, {
                            'url': '/cloud_metrics',
                            'name': 'Cloud Metrics',
                            'db_name': 'cloud_metrics',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 13,
                            'permissions': 'all'
                        }, {
                            'url': '/monitoring',
                            'name': 'Monitoring',
                            'db_name': 'monitoring',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 14,
                            'permissions': 'all'
                        }, {
                            'url': '/networks',
                            'name': 'Networks',
                            'db_name': 'networks',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 15,
                            'permissions': 'all'
                        }, {
                            'url': '/orchestration',
                            'name': 'Orchestration',
                            'db_name': 'orchestration',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 16,
                            'permissions': 'all'
                        }, {
                            'url': '/queues',
                            'name': 'Queues',
                            'db_name': 'queues',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 17,
                            'permissions': 'all'
                        }, {
                            'url': '/rackconnect',
                            'name': 'RackConnect',
                            'db_name': 'rackconnect',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 18,
                            'permissions': 'all'
                        }, {
                            'url': '/servers',
                            'name': 'Servers',
                            'db_name': 'servers',
                            'parent': 'cloud_products',
                            'active': True,
                            'parent_order': 3,
                            'order': 19,
                            'permissions': 'all'
                        }, {
                            'url': '/autoscale/manage',
                            'name': 'Autoscale',
                            'db_name': 'autoscale_manage',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 1,
                            'permissions': 'administrators'
                        }, {
                            'url': '/backups/manage',
                            'name': 'Backup',
                            'db_name': 'backup_setup',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 2,
                            'permissions': 'administrators'
                        }, {
                            'url': '/big_data/manage',
                            'name': 'Big Data',
                            'db_name': 'big_data_setup',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 3,
                            'permissions': 'administrators'
                        }, {
                            'url': '/cbs/manage',
                            'name': 'Block Storage',
                            'db_name': 'block_storage_setup',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 4,
                            'permissions': 'administrators'
                        }, {
                            'url': '/cdn/manage',
                            'name': 'CDN',
                            'db_name': 'cdn_setup',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 5,
                            'permissions': 'administrators'
                        }, {
                            'url': '/databases/manage',
                            'name': 'Databases',
                            'db_name': 'databases_setup',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 6,
                            'permissions': 'administrators'
                        }, {
                            'url': '/dns/manage',
                            'name': 'DNS',
                            'db_name': 'dns_setup',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 7,
                            'permissions': 'administrators'
                        }, {
                            'url': '/cloud_feeds/manage',
                            'name': 'Feeds',
                            'db_name': 'manage_feeds',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 8,
                            'permissions': 'administrators'
                        }, {
                            'url': '/fg_servers/manage',
                            'name': 'FG Servers',
                            'db_name': 'fg_servers_setup',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 9,
                            'permissions': 'administrators'
                        }, {
                            'url': '/identity/manage',
                            'name': 'Identity',
                            'db_name': 'identity_setup',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 10,
                            'permissions': 'administrators'
                        }, {
                            'url': '/images/manage',
                            'name': 'Images',
                            'db_name': 'images_manage',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 11,
                            'permissions': 'administrators'
                        }, {
                            'url': '/load_balancers/manage',
                            'name': 'Load Balancers',
                            'db_name': 'lb_setup',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 12,
                            'permissions': 'administrators'
                        }, {
                            'url': '/cloud_metrics/manage',
                            'name': 'Cloud Metrics',
                            'db_name': 'cloud_metrics_setup',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 13,
                            'permissions': 'administrators'
                        }, {
                            'url': '/monitoring/manage',
                            'name': 'Monitoring',
                            'db_name': 'monitoring_manage',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 14,
                            'permissions': 'administrators'
                        }, {
                            'url': '/networks/manage',
                            'name': 'Networks',
                            'db_name': 'networks_setup',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 15,
                            'permissions': 'administrators'
                        }, {
                            'url': '/orchestration/manage',
                            'name': 'Orchestration',
                            'db_name': 'orchestration_manage',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 16,
                            'permissions': 'administrators'
                        }, {
                            'url': '/queues/manage',
                            'name': 'Queues',
                            'db_name': 'queues_manage',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 17,
                            'permissions': 'administrators'
                        }, {
                            'url': '/rackconnect/manage',
                            'name': 'RackConnect',
                            'db_name': 'rackconnect_manage',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 18,
                            'permissions': 'administrators'
                        }, {
                            'url': '/servers/manage',
                            'name': 'Servers',
                            'db_name': 'servers_setup',
                            'parent': 'manage_products',
                            'active': True,
                            'parent_order': 4,
                            'order': 19,
                            'permissions': 'administrators'
                        }, {
                            'url': '/autoscale/manage/api',
                            'name': 'Autoscale',
                            'db_name': 'autoscale_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 1,
                            'permissions': 'administrators'
                        }, {
                            'url': '/backups/manage/api',
                            'name': 'Backup',
                            'db_name': 'backup_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 2,
                            'permissions': 'administrators'
                        }, {
                            'url': '/big_data/manage/api',
                            'name': 'Big Data',
                            'db_name': 'big_data_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 3,
                            'permissions': 'administrators'
                        }, {
                            'url': '/cbs/manage/api',
                            'name': 'Block Storage',
                            'db_name': 'block_storage_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 4,
                            'permissions': 'administrators'
                        }, {
                            'url': '/cdn/manage/api',
                            'name': 'CDN',
                            'db_name': 'cdn_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 5,
                            'permissions': 'administrators'
                        }, {
                            'url': '/databases/manage/api',
                            'name': 'Databases',
                            'db_name': 'databases_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 6,
                            'permissions': 'administrators'
                        }, {
                            'url': '/dns/manage/api',
                            'name': 'DNS',
                            'db_name': 'dns_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 7,
                            'permissions': 'administrators'
                        }, {
                            'url': '/cloud_feeds/manage/api',
                            'name': 'Feeds',
                            'db_name': 'feeds_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 8,
                            'permissions': 'administrators'
                        }, {
                            'url': '/fg_servers/manage/api',
                            'name': 'FG Servers',
                            'db_name': 'fg_servers_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 9,
                            'permissions': 'administrators'
                        }, {
                            'url': '/identity/manage/api',
                            'name': 'Identity',
                            'db_name': 'identity_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 10,
                            'permissions': 'administrators'
                        }, {
                            'url': '/images/manage/api',
                            'name': 'Images',
                            'db_name': 'images_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 11,
                            'permissions': 'administrators'
                        }, {
                            'url': '/load_balancers/manage/api',
                            'name': 'Load Balancers',
                            'db_name': 'load_balancers_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 12,
                            'permissions': 'administrators'
                        }, {
                            'url': '/cloud_metrics/manage/api',
                            'name': 'Metrics',
                            'db_name': 'metrics_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 13,
                            'permissions': 'administrators'
                        }, {
                            'url': '/monitoring/manage/api',
                            'name': 'Monitoring',
                            'db_name': 'monitoring_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 14,
                            'permissions': 'administrators'
                        }, {
                            'url': '/networks/manage/api',
                            'name': 'Networks',
                            'db_name': 'networks_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 15,
                            'permissions': 'administrators'
                        }, {
                            'url': '/orchestration/manage/api',
                            'name': 'Orchestration',
                            'db_name': 'orchestration_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 16,
                            'permissions': 'administrators'
                        }, {
                            'url': '/queues/manage/api',
                            'name': 'Queues',
                            'db_name': 'queues_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 17,
                            'permissions': 'administrators'
                        }, {
                            'url': '/rackconnect/manage/api',
                            'name': 'RackConnect',
                            'db_name': 'rackconnect_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 18,
                            'permissions': 'administrators'
                        }, {
                            'url': '/servers/manage/api',
                            'name': 'Servers',
                            'db_name': 'servers_api',
                            'parent': 'api_settings',
                            'active': True,
                            'parent_order': 5,
                            'order': 19,
                            'permissions': 'administrators'
                        }, {
                            'active': True,
                            'name': 'Generate Report',
                            'db_name': 'engine',
                            'parent': '',
                            'url': '/engine/',
                            'parent_order': 6,
                            'divider': False,
                            'order': 3,
                            'permissions': 'administrators'
                        }, {
                            'url': '/admin/users/admins',
                            'name': 'Manage Admins',
                            'db_name': 'manage_admins',
                            'parent': 'system',
                            'active': True,
                            'parent_order': 7,
                            'order': 1,
                            'permissions': 'administrators'
                        }, {
                            'active': True,
                            'name': 'Manage Exemptions',
                            'db_name': 'manage_exemptions',
                            'order': 2,
                            'parent': 'system',
                            'parent_order': 7,
                            'url': '/admin/users/exemptions',
                            'permissions': 'administrators'
                        }, {
                            'active': True,
                            'name': 'Manage Engine',
                            'divider': True,
                            'db_name': 'engine_setup',
                            'order': 3,
                            'parent': 'system',
                            'parent_order': 7,
                            'url': '/engine/setup',
                            'permissions': 'administrators'
                        }, {
                            'url': '/manage/regions',
                            'name': 'Manage Regions',
                            'db_name': 'manage_regions',
                            'parent': 'system',
                            'active': True,
                            'parent_order': 7,
                            'order': 4,
                            'permissions': 'administrators'
                        }, {
                            'url': '/manage/verbs',
                            'name': 'Manage Verbs',
                            'db_name': 'manage_verbs',
                            'parent': 'system',
                            'active': True,
                            'parent_order': 7,
                            'order': 5,
                            'permissions': 'administrators'
                        }, {
                            'url': '/admin/general/',
                            'name': 'General Settings',
                            'db_name': 'general_settings',
                            'parent': 'administrators',
                            'active': True,
                            'parent_order': 8,
                            'order': 1,
                            'permissions': 'administrators'
                        }, {
                            'url': '/admin/menu/',
                            'name': 'Menu Settings',
                            'db_name': 'menu_settings',
                            'parent': 'administrators',
                            'active': True,
                            'parent_order': 8,
                            'order': 2,
                            'permissions': 'administrators'
                        }, {
                            'url': '/admin/roles/',
                            'name': 'Manage Roles',
                            'db_name': 'manage_roles',
                            'parent': 'administrators',
                            'active': True,
                            'parent_order': 8,
                            'order': 3,
                            'permissions': 'administrators'
                        }, {
                            'name': 'Anchor - Host Distribution',
                            'parent': 'additional_tools',
                            'url': 'https://rscloud.info',
                            'parent_order': 9,
                            'db_name': 'anchor',
                            'active': True,
                            'divider': False,
                            'order': 1,
                            'permissions': 'all'
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
                    'parent_menu': [
                        {
                            'order': 1,
                            'slug': 'history',
                            'name': 'History'
                        },  {
                            'order': 2,
                            'slug': 'favorites',
                            'name': 'Favorites'
                        }, {
                            'order': 3,
                            'slug': 'cloud_products',
                            'name': 'Cloud Products'
                        }, {
                            'order': 4,
                            'slug': 'manage_products',
                            'name': 'Manage Products'
                        }, {
                            'order': 5,
                            'slug': 'api_settings',
                            'name': 'API Settings'
                        }, {
                            'order': 6,
                            'name': 'Generate Report',
                            'slug': 'generate_report'
                        }, {
                            'order': 7,
                            'name': 'System',
                            'slug': 'system'
                        }, {
                            'order': 8,
                            'name': 'Administrators',
                            'slug': 'administrators'
                        },  {
                            'order': 9,
                            'slug': 'additional_tools',
                            'name': 'Additional Tools'
                        }
                    ],
                    'roles': [
                        {
                            'active': True,
                            'name': 'Administrators',
                            'slug': 'administrators'
                        }, {
                            'active': True,
                            'name': 'Logged In',
                            'slug': 'logged_in',
                            'perms': [
                                '/',
                                '/<product>/',
                                '/<product>/api/call/process',
                                '/generate_hybrid_token',
                                '/favorites',
                                '/feedback/',
                                '/<product>/favorites/<action>',
                                '/admin/logout/',
                                '/history'
                            ]
                        }, {
                            'active': True,
                            'name': 'All',
                            'slug': 'all',
                            'perms': [
                                '/',
                                '/<product>/',
                                '/<product>/api/call/process',
                                '/admin/login',
                                '/admin/login/check'
                            ]
                        },
                    ],
                    'application_set': True
                }
            }
        )

    if api_settings is None:
        db.api_settings.insert(
            {
                'active_products': [
                    'autoscale',
                    'big_data',
                    'databases',
                    'dns',
                    'cloud_feeds',
                    'fg_servers',
                    'identity',
                    'images',
                    'load_balancers',
                    'monitoring',
                    'networks',
                    'orchestration',
                    'queues',
                    'rackconnect',
                    'cdn',
                    'cbs',
                    'servers',
                    'backups',
                    'cloud_metrics'
                ],
                'autoscale': {
                    'app_url': '/autoscale',
                    'title': 'Autoscale',
                    'us_api': (
                        'https://{region}.autoscale.api.rackspacecloud.com'
                    ),
                    'db_name': 'autoscale',
                    'groups': [
                        {
                            'order': 1,
                            'name': 'Scaling Groups',
                            'slug': 'scaling_groups'
                        }, {
                            'order': 2,
                            'slug': 'configurations',
                            'name': 'Configurations'
                        }, {
                            'slug': 'policies',
                            'order': 3,
                            'name': 'Policies'
                        }, {
                            'slug': 'webhooks',
                            'name': 'Webhooks',
                            'order': 4
                        },
                    ],
                    'uk_api': (
                        'https://{region}.autoscale.api.rackspacecloud.com'
                    ),
                    'active': True,
                    'require_region': True,
                    'doc_url': (
                        'http://docs.rackspace.com/cas/api/v1.0'
                        '/autoscale-devguide/content/Overview.html'
                    )
                },
                'big_data': {
                    'app_url': '/big_data',
                    'title': 'Big Data',
                    'us_api': (
                        'https://{region}.bigdata.api.rackspacecloud.com'
                    ),
                    'db_name': 'big_data',
                    'groups': [
                        {
                            'order': 1,
                            'slug': 'clusters',
                            'name': 'Clusters'
                        }, {
                            'slug': 'nodes',
                            'order': 2,
                            'name': 'Nodes'
                        }, {
                            'slug': 'flavors',
                            'name': 'Flavors',
                            'order': 3
                        }, {
                            'order': 4,
                            'slug': 'types',
                            'name': 'Types'
                        }, {
                            'order': 5,
                            'name': 'Profiles',
                            'slug': 'profiles'
                        }, {
                            'order': 6,
                            'name': 'Limits',
                            'slug': 'limits'
                        }
                    ],
                    'uk_api': (
                        'https://{region}.bigdata.api.rackspacecloud.com'
                    ),
                    'active': True,
                    'require_region': True,
                    'doc_url': (
                        'http://docs.rackspace.com/cbd/api/v1.0'
                        '/cbd-devguide/content/overview.html'
                    )
                },
                'cloud_feeds': {
                    'app_url': '/cloud_feeds',
                    'title': 'Cloud Feeds',
                    'us_api': 'https://{region}.feeds.api.rackspacecloud.com',
                    'db_name': 'cloud_feeds',
                    'groups': [],
                    'uk_api': 'https://{region}.feeds.api.rackspacecloud.com',
                    'active': True,
                    'require_region': True,
                    'doc_url': (
                        'http://docs.rackspace.com/cloud-feeds/api/v1.0'
                        '/feeds-devguide/content/overview.html'
                    )
                },
                'databases': {
                    'app_url': '/databases',
                    'title': 'Databases',
                    'us_api': (
                        'https://{region}.databases.api.rackspacecloud.com'
                    ),
                    'db_name': 'cloud_db',
                    'groups': [
                        {
                            'order': 1,
                            'name': 'Instances',
                            'slug': 'instances'
                        }, {
                            'order': 2,
                            'slug': 'databases',
                            'name': 'Databases'
                        }, {
                            'slug': 'users',
                            'order': 3,
                            'name': 'Users'
                        }, {
                            'order': 4,
                            'slug': 'actions',
                            'name': 'Actions'
                        }, {
                            'order': 5,
                            'slug': 'backups',
                            'name': 'Backups'
                        }, {
                            'slug': 'configurations',
                            'name': 'Configurations',
                            'order': 6
                        }, {
                            'slug': 'flavors',
                            'order': 7,
                            'name': 'Flavors'
                        }, {
                            'order': 8,
                            'name': 'Types',
                            'slug': 'types'
                        }, {
                            'slug': 'api_versions',
                            'name': 'API Versions',
                            'order': 9
                        }
                    ],
                    'uk_api': (
                        'https://{region}.databases.api.rackspacecloud.com'
                    ),
                    'active': True,
                    'require_region': True,
                    'doc_url': (
                        'http://docs.rackspace.com/cdb/api/v1.0'
                        '/cdb-devguide/content/overview.html'
                    )
                },
                'dns': {
                    'app_url': '/dns',
                    'title': 'DNS',
                    'us_api': 'https://dns.api.rackspacecloud.com',
                    'db_name': 'cloud_dns',
                    'groups': [
                        {
                            'order': 1,
                            'name': 'Domains',
                            'slug': 'domains'
                        }, {
                            'slug': 'subdomains',
                            'name': 'Subdomains',
                            'order': 2
                        }, {
                            'slug': 'records',
                            'order': 3,
                            'name': 'Records'
                        }, {
                            'order': 4,
                            'slug': 'reverse_dns',
                            'name': 'Reverse DNS'
                        }, {
                            'order': 5,
                            'slug': 'jobs',
                            'name': 'Jobs'
                        }, {
                            'order': 6,
                            'name': 'Limits',
                            'slug': 'limits'
                        }
                    ],
                    'uk_api': 'https://lon.dns.api.rackspacecloud.com',
                    'active': True,
                    'require_region': True,
                    'doc_url': (
                        'http://docs.rackspace.com/cdns/api/v1.0'
                        '/cdns-devguide/content/overview.html'
                    )
                },
                'fg_servers': {
                    'app_url': '/fg_servers',
                    'title': 'First Gen Servers',
                    'us_api': 'https://servers.api.rackspacecloud.com',
                    'db_name': 'fg_servers',
                    'groups': [
                        {
                            'order': 1,
                            'name': 'Servers',
                            'slug': 'servers'
                        }, {
                            'slug': 'actions',
                            'order': 2,
                            'name': 'Actions'
                        }, {
                            'order': 3,
                            'slug': 'images',
                            'name': 'Images'
                        }, {
                            'order': 4,
                            'name': 'Backup Schedules',
                            'slug': 'backup_schedules'
                        }, {
                            'slug': 'shared_ip_groups',
                            'order': 5,
                            'name': 'Shared IP Groups'
                        }, {
                            'order': 6,
                            'slug': 'addresses',
                            'name': 'Addresses'
                        }, {
                            'slug': 'flavors',
                            'name': 'Flavors',
                            'order': 7
                        }
                    ],
                    'uk_api': 'https://lon.servers.api.rackspacecloud.com',
                    'active': True,
                    'require_region': True,
                    'doc_url': (
                        'http://docs.rackspace.com/servers/api/v1.0'
                        '/cs-devguide/content/Overview-d1e70.html'
                    )
                },
                'identity': {
                    'app_url': '/identity',
                    'title': 'Identity',
                    'us_api': 'https://identity.api.rackspacecloud.com',
                    'db_name': 'cloud_identity',
                    'groups': [
                        {
                            'slug': 'tokens',
                            'order': 1,
                            'name': 'Tokens'
                        }, {
                            'order': 2,
                            'slug': 'users',
                            'name': 'Users'
                        }, {
                            'slug': 'roles',
                            'name': 'Roles',
                            'order': 3
                        }, {
                            'order': 4,
                            'name': 'Tenants',
                            'slug': 'tenants'
                        }, {
                            'order': 5,
                            'slug': 'domains',
                            'name': 'Domains'
                        }, {
                            'order': 6,
                            'name': 'Extensions',
                            'slug': 'extensions'
                        }, {
                            'slug': 'contract_versions',
                            'order': 7,
                            'name': 'Contract Versions'
                        }
                    ],
                    'uk_api': 'https://lon.identity.api.rackspacecloud.com',
                    'active': True,
                    'require_region': True,
                    'doc_url': (
                        'http://docs.rackspace.com/auth/api/v2.0'
                        '/auth-client-devguide/content/Overview-d1e65.html'
                    )
                },
                'images': {
                    'app_url': '/images',
                    'title': 'Images',
                    'us_api': 'https://{region}.images.api.rackspacecloud.com',
                    'db_name': 'images',
                    'groups': [
                        {
                            'order': 1,
                            'name': 'Operations',
                            'slug': 'operations'
                        }, {
                            'slug': 'sharing',
                            'order': 2,
                            'name': 'Sharing'
                        }, {
                            'slug': 'tasks',
                            'name': 'Tasks',
                            'order': 3
                        }, {
                            'order': 4,
                            'slug': 'tags',
                            'name': 'Tags'
                        }, {
                            'order': 5,
                            'name': 'Schema',
                            'slug': 'schema'
                        }
                    ],
                    'uk_api': 'https://{region}.images.api.rackspacecloud.com',
                    'active': True,
                    'require_region': True,
                    'doc_url': (
                        'http://docs.rackspace.com/images/api/v2/ci-'
                        'devguide/content/ch_image-service-dev-overview.html'
                    )
                },
                'load_balancers': {
                    'app_url': '/load_balancers',
                    'title': 'Load Balancers',
                    'us_api': (
                        'https://{region}.loadbalancers.api.rackspacecloud.com'
                    ),
                    'db_name': 'load_balancers',
                    'groups': [
                        {
                            'order': 1,
                            'slug': 'load_balancers',
                            'name': 'Load Balancers'
                        }, {
                            'order': 2,
                            'name': 'Nodes',
                            'slug': 'nodes'
                        }, {
                            'slug': 'virtual_ips',
                            'name': 'Virtual IPs',
                            'order': 3
                        }, {
                            'slug': 'ssl',
                            'order': 4,
                            'name': 'SSL'
                        }, {
                            'slug': 'caching',
                            'name': 'Caching',
                            'order': 5
                        }, {
                            'slug': 'throttling',
                            'order': 6,
                            'name': 'Throttling'
                        }, {
                            'order': 7,
                            'name': 'Log Connections',
                            'slug': 'log_connections'
                        }, {
                            'order': 8,
                            'slug': 'session_persistence',
                            'name': 'Session Persistence'
                            }, {
                            'slug': 'health_monitoring',
                            'name': 'Health Monitoring',
                            'order': 9
                        }, {
                            'slug': 'access_lists',
                            'order': 10,
                            'name': 'Access Lists'
                        }, {
                            'order': 11,
                            'slug': 'allowed_domains',
                            'name': 'Allowed Domains'
                        }, {
                            'slug': 'error_pages',
                            'order': 12,
                            'name': 'Error Pages'
                        }, {
                            'slug': 'metadata',
                            'name': 'Metadata',
                            'order': 13
                        }, {
                            'order': 14,
                            'name': 'Usage',
                            'slug': 'usage'
                        }, {
                            'order': 15,
                            'name': 'Algorithms',
                            'slug': 'algorithms'
                        }, {
                            'order': 16,
                            'slug': 'protocols',
                            'name': 'Protocols'
                        }
                    ],
                    'uk_api': (
                        'https://{region}.loadbalancers.api.rackspacecloud.com'
                    ),
                    'active': True,
                    'require_region': True,
                    'doc_url': (
                        'http://docs.rackspace.com/loadbalancers/api/v1.0'
                        '/clb-devguide/content/Overview-d1e82.html'
                    )
                },
                'monitoring': {
                    'app_url': '/monitoring',
                    'title': 'Monitoring',
                    'us_api': 'https://monitoring.api.rackspacecloud.com',
                    'db_name': 'monitoring',
                    'groups': [
                        {
                            'slug': 'account',
                            'order': 1,
                            'name': 'Account'
                        }, {
                            'order': 2,
                            'name': 'Entities',
                            'slug': 'entities'
                        }, {
                            'slug': 'checks',
                            'order': 3,
                            'name': 'Checks'
                        }, {
                            'order': 4,
                            'name': 'Alarms',
                            'slug': 'alarms'
                        }, {
                            'order': 5,
                            'name': 'Suppressions',
                            'slug': 'suppressions'
                        }, {
                            'slug': 'notifications',
                            'name': 'Notifications',
                            'order': 6
                        }, {
                            'slug': 'agents',
                            'name': 'Agents',
                            'order': 7
                        }, {
                            'slug': 'zones',
                            'name': 'Zones',
                            'order': 8
                        }, {
                            'order': 9,
                            'slug': 'check_types',
                            'name': 'Check Types'
                        }, {
                            'slug': 'notification_plan',
                            'order': 10,
                            'name': 'Notification Plan'
                        }, {
                            'order': 11,
                            'slug': 'notification_types',
                            'name': 'Notification Types'
                        }, {
                            'order': 12,
                            'name': 'Metrics',
                            'slug': 'metrics'
                        }, {
                            'slug': 'alarm_notification_history',
                            'name': 'Alarm Notification History',
                            'order': 13
                        }, {
                            'slug': 'changelogs',
                            'order': 14,
                            'name': 'Changelogs'
                        }, {
                            'order': 15,
                            'slug': 'overview',
                            'name': 'Overview'
                        }, {
                            'slug': 'agent_tokens',
                            'order': 16,
                            'name': 'Agent Tokens'
                        }, {
                            'order': 17,
                            'slug': 'agent_targets',
                            'name': 'Agent Targets'
                        }, {
                            'order': 18,
                            'name': 'Agent Host Information',
                            'slug': 'agent_host_information'
                        }, {
                            'order': 19,
                            'slug': 'alarm_examples',
                            'name': 'Alarm Examples'
                        }
                    ],
                    'uk_api': 'https://monitoring.api.rackspacecloud.com',
                    'active': True,
                    'require_region': False,
                    'doc_url': (
                        'http://docs.rackspace.com/cm/api/v1.0'
                        '/cm-devguide/content/overview.html'
                    )
                },
                'networks': {
                    'app_url': '/networks',
                    'title': 'Networks',
                    'us_api': (
                        'https://{region}.networks.api.rackspacecloud.com'
                    ),
                    'db_name': 'cloud_networks',
                    'groups': [
                        {
                            'order': 1,
                            'slug': 'networks',
                            'name': 'Networks'
                        }, {
                            'slug': 'subnets',
                            'order': 2,
                            'name': 'Subnets'
                        }, {
                            'slug': 'ports',
                            'name': 'Ports',
                            'order': 3
                        }, {
                            'order': 4,
                            'name': 'Security Groups',
                            'slug': 'security_groups'
                        }
                    ],
                    'uk_api': (
                        'https://{region}.networks.api.rackspacecloud.com'
                    ),
                    'active': True,
                    'require_region': True,
                    'doc_url': (
                        'http://docs.rackspace.com/networks/api/v2'
                        '/cn-devguide/content/ch_preface.html'
                    )
                },
                'orchestration': {
                    'app_url': '/orchestration',
                    'title': 'Orchestration',
                    'us_api': (
                        'https://{region}.orchestration.api.rackspacecloud.com'
                    ),
                    'db_name': 'orchestration',
                    'groups': [
                        {
                            'order': 1,
                            'slug': 'stack_operations',
                            'name': 'Stack Operations'
                        }, {
                            'order': 2,
                            'name': 'Stack Resources',
                            'slug': 'stack_resources'
                        }, {
                            'slug': 'stack_events',
                            'order': 3,
                            'name': 'Stack Events'
                        }, {
                            'slug': 'templates',
                            'name': 'Templates',
                            'order': 4
                        }, {
                            'order': 5,
                            'slug': 'build_info',
                            'name': 'Build Info'
                        }
                    ],
                    'uk_api': (
                        'https://{region}.orchestration.api.rackspacecloud.com'
                    ),
                    'active': True,
                    'require_region': True,
                    'doc_url': (
                        'http://docs.rackspace.com/orchestration/api/v1'
                        '/orchestration-devguide/content/overview.html'
                    )
                },
                'queues': {
                    'app_url': '/queues',
                    'title': 'Queues',
                    'us_api': 'https://{region}.queues.api.rackspacecloud.com',
                    'db_name': 'queues',
                    'groups': [
                        {
                            'slug': 'queues',
                            'name': 'Queues',
                            'order': 1
                        }, {
                            'order': 2,
                            'slug': 'messages',
                            'name': 'Messages'
                        }, {
                            'order': 3,
                            'name': 'Claims',
                            'slug': 'claims'
                        }, {
                            'order': 4,
                            'slug': 'home_document',
                            'name': 'Home Document'
                        }
                    ],
                    'uk_api': 'https://{region}.queues.api.rackspacecloud.com',
                    'active': True,
                    'require_region': True,
                    'doc_url': (
                        'http://docs.rackspace.com/queues/api/v1.0'
                        '/cq-devguide/content/overview.html'
                    )
                },
                'rackconnect': {
                    'app_url': '/rackconnect',
                    'title': 'RackConnect',
                    'us_api': (
                        'https://{region}.rackconnect.api.rackspacecloud.com'
                    ),
                    'db_name': 'rack_connect',
                    'groups': [
                        {
                            'slug': 'public_ips',
                            'name': 'Public IPs',
                            'order': 1
                        }, {
                            'order': 2,
                            'slug': 'load_balancer_pools',
                            'name': 'Load Balancer Pools'
                        }, {
                            'slug': 'networks',
                            'order': 3,
                            'name': 'Networks'
                        }
                    ],
                    'uk_api': (
                        'https://{region}.rackconnect.api.rackspacecloud.com'
                    ),
                    'active': True,
                    'require_region': True,
                    'doc_url': (
                        'http://docs.rackspace.com/rackconnect/api/v3'
                        '/rackconnect-devguide/content/Overview.html'
                    )
                },
                'cloud_metrics': {
                    'app_url': '/metrics',
                    'title': 'Cloud Metrics',
                    'us_api': 'https://global.metrics.api.rackspacecloud.com',
                    'db_name': 'cloud_metrics',
                    'groups': [
                        {
                            'order': 1,
                            'name': 'Queries',
                            'slug': 'queries'
                        }
                    ],
                    'uk_api': 'https://global.metrics.api.rackspacecloud.com',
                    'active': True,
                    'require_region': False,
                    'doc_url': (
                        'http://docs.rackspace.com/cmet/api/v1.0'
                        '/cmet-gettingstarted/content/doc-change-history.html'
                    )
                },
                'servers': {
                    'app_url': '/servers',
                    'title': 'Cloud Servers',
                    'us_api': (
                        'https://{region}.servers.api.rackspacecloud.com'
                    ),
                    'db_name': 'cloud_servers',
                    'groups': [
                        {
                            'order': 1,
                            'name': 'Servers',
                            'slug': 'servers'
                        }, {
                            'slug': 'actions',
                            'order': 2,
                            'name': 'Actions'
                        }, {
                            'slug': 'metadata',
                            'order': 3,
                            'name': 'Metadata'
                        }, {
                            'order': 4,
                            'name': 'Volumes',
                            'slug': 'volumes'
                        }, {
                            'order': 5,
                            'name': 'Networks',
                            'slug': 'networks'
                        }, {
                            'slug': 'images',
                            'name': 'Images',
                            'order': 6
                        }, {
                            'order': 7,
                            'slug': 'flavors',
                            'name': 'Flavors'
                        }, {
                            'slug': 'addresses',
                            'name': 'Addresses',
                            'order': 8
                        }, {
                            'order': 9,
                            'slug': 'key_pairs',
                            'name': 'Key Pairs'
                        }
                    ],
                    'uk_api': (
                        'https://{region}.servers.api.rackspacecloud.com'
                    ),
                    'active': True,
                    'require_region': True,
                    'doc_url': (
                        'http://docs.rackspace.com/servers/api/v2/'
                        'cs-devguide/content/ch_preface.html'
                    )
                },
                'cdn': {
                    'app_url': '/cdn',
                    'title': 'CDN',
                    'us_api': 'https://global.cdn.api.rackspacecloud.com',
                    'db_name': 'cdn',
                    'groups': [
                        {
                            'order': 1,
                            'slug': 'services',
                            'name': 'Services'
                        }, {
                            'slug': 'assets',
                            'order': 2,
                            'name': 'Assets'
                        }, {
                            'order': 3,
                            'name': 'Operations',
                            'slug': 'operations'
                        }, {
                            'slug': 'flavors',
                            'name': 'Flavors',
                            'order': 4
                        }
                    ],
                    'uk_api': 'https://global.cdn.api.rackspacecloud.com',
                    'active': True,
                    'require_region': False,
                    'doc_url': (
                        'http://docs.rackspace.com/cdn/api/v1.0'
                        '/cdn-devguide/content/Overview.html'
                    )
                },
                'cbs': {
                    'app_url': '/cbs',
                    'title': 'CBS',
                    'us_api': (
                        'https://{region}.blockstorage.api.rackspacecloud.com'
                    ),
                    'db_name': 'cbs',
                    'groups': [
                        {
                            'slug': 'snapshots',
                            'name': 'Snapshots',
                            'order': 1
                        }, {
                            'slug': 'volumes',
                            'order': 2,
                            'name': 'Volumes'
                        }, {
                            'order': 3,
                            'slug': 'operations',
                            'name': 'Operations'
                        }, {
                            'order': 4,
                            'name': 'Types',
                            'slug': 'types'
                        }
                    ],
                    'uk_api': (
                        'https://{region}.blockstorage.api.rackspacecloud.com'
                    ),
                    'active': True,
                    'require_region': True,
                    'doc_url': (
                        'http://docs.rackspace.com/cbs/api/v1.0'
                        '/cbs-devguide/content/overview.html'
                    )
                },
                'backups': {
                    'app_url': '/backups',
                    'title': 'Cloud Backup',
                    'us_api': 'https://{region}.backup.api.rackspacecloud.com',
                    'db_name': 'cloud_backup',
                    'groups': [
                        {
                            'order': 1,
                            'name': 'Agent Operations',
                            'slug': 'agent_operations'
                        }, {
                            'order': 2,
                            'slug': 'backup_configurations',
                            'name': 'Backup Configurations'
                        }, {
                            'slug': 'backup_operations',
                            'name': 'Backup Operations',
                            'order': 3
                        }, {
                            'order': 4,
                            'slug': 'restore_configurations',
                            'name': 'Restore Configurations'
                        }, {
                            'order': 5,
                            'name': 'Restore Operations',
                            'slug': 'restore_operations'
                        }, {
                            'slug': 'user_operations',
                            'order': 6,
                            'name': 'User Operations'
                        }, {
                            'slug': 'activity',
                            'order': 7,
                            'name': 'Activity'
                        }
                    ],
                    'uk_api': 'https://{region}.backup.api.rackspacecloud.com',
                    'active': True,
                    'require_region': True,
                    'doc_url': (
                        'http://docs.rackspace.com/rcbu/api/v1.0'
                        '/rcbu-devguide/content/overview.html'
                    )
                },
                'regions': [
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

    if reporting is None:
        db.reporting.insert(
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
        db.reporting.insert(
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
        db.reporting.insert(
            {
                'data_type': 'text',
                'description': 'Data Center where call was made',
                'field_display': 'SelectField',
                'field_display_data': '',
                'field_display_label': '',
                'field_name': 'region',
                'graphable': True,
                'searchable': True
            }
        )
        db.reporting.insert(
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
        db.reporting.insert(
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
        db.reporting.insert(
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
