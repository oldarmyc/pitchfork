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

from dateutil import tz, parser
from datetime import datetime, timedelta
from flask import g

import re
import forms


def unslug(value):
    text = re.sub('_', ' ', value)
    return text.title()


def parse_field_data(value):
        choices = re.sub('\r\n', ',', value)
        return choices.split(',')


def generate_reporting_form():
    class F(forms.Reporting):
        pass

    fields = g.db.reporting.find({'searchable': True})
    for field in fields:
        if field.get('data_type') == 'boolean':
            choices = [('', ''), (True, 'True'), (False, 'False')]
            setattr(
                F,
                unslug(field.get('field_name')),
                forms.SelectField(
                    '%s:' % unslug(field.get('field_name')),
                    choices=choices
                )
            )

        elif field.get('data_type') == 'datetime':
            setattr(
                F,
                '%s-start' % unslug(field.get('field_name')),
                forms.TextField(
                    'After Date:',
                    id='date_time_start'
                )
            )
            setattr(
                F,
                '%s-end' % unslug(field.get('field_name')),
                forms.TextField(
                    'Before Date:',
                    id='date_time_end'
                )
            )

        elif field.get('field_display') == 'TextField':
            setattr(
                F,
                unslug(field.get('field_name')),
                forms.TextField(
                    '%s:' % unslug(field.get('field_name'))
                )
            )

        elif field.get('field_display') == 'SelectField':

            api_settings = g.db.api_settings.find_one()
            if field.get('field_name') == 'product':
                products = ['']
                for product in api_settings.get('active_products'):
                    temp_product = api_settings.get(product)
                    products.append(temp_product.get('title'))

                choices = [(item, item) for item in products]
            elif field.get('field_name') == 'data_center':
                dcs = ['']
                for item in api_settings.get('dcs'):
                    dcs.append(item.get('abbreviation'))

                choices = [(item, item) for item in dcs]
            elif field.get('field_name') == 'verb':
                verbs = ['']
                for item in api_settings.get('verbs'):
                    if item.get('active'):
                        verbs.append(item.get('name'))

                choices = [(item, item) for item in verbs]
            else:
                select_items = parse_field_data(
                    field.get('field_display_data')
                )
                select_items.insert(0, '')
                choices = [(item, item) for item in select_items]

            setattr(
                F,
                unslug(field.get('field_name')),
                forms.SelectField(
                    '%s:' % unslug(field.get('field_name')),
                    choices=choices
                )
            )

    setattr(
        F,
        'submit',
        forms.SubmitField('Generate Report')
    )
    return F()


def check_for_field(data, compare, found):
    for key, value in data.iteritems():
        if isinstance(value, dict):
            found = check_for_field(value, compare, found)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    found = check_for_field(item, compare, found)
        else:
            if key == compare:
                found = True
    return found


def generate_reporting_query(request):
    query = {}
    if request.json.get('Name') != '':
        query['name'] = {
            '$regex': request.json.get('Name'),
            '$options': 'i'
        }

    if request.json.get('Ddi') != '':
        query['ddi'] = request.json.get('Ddi')

    if (
        request.json.get('Data Center') != '' and
        request.json.get('Data Center')
    ):
        query['data_center'] = request.json.get('Data Center').lower()

    if request.json.get('Verb') != '':
        query['request.verb'] = request.json.get('Verb')

    if request.json.get('Product') != '':
        query['product'] = request.json.get('Product')

    if (
        request.json.get('Completed At-start') != '' and
        request.json.get('Completed At-end') != '' and
        request.json.get('Completed At-start') and
        request.json.get('Completed At-end')
    ):
        after_date = parser.parse(request.json.get('Completed At-start'))
        before_date = parser.parse(request.json.get('Completed At-end'))
        before_date = before_date + timedelta(days=1)
        query['completed_at'] = {'$gte': after_date, '$lt': before_date}

    elif (
        request.json.get('Completed At-start') != '' and
        request.json.get('Completed At-start')
    ):
        after_date = parser.parse(request.json.get('Completed At-start'))
        query['completed_at'] = {'$gte': after_date}

    elif (
        request.json.get('Completed At-end') != '' and
        request.json.get('Completed At-end')
    ):
        before_date = parser.parse(request.json.get('Completed At-end'))
        before_date = before_date + timedelta(days=1)
        query['completed_at'] = {'$lt': before_date}

    return query
