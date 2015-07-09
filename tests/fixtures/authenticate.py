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

auth_return = {
    'access': {
        'token': {
            'RAX-AUTH:authenticatedBy': [
                'APIKEY'
            ],
            'expires': '2015-06-23T12:44:18.758Z',
            'id': '183e2f66535d4e03a04b2a91cf4a4f83',
            'tenant': {
                'id': '123456',
                'name': '123456'
            }
        },
        'serviceCatalog': [
            {
                'endpoints': [
                    {
                        'region': 'IAD',
                        'publicURL': (
                            'https://cdn5.clouddrive.com/'
                            'v1/MossoCloudFS_123456'
                        ),
                        'tenantId': 'MossoCloudFS_123456'
                    }, {
                        'region': 'SYD',
                        'publicURL': (
                            'https://cdn4.clouddrive.com/v1/'
                            'MossoCloudFS_123456'
                        ),
                        'tenantId': 'MossoCloudFS_123456'
                    }, {
                        'region': 'DFW',
                        'publicURL': (
                            'https://cdn1.clouddrive.com/v1/'
                            'MossoCloudFS_123456'
                        ),
                        'tenantId': 'MossoCloudFS_123456'
                    }, {
                        'region': 'HKG',
                        'publicURL': (
                            'https://cdn6.clouddrive.com/v1/'
                            'MossoCloudFS_123456'
                        ),
                        'tenantId': 'MossoCloudFS_123456'
                    }
                ],
                'type': 'rax:object-cdn',
                'name': 'cloudFilesCDN'
            }, {
                'endpoints': [
                    {
                        'region': 'IAD',
                        'publicURL': (
                            'https://storage101.iad3.clouddrive.com/v1'
                            '/MossoCloudFS_123456'
                        ),
                        'internalURL': (
                            'https://snet-storage101.iad3.clouddrive.com/v1'
                            '/MossoCloudFS_123456'
                        ),
                        'tenantId': 'MossoCloudFS_123456'
                    }, {
                        'region': 'SYD',
                        'publicURL': (
                            'https://storage101.syd2.clouddrive.com/v1'
                            '/MossoCloudFS_123456'
                        ),
                        'internalURL': (
                            'https://snet-storage101.syd2.clouddrive.com/v1'
                            '/MossoCloudFS_123456'
                        ),
                        'tenantId': 'MossoCloudFS_123456'
                    }, {
                        'region': 'DFW',
                        'publicURL': (
                            'https://storage101.dfw1.clouddrive.com/v1'
                            '/MossoCloudFS_123456'
                        ),
                        'internalURL': (
                            'https://snet-storage101.dfw1.clouddrive.com/v1'
                            '/MossoCloudFS_123456'
                        ),
                        'tenantId': 'MossoCloudFS_123456'
                    }, {
                        'region': 'HKG',
                        'publicURL': (
                            'https://storage101.hkg1.clouddrive.com/v1'
                            '/MossoCloudFS_123456'
                        ),
                        'internalURL': (
                            'https://snet-storage101.hkg1.clouddrive.com/v1'
                            '/MossoCloudFS_123456'
                        ),
                        'tenantId': 'MossoCloudFS_123456'
                    }
                ],
                'type': 'object-store',
                'name': 'cloudFiles'
            }, {
                'endpoints': [
                    {
                        'region': 'DFW',
                        'publicURL': (
                            'https://dfw.blockstorage.api.rackspacecloud.com/'
                            'v1/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'SYD',
                        'publicURL': (
                            'https://syd.blockstorage.api.rackspacecloud.com/'
                            'v1/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'IAD',
                        'publicURL': (
                            'https://iad.blockstorage.api.rackspacecloud.com/'
                            'v1/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'HKG',
                        'publicURL': (
                            'https://hkg.blockstorage.api.rackspacecloud.com/'
                            'v1/123456'
                        ),
                        'tenantId': '123456'
                    }
                ],
                'type': 'volume',
                'name': 'cloudBlockStorage'
            }, {
                'endpoints': [
                    {
                        'region': 'IAD',
                        'publicURL': (
                            'https://iad.images.api.rackspacecloud.com/v2'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'HKG',
                        'publicURL': (
                            'https://hkg.images.api.rackspacecloud.com/v2'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'DFW',
                        'publicURL': (
                            'https://dfw.images.api.rackspacecloud.com/v2'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'SYD',
                        'publicURL': (
                            'https://syd.images.api.rackspacecloud.com/v2'
                        ),
                        'tenantId': '123456'
                    }
                ],
                'type': 'image',
                'name': 'cloudImages'
            }, {
                'endpoints': [
                    {
                        'region': 'HKG',
                        'publicURL': (
                            'https://hkg.queues.api.rackspacecloud.com/'
                            'v1/123456'
                        ),
                        'internalURL': (
                            'https://snet-hkg.queues.api.rackspacecloud.com/'
                            'v1/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'SYD',
                        'publicURL': (
                            'https://syd.queues.api.rackspacecloud.com/'
                            'v1/123456'
                        ),
                        'internalURL': (
                            'https://snet-syd.queues.api.rackspacecloud.com/'
                            'v1/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'DFW',
                        'publicURL': (
                            'https://dfw.queues.api.rackspacecloud.com/'
                            'v1/123456'
                        ),
                        'internalURL': (
                            'https://snet-dfw.queues.api.rackspacecloud.com/'
                            'v1/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'IAD',
                        'publicURL': (
                            'https://iad.queues.api.rackspacecloud.com/'
                            'v1/123456'
                        ),
                        'internalURL': (
                            'https://snet-iad.queues.api.rackspacecloud.com/'
                            'v1/123456'
                        ),
                        'tenantId': '123456'
                    }
                ],
                'type': 'rax:queues',
                'name': 'cloudQueues'
            }, {
                'endpoints': [
                    {
                        'region': 'IAD',
                        'publicURL': (
                            'https://iad.bigdata.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'DFW',
                        'publicURL': (
                            'https://dfw.bigdata.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }
                ],
                'type': 'rax:bigdata',
                'name': 'cloudBigData'
            }, {
                'endpoints': [
                    {
                        'region': 'HKG',
                        'publicURL': (
                            'https://hkg.orchestration.api.rackspacecloud.com/'
                            'v1/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'DFW',
                        'publicURL': (
                            'https://dfw.orchestration.api.rackspacecloud.com/'
                            'v1/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'IAD',
                        'publicURL': (
                            'https://iad.orchestration.api.rackspacecloud.com/'
                            'v1/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'SYD',
                        'publicURL': (
                            'https://syd.orchestration.api.rackspacecloud.com/'
                            'v1/123456'
                        ),
                        'tenantId': '123456'
                    }
                ],
                'type': 'orchestration',
                'name': 'cloudOrchestration'
            }, {
                'endpoints': [
                    {
                        'region': 'IAD',
                        'tenantId': '123456',
                        'versionId': '2',
                        'versionList': (
                            'https://iad.servers.api.rackspacecloud.com/'
                        ),
                        'versionInfo': (
                            'https://iad.servers.api.rackspacecloud.com/v2'
                        ),
                        'publicURL': (
                            'https://iad.servers.api.rackspacecloud.com/'
                            'v2/123456'
                        )
                    }, {
                        'region': 'DFW',
                        'tenantId': '123456',
                        'versionId': '2',
                        'versionList': (
                            'https://dfw.servers.api.rackspacecloud.com/'
                        ),
                        'versionInfo': (
                            'https://dfw.servers.api.rackspacecloud.com/v2'
                        ),
                        'publicURL': (
                            'https://dfw.servers.api.rackspacecloud.com/'
                            'v2/123456'
                        )
                    }, {
                        'region': 'SYD',
                        'tenantId': '123456',
                        'versionId': '2',
                        'versionList': (
                            'https://syd.servers.api.rackspacecloud.com/'
                        ),
                        'versionInfo': (
                            'https://syd.servers.api.rackspacecloud.com/v2'
                        ),
                        'publicURL': (
                            'https://syd.servers.api.rackspacecloud.com/'
                            'v2/123456'
                        )
                    }, {
                        'region': 'HKG',
                        'tenantId': '123456',
                        'versionId': '2',
                        'versionList': (
                            'https://hkg.servers.api.rackspacecloud.com/'
                        ),
                        'versionInfo': (
                            'https://hkg.servers.api.rackspacecloud.com/v2'
                        ),
                        'publicURL': (
                            'https://hkg.servers.api.rackspacecloud.com/'
                            'v2/123456'
                        )
                    }
                ],
                'type': 'compute',
                'name': 'cloudServersOpenStack'
            }, {
                'endpoints': [
                    {
                        'region': 'DFW',
                        'publicURL': (
                            'https://dfw.autoscale.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'HKG',
                        'publicURL': (
                            'https://hkg.autoscale.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'IAD',
                        'publicURL': (
                            'https://iad.autoscale.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'SYD',
                        'publicURL': (
                            'https://syd.autoscale.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }
                ],
                'type': 'rax:autoscale',
                'name': 'autoscale'
            }, {
                'endpoints': [
                    {
                        'region': 'DFW',
                        'publicURL': (
                            'https://dfw.databases.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'IAD',
                        'publicURL': (
                            'https://iad.databases.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'SYD',
                        'publicURL': (
                            'https://syd.databases.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'HKG',
                        'publicURL': (
                            'https://hkg.databases.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }
                ],
                'type': 'rax:database',
                'name': 'cloudDatabases'
            }, {
                'endpoints': [
                    {
                        'region': 'IAD',
                        'publicURL': (
                            'https://iad.backup.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'HKG',
                        'publicURL': (
                            'https://hkg.backup.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'SYD',
                        'publicURL': (
                            'https://syd.backup.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'DFW',
                        'publicURL': (
                            'https://dfw.backup.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }
                ],
                'type': 'rax:backup',
                'name': 'cloudBackup'
            }, {
                'endpoints': [
                    {
                        'region': 'IAD',
                        'publicURL': (
                            'https://iad.networks.api.rackspacecloud.com/v2.0'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'SYD',
                        'publicURL': (
                            'https://syd.networks.api.rackspacecloud.com/v2.0'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'DFW',
                        'publicURL': (
                            'https://dfw.networks.api.rackspacecloud.com/v2.0'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'HKG',
                        'publicURL': (
                            'https://hkg.networks.api.rackspacecloud.com/v2.0'
                        ),
                        'tenantId': '123456'
                    }
                ],
                'type': 'network',
                'name': 'cloudNetworks'
            }, {
                'endpoints': [
                    {
                        'region': 'IAD',
                        'publicURL': (
                            'https://iad.loadbalancers.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'HKG',
                        'publicURL': (
                            'https://hkg.loadbalancers.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'DFW',
                        'publicURL': (
                            'https://dfw.loadbalancers.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'SYD',
                        'publicURL': (
                            'https://syd.loadbalancers.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }
                ],
                'type': 'rax:load-balancer',
                'name': 'cloudLoadBalancers'
            }, {
                'endpoints': [
                    {
                        'region': 'IAD',
                        'publicURL': (
                            'https://global.metrics.api.rackspacecloud.com/'
                            'v2.0/123456'
                        ),
                        'tenantId': '123456'
                    }
                ],
                'type': 'rax:cloudmetrics',
                'name': 'cloudMetrics'
            }, {
                'endpoints': [
                    {
                        'region': 'HKG',
                        'publicURL': (
                            'https://hkg.feeds.api.rackspacecloud.com/123456'
                        ),
                        'internalURL': (
                            'https://atom.prod.hkg1.us.ci.rackspace.net/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'SYD',
                        'publicURL': (
                            'https://syd.feeds.api.rackspacecloud.com/123456'
                        ),
                        'internalURL': (
                            'https://atom.prod.syd2.us.ci.rackspace.net/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'IAD',
                        'publicURL': (
                            'https://iad.feeds.api.rackspacecloud.com/123456'
                        ),
                        'internalURL': (
                            'https://atom.prod.iad3.us.ci.rackspace.net/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'DFW',
                        'publicURL': (
                            'https://dfw.feeds.api.rackspacecloud.com/123456'
                        ),
                        'internalURL': (
                            'https://atom.prod.dfw1.us.ci.rackspace.net/123456'
                        ),
                        'tenantId': '123456'
                    }, {
                        'region': 'ORD',
                        'publicURL': (
                            'https://ord.feeds.api.rackspacecloud.com/123456'
                        ),
                        'internalURL': (
                            'https://atom.prod.ord1.us.ci.rackspace.net/123456'
                        ),
                        'tenantId': '123456'
                    }
                ],
                'type': 'rax:feeds',
                'name': 'cloudFeeds'
            }, {
                'endpoints': [
                    {
                        'region': 'DFW',
                        'publicURL': (
                            'https://sites.api.rackspacecloud.com/v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }
                ],
                'type': 'rax:sites',
                'name': 'cloudSites'
            }, {
                'endpoints': [
                    {
                        'publicURL': (
                            'https://monitoring.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }
                ],
                'type': 'rax:monitor',
                'name': 'cloudMonitoring'
            }, {
                'endpoints': [
                    {
                        'publicURL': (
                            'https://dns.api.rackspacecloud.com/v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }
                ],
                'type': 'rax:dns',
                'name': 'cloudDNS'
            }, {
                'endpoints': [
                    {
                        'region': 'DFW',
                        'publicURL': (
                            'https://global.cdn.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'internalURL': (
                            'https://global.cdn.api.rackspacecloud.com/'
                            'v1.0/123456'
                        ),
                        'tenantId': '123456'
                    }
                ],
                'type': 'rax:cdn',
                'name': 'rackCDN'
            }
        ],
        'user': {
            'RAX-AUTH:defaultRegion': 'IAD',
            'id': 'a432dbe77f5e4e20a88aaf1cab26c51b',
            'roles': [
                {
                    'description': (
                        'A Role that allows a user access'
                        ' to keystone Service methods'
                    ),
                    'id': '5',
                    'name': 'object-store:default',
                    'tenantId': 'MossoCloudFS_123456'
                }, {
                    'description': (
                        'A Role that allows a user access'
                        ' to keystone Service methods'
                    ),
                    'id': '6',
                    'name': 'compute:default',
                    'tenantId': '123456'
                }, {
                    'id': '3',
                    'name': 'identity:user-admin',
                    'description': 'User Admin Role.'
                }
            ],
            'name': 'rusty.shackelford'
        }
    }
}
