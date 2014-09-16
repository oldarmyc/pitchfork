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

from pitchfork import db


import re


class Product:
    def __init__(self, product):
        self.app_url = product.get('app_url')
        self.title = product.get('title')
        self.us_api = product.get('us_api')
        self.uk_api = product.get('uk_api')
        self.require_dc = bool(product.get('require_dc'))
        self.doc_url = product.get('doc_url')
        self.active = bool(product.get('active'))
        self.db_name = product.get('db_name')

    def __unicode__(self):
        return self.title

    def set_db_name(self):
        temp = re.sub(' +', ' ', str(self.title.lower().strip()))
        self.db_name = re.sub(' ', '_', temp)

    def get_db_name(self):
        if not self.db_name:
            self.set_db_name()

        return self.db_name


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
        self.use_data = bool(call.get('use_data'))
        self.data_object = call.get('data_object')
        self.remove_token = bool(call.get('remove_token'))
        self.remove_content_type = bool(call.get('remove_content_type'))
        self.required_key = bool(call.get('required_key'))
        self.required_key_name = call.get('required_key_name', '').strip()
        self.required_key_type = call.get('required_key_type')
        self.tested = bool(call.get('tested'))
        self.variables = call.get('variables', [])

    def __unicode__(self):
        return self.title


class Variable:
    def __init__(self, variable):
        self.field_type = variable.get('field_type')
        self.description = variable.get('description')
        self.required = bool(variable.get('required'))
        self.field_display_data = variable.get('field_display_data')
        self.id_value = int(variable.get('id_value'))
        self.field_display = variable.get('field_display')
        self.variable_name = variable.get('variable_name', '').strip()

    def __unicode__(self):
        return self.variable_name
