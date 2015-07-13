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
from models import Product
from bson.objectid import ObjectId


import re


def utility_processor():
    def unslug(string):
        return re.sub('_|\+', ' ', string)

    def parse_field_data(value):
        choices = re.sub('\r\n', ',', value)
        return choices.split(',')

    def slugify(data):
        temp_string = re.sub(' +', ' ', str(data.strip()))
        return re.sub(' ', '_', temp_string)

    def get_product_for_call(product):
        temp_product = g.db.api_settings.find_one()
        if temp_product and temp_product.get(product):
            return Product(temp_product.get(product))
        return {}

    def get_product_call(call_id, db_name):
        if call_id:
            return getattr(g.db, db_name).find_one(
                {'_id': ObjectId(str(call_id))}
            )

    return dict(
        parse_field_data=parse_field_data,
        unslug=unslug,
        slugify=slugify,
        get_product_for_call=get_product_for_call,
        get_product_call=get_product_call
    )
