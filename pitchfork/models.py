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

from flask import g
from operator import itemgetter
from datetime import datetime
from dateutil import tz


import re


def slug(string):
    if string:
        temp = re.sub(' +', ' ', string.lower())
        return re.sub(' ', '_', temp)


class Product:
    def __init__(self, product):
        self.app_url = product.get('app_url')
        self.title = product.get('title')
        self.us_api = product.get('us_api')
        self.uk_api = product.get('uk_api')
        self.require_region = bool(product.get('require_region'))
        self.doc_url = product.get('doc_url')
        self.active = bool(product.get('active'))
        self.db_name = product.get('db_name')
        if product.get('groups'):
            self.groups = product.get('groups')
        else:
            self.groups = []

    def set_db_name(self):
        temp = re.sub(' +', ' ', str(self.title.lower().strip()))
        self.db_name = re.sub(' ', '_', temp)

    def get_endpoints(self):
        return {'us_api': self.us_api, 'uk_api': self.uk_api}

    def get_db_name(self):
        if not self.db_name:
            self.set_db_name()

        return self.db_name

    def add_group(self, group):
        found, order = False, 1
        for item in self.groups:
            if slug(group) == item.get('slug'):
                found = True
            if item.get('order') == order:
                order += 1

        if not found:
            self.groups.append(
                {
                    'slug': slug(group),
                    'name': group,
                    'order': order
                }
            )

    def get_sorted_groups(self):
        return sorted(self.groups, key=itemgetter('order'))

    def get_total_calls(self):
        return getattr(g.db, self.db_name).count()

    def get_active_calls(self):
        return getattr(g.db, self.db_name).find({'tested': True}).count()

    def get_testing_calls(self):
        return getattr(g.db, self.db_name).find({'tested': False}).count()

    def get_total_executions(self):
        temp = getattr(g.db, self.db_name).aggregate(
            [{
                '$project': {
                    '_id': 0,
                    'accessed': 1
                }
            }, {
                '$group': {
                    '_id': '',
                    'total': {'$sum': '$accessed'}
                }
            }]
        )
        for item in temp:
            if (
                isinstance(item, dict) and
                item.get('result') and
                len(item.get('result')) == 1
            ):
                return int(item.get('result')[0].get('total'))
        return 0


class Favorite:
    def __init__(self, data):
        self.username = data.get('username')
        if data.get('favorites'):
            self.favorites = data.get('favorites')
        else:
            self.favorites = []

    def add_to_favorites(self, call_id, db_name, app_url, user):
        favorite = {
            'call_id': call_id,
            'db_name': db_name,
            'app_url': app_url
        }
        current_favorites = g.db.favorites.find_one({'username': user})
        if current_favorites:
            g.db.favorites.update(
                {
                    'username': user
                }, {
                    '$addToSet': {
                        'favorites': favorite
                    }
                }
            )
        else:
            g.db.favorites.insert(
                {
                    'username': user,
                    'favorites': [
                        favorite
                    ]
                }
            )

    def remove_favorite(self, call_id, user):
        g.db.favorites.update(
            {
                'username': user
            }, {
                '$pull': {
                    'favorites': {
                        'call_id': call_id
                    }
                }
            }
        )


class Call:
    def __init__(self, call):
        self.title = call.get('title').strip().lower().title()
        self.short_description = call.get('short_description')
        self.verb = call.get('verb')
        self.api_uri = call.get('api_uri').strip()
        self.doc_url = call.get('doc_url').strip()
        self.add_to_header = bool(call.get('add_to_header'))
        self.custom_header_key = call.get('custom_header_key', '').strip()
        self.custom_header_value = call.get('custom_header_value', '').strip()
        self.change_content_type = bool(call.get('change_content_type'))
        self.custom_content_type = call.get('custom_content_type', '').strip()
        self.use_data = bool(call.get('use_data'))
        self.data_object = call.get('data_object')
        self.allow_filter = bool(call.get('allow_filter'))
        self.remove_token = bool(call.get('remove_token'))
        self.remove_ddi = bool(call.get('remove_ddi'))
        self.remove_content_type = bool(call.get('remove_content_type'))
        self.required_key = bool(call.get('required_key'))
        self.required_key_name = call.get('required_key_name', '').strip()
        self.required_key_type = call.get('required_key_type')
        self.tested = bool(call.get('tested'))
        self.variables = call.get('variables', [])
        if call.get('group') == 'add_new_group':
            self.group = self.setup_new_group(
                call.get('new_group'),
                call.get('product')
            )
        else:
            self.group = call.get('group')

    def setup_new_group(self, group, product):
        api_settings = g.db.api_settings.find_one()
        if api_settings and api_settings.get(product):
            temp_product = Product(api_settings.get(product))
            temp_product.add_group(group)
            g.db.api_settings.update(
                {}, {
                    '$set': {
                        product: temp_product.__dict__
                    }
                }
            )
            return slug(group)


class Variable:
    def __init__(self, variable):
        self.field_type = variable.get('field_type')
        self.description = variable.get('description')
        self.required = bool(variable.get('required'))
        self.field_display_data = variable.get('field_display_data')
        self.id_value = int(variable.get('id_value', 0))
        self.field_display = variable.get('field_display')
        self.variable_name = variable.get('variable_name', '').strip()


class Verb:
    def __init__(self, data):
        self.name = data.get('name').upper()
        self.active = bool(data.get('active'))


class Region:
    def __init__(self, data):
        self.abbreviation = data.get('abbreviation').upper()
        self.name = data.get('name')


class Feedback:
    def __init__(self, data):
        self.call_id = data.get('call_id')
        self.product_db = data.get('product_db')
        self.category = data.get('category')
        self.feedback = data.get('feedback')

        if data.get('product_url'):
            self.product_url = data.get('product_url')
        else:
            self.product_url = self.get_product_url(data.get('product_db'))

        if data.get('submitted'):
            self.submitted = data.get('submitted')
        else:
            self.submitted = datetime.now(tz.tzutc())

        if data.get('complete'):
            self.complete = data.get('complete')
        else:
            self.complete = False

    def get_product_url(self, product_db):
        api_settings = g.db.api_settings.find_one()
        if api_settings and api_settings.get(product_db):
            return api_settings.get(product_db).get('app_url')
        return None
