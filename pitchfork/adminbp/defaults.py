
from flask import g, session, current_app


def check_and_initialize():
    settings = g.db.settings.find_one()
    forms = g.db.forms.find_one()
    api_settings = g.db.api_settings.find_one()
    if settings is None:
        current_app.logger.debug('Settings are empty...initializing')
        g.db.settings.insert(
            {
                'application_title': current_app.name.title(),
                'application_email': current_app.config.get('APP_EMAIL'),
                'application_well': (
                    '<p class="lead">Rackspace Cloud API interactive website '
                    'application</p><div class="center">'
                    'For improvements or suggestions please go to GitHub and '
                    'submit an <a href="https://github.com/rackerlabs/'
                    'pitchfork/issues/new" target="_blank" title="Submit'
                    ' a GitHub issue">issue</a></div><div id="issue_feedback"'
                    ' class="center"></div>'
                ),
                'application_footer': '&copy; Rackspace, US',
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
                        'active': True,
                        'display_name': 'My History',
                        'name': 'my_history',
                        'parent': '',
                        'url': '/history',
                        'parent_order': 1,
                        'order': 2,
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'Autoscale',
                        'name': 'autoscale',
                        'parent': 'cloud_products',
                        'url': '/autoscale',
                        'parent_order': 2,
                        'order': 1,
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'Backup',
                        'name': 'backup',
                        'parent': 'cloud_products',
                        'url': '/cloud_backup',
                        'parent_order': 2,
                        'order': 2,
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'Big Data',
                        'name': 'big_data',
                        'parent': 'cloud_products',
                        'url': '/big_data',
                        'parent_order': 2,
                        'order': 3,
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'Block Storage',
                        'name': 'block_storage',
                        'parent': 'cloud_products',
                        'url': '/block_storage',
                        'parent_order': 2,
                        'order': 4,
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'Databases',
                        'name': 'databases',
                        'parent': 'cloud_products',
                        'url': '/databases',
                        'parent_order': 2,
                        'order': 5,
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'DNS',
                        'name': 'dns',
                        'parent': 'cloud_products',
                        'url': '/dns',
                        'parent_order': 2,
                        'order': 6,
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'First Gen Servers',
                        'name': 'first_gen_servers',
                        'parent': 'cloud_products',
                        'url': '/fg_servers',
                        'parent_order': 2,
                        'order': 7,
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'Identity',
                        'name': 'identity',
                        'parent': 'cloud_products',
                        'url': '/identity',
                        'parent_order': 2,
                        'order': 8,
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'Images',
                        'name': 'images',
                        'parent': 'cloud_products',
                        'url': '/images',
                        'parent_order': 2,
                        'order': 9,
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'Load Balancers',
                        'name': 'load_balancers',
                        'parent': 'cloud_products',
                        'url': '/load_balancers',
                        'parent_order': 2,
                        'order': 10,
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'Monitoring',
                        'name': 'monitoring',
                        'parent': 'cloud_products',
                        'url': '/monitoring',
                        'parent_order': 2,
                        'order': 11,
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'Networks',
                        'name': 'networks',
                        'parent': 'cloud_products',
                        'url': '/networks',
                        'parent_order': 2,
                        'order': 12,
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'Next Gen Servers',
                        'name': 'next_gen_servers',
                        'parent': 'cloud_products',
                        'url': '/ng_servers',
                        'parent_order': 2,
                        'order': 13,
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'Orchestration',
                        'name': 'orchestration',
                        'parent': 'cloud_products',
                        'url': '/orchestration',
                        'parent_order': 2,
                        'order': 14,
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'Queues',
                        'name': 'queues',
                        'parent': 'cloud_products',
                        'url': '/queues',
                        'parent_order': 2,
                        'order': 15,
                        'view_permissions': 'logged_in'
                    }, {
                        'active': True,
                        'display_name': 'Autoscale',
                        'name': 'autoscale_manage',
                        'parent': 'manage_products',
                        'url': '/autoscale/manage',
                        'parent_order': 3,
                        'order': 1,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Backup',
                        'name': 'backup_setup',
                        'order': 2,
                        'parent': 'manage_products',
                        'parent_order': 3,
                        'url': '/cloud_backup/manage',
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Big Data',
                        'name': 'big_data_setup',
                        'parent': 'manage_products',
                        'url': '/big_data/manage',
                        'parent_order': 3,
                        'order': 3,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Block Storage',
                        'name': 'block_storage_setup',
                        'parent': 'manage_products',
                        'url': '/block_storage/manage',
                        'parent_order': 3,
                        'order': 4,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Databases',
                        'name': 'databases_setup',
                        'parent': 'manage_products',
                        'url': '/databases/manage',
                        'parent_order': 3,
                        'order': 5,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'DNS',
                        'name': 'dns_setup',
                        'parent': 'manage_products',
                        'url': '/dns/manage',
                        'parent_order': 3,
                        'order': 6,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'FG Servers',
                        'name': 'fg_servers_setup',
                        'parent': 'manage_products',
                        'url': '/fg_servers/manage',
                        'parent_order': 3,
                        'order': 7,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Identity',
                        'name': 'identity_setup',
                        'parent': 'manage_products',
                        'url': '/identity/manage',
                        'parent_order': 3,
                        'order': 8,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Images',
                        'name': 'images_manage',
                        'parent': 'manage_products',
                        'url': '/images/manage',
                        'parent_order': 3,
                        'order': 9,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Load Balancers',
                        'name': 'lb_setup',
                        'parent': 'manage_products',
                        'url': '/load_balancers/manage',
                        'parent_order': 3,
                        'order': 10,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Monitoring',
                        'name': 'monitoring_manage',
                        'order': 11,
                        'parent': 'manage_products',
                        'parent_order': 3,
                        'url': '/monitoring/manage',
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Networks',
                        'name': 'networks_setup',
                        'parent': 'manage_products',
                        'url': '/networks/manage',
                        'parent_order': 3,
                        'order': 12,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'NG Servers',
                        'name': 'ng_server_setup',
                        'parent': 'manage_products',
                        'url': '/ng_servers/manage',
                        'parent_order': 3,
                        'order': 13,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Orchestration',
                        'name': 'orchestration_manage',
                        'parent': 'manage_products',
                        'url': '/orchestration/manage',
                        'parent_order': 3,
                        'order': 14,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Queues',
                        'name': 'queues_manage',
                        'parent': 'manage_products',
                        'url': '/queues/manage',
                        'parent_order': 3,
                        'order': 15,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Autoscale',
                        'name': 'autoscale_api',
                        'parent': 'api_settings',
                        'url': '/autoscale/manage/api',
                        'parent_order': 4,
                        'order': 1,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Backup',
                        'name': 'backup_api',
                        'parent': 'api_settings',
                        'url': '/cloud_backup/manage/api',
                        'parent_order': 4,
                        'order': 2,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Big Data',
                        'name': 'big_data_api',
                        'parent': 'api_settings',
                        'url': '/big_data/manage/api',
                        'parent_order': 4,
                        'order': 3,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Block Storage',
                        'name': 'block_storage_api',
                        'parent': 'api_settings',
                        'url': '/block_storage/manage/api',
                        'parent_order': 4,
                        'order': 4,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Databases',
                        'name': 'databases_api',
                        'parent': 'api_settings',
                        'url': '/databases/manage/api',
                        'parent_order': 4,
                        'order': 5,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'DNS',
                        'name': 'dns_api',
                        'parent': 'api_settings',
                        'url': '/dns/manage/api',
                        'parent_order': 4,
                        'order': 6,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'FG Servers',
                        'name': 'fg_servers_api',
                        'parent': 'api_settings',
                        'url': '/fg_servers/manage/api',
                        'parent_order': 4,
                        'order': 7,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Identity',
                        'name': 'identity_api',
                        'parent': 'api_settings',
                        'url': '/identity/manage/api',
                        'parent_order': 4,
                        'order': 8,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Images',
                        'name': 'images_api',
                        'parent': 'api_settings',
                        'url': '/images/manage/api',
                        'parent_order': 4,
                        'order': 9,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Load Balancers',
                        'name': 'load_balancers_api',
                        'parent': 'api_settings',
                        'url': '/load_balancers/manage/api',
                        'parent_order': 4,
                        'order': 10,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Monitoring',
                        'name': 'monitoring_api',
                        'parent': 'api_settings',
                        'url': '/monitoring/manage/api',
                        'parent_order': 4,
                        'order': 11,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Networks',
                        'name': 'networks_api',
                        'parent': 'api_settings',
                        'url': '/networks/manage/api',
                        'parent_order': 4,
                        'order': 12,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'NG Servers',
                        'name': 'ng_servers_api',
                        'parent': 'api_settings',
                        'url': '/ng_servers/manage/api',
                        'parent_order': 4,
                        'order': 13,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Orchestration',
                        'name': 'orchestration_api',
                        'parent': 'api_settings',
                        'url': '/orchestration/manage/api',
                        'parent_order': 4,
                        'order': 14,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Queues',
                        'name': 'queues_api',
                        'parent': 'api_settings',
                        'url': '/queues/manage/api',
                        'parent_order': 4,
                        'order': 15,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Generate Report',
                        'name': 'reporting',
                        'order': 1,
                        'parent': 'reporting',
                        'parent_order': 5,
                        'url': '/reporting',
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Report Setup',
                        'name': 'reporting_setup',
                        'order': 2,
                        'parent': 'reporting',
                        'parent_order': 5,
                        'url': '/reporting/setup',
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Manage Fields',
                        'name': 'reporting_fields',
                        'order': 3,
                        'parent': 'reporting',
                        'parent_order': 5,
                        'url': '/reporting/fields/manage',
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Manage Admins',
                        'name': 'manage_admins',
                        'parent': 'system',
                        'url': '/admin/settings/admins',
                        'parent_order': 6,
                        'order': 1,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Data Centers',
                        'name': 'manage_dcs',
                        'parent': 'system',
                        'url': '/manage/dcs',
                        'parent_order': 6,
                        'order': 2,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'API Verbs',
                        'name': 'manage_verbs',
                        'parent': 'system',
                        'url': '/manage/verbs',
                        'parent_order': 6,
                        'order': 3,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'General Settings',
                        'name': 'general_settings',
                        'order': 1,
                        'parent': 'administrators',
                        'parent_order': 7,
                        'url': '/admin/settings/general',
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Menu Settings',
                        'name': 'menu_settings',
                        'parent': 'administrators',
                        'url': '/admin/settings/menu',
                        'parent_order': 7,
                        'order': 2,
                        'view_permissions': 'administrators'
                    }, {
                        'active': True,
                        'display_name': 'Manage Roles',
                        'name': 'manage_roles',
                        'parent': 'administrators',
                        'url': '/admin/settings/roles',
                        'parent_order': 7,
                        'order': 3,
                        'view_permissions': 'administrators'
                    }, {
                        'url': '/admin/forms',
                        'display_name': 'Manage Forms',
                        'name': 'manage_forms',
                        'parent': 'administrators',
                        'active': True,
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
                        'slug': 'my_history',
                        'name': 'My History',
                        'order': 1
                    }, {
                        'slug': 'cloud_products',
                        'name': 'Cloud Products',
                        'order': 2
                    }, {
                        'slug': 'manage_products',
                        'name': 'Manage Products',
                        'order': 3
                    }, {
                        'slug': 'api_settings',
                        'name': 'API Settings',
                        'order': 4
                    }, {
                        'slug': 'reporting',
                        'name': 'Reporting',
                        'order': 5
                    }, {
                        'slug': 'system',
                        'name': 'System',
                        'order': 6
                    }, {
                        'name': 'Administrators',
                        'slug': 'administrators',
                        'order': 7,
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
                            '/ng_servers/',
                            '/ng_servers/api_call/process',
                            '/identity/',
                            '/identity/api_call/process',
                            '/dns/',
                            '/dns/api_call/process',
                            '/cloud_backup/',
                            '/cloud_backup/api_call/process',
                            '/queues/',
                            '/queues/api_call/process',
                            '/networks/',
                            '/networks/api_call/process',
                            '/big_data/',
                            '/big_data/api_call/process',
                            '/autoscale/',
                            '/autoscale/api_call/process',
                            '/block_storage/',
                            '/block_storage/api_call/process',
                            '/monitoring/',
                            '/monitoring/api_call/process',
                            '/images/',
                            '/images/api_call/process',
                            '/orchestration/',
                            '/orchestration/api_call/process',
                            '/load_balancers/',
                            '/load_balancers/api_call/process',
                            '/databases/',
                            '/databases/api_call/process',
                            '/fg_servers/',
                            '/fg_servers/api_call/process',
                        ]
                    }, {
                        'active': True,
                        'display_name': 'All',
                        'name': 'all',
                        'perms': [
                            '/'
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
                    'cbs',
                    'cloud_db',
                    'cloud_dns',
                    'fg_servers',
                    'cloud_identity',
                    'images',
                    'load_balancers',
                    'monitoring',
                    'ng_servers',
                    'cloud_networks',
                    'orchestration',
                    'queues'
                ],
                'autoscale': {
                    'app_url': '/autoscale',
                    'title': 'Autoscale',
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
                'cbs': {
                    'app_url': '/block_storage',
                    'title': 'Block Storage',
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
                'cloud_db': {
                    'app_url': '/databases',
                    'title': 'Databases',
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
                'cloud_dns': {
                    'app_url': '/dns',
                    'title': 'DNS',
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
                'cloud_identity': {
                    'app_url': '/identity',
                    'title': 'Identity',
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
                'cloud_networks': {
                    'app_url': '/networks',
                    'title': 'Networks',
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
                    'us_api': (
                        'https://monitoring.api.rackspacecloud.com/v1.0/{ddi}'
                    ),
                    'uk_api': (
                        'https://monitoring.api.rackspacecloud.com/v1.0/{ddi}',
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
                        'label': 'View Permissions:'
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
                        'field_type': 'SubmitField',
                        'field_choices': '',
                        'name': 'menu',
                        'default': False,
                        'style_id': '',
                        'required': False,
                        'active': True,
                        'order': 8,
                        'label': 'Submit'
                    }
                ],
                'name': 'menu_items_form',
                'submission_url': '/admin/settings/menu',
                'system_form': True
            }
        )

    return settings
