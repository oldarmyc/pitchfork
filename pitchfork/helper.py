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


from flask import g, session
from dateutil import tz
from models import Variable
from pygments import highlight
from pygments.lexers import JsonLexer, XmlLexer
from pygments.formatters import HtmlFormatter
from bson.objectid import ObjectId


import re
import copy
import requests
import json
import forms
import pymongo
import datetime


UTC = tz.tzutc()


requests.packages.urllib3.disable_warnings()


def get_timestamp():
    return datetime.datetime.now(UTC)


def check_for_product_regions(product=None):
    restrict_regions, regions = False, []
    api_settings = g.db.api_settings.find_one()
    if api_settings:
        regions = api_settings.get('regions')
        if not regions:
            regions = api_settings.get('dcs')

        if product and product.require_region:
            restrict_regions = check_url_endpoints(
                product.us_api,
                product.uk_api
            )
            if restrict_regions:
                regions = [
                    {'abbreviation': 'US'},
                    {'abbreviation': 'UK'}
                ]

    return restrict_regions, regions


def generate_group_choices(product):
    choices = [('', '')]
    for group in product.groups:
        choices.append((group.get('slug'), group.get('name')))
    choices.append(('add_new_group', 'Add New Group'))
    return choices


def check_url_endpoints(us, uk):
    us_find = re.findall('\{(.+?)\}', us)
    uk_find = re.findall('\{(.+?)\}', uk)
    if 'region' in us_find:
        return False

    if 'region' in uk_find:
        return False

    return True


def change_group_order(groups, new_position, old_position, group_slug, db):
    for group in groups:
        if group.get('order') == new_position:
            g.db.api_settings.update(
                {
                    '%s.groups.slug' % db: group.get('slug')
                }, {
                    '$set': {
                        '%s.groups.$.order' % db: old_position
                    }
                }
            )
        elif group.get('slug') == group_slug:
            g.db.api_settings.update(
                {
                    '%s.groups.slug' % db: group.get('slug')
                }, {
                    '$set': {
                        '%s.groups.$.order' % db: new_position
                    }
                }
            )
    return


def gather_api_calls(product, testing, groups):
    if testing:
        query = {
            '$or': [
                {'tested': False},
                {'tested': None}
            ]
        }
    else:
        query = {'tested': True}

    api_calls = getattr(g.db, product.get_db_name()).find(query).sort(
        [('title', pymongo.ASCENDING)]
    )
    calls = {'': []}
    for group in groups:
        calls[group.get('slug')] = []

    for call in api_calls:
        if call.get('group'):
            calls[call.get('group')].append(call)
        else:
            calls[''].append(call)

    return calls


def add_fields_to_form(count):
    class F(forms.ApiCall):
        pass

    for i in range(count):
        setattr(
            F,
            'variable_%i' % i,
            forms.fields.FormField(forms.CallVariables)
        )

    setattr(
        F,
        'submit',
        forms.fields.SubmitField('Submit')
    )
    return F()


def generate_edit_call_form(product, call, call_id):
    count = 1
    if len(call.variables) > 1:
        count = len(call.variables)

    form = add_fields_to_form(count)
    if len(call.variables) > 0:
        for i in range(count):
            temp = getattr(form, 'variable_%i' % i)
            temp_variable = Variable(call.variables[i])
            temp.form.field_type.data = temp_variable.field_type
            temp.form.required.data = temp_variable.required
            temp.form.description.data = temp_variable.description
            temp.form.variable_name.data = temp_variable.variable_name
            temp.form.field_display.data = temp_variable.field_display
            temp.form.field_display_data.data = (
                temp_variable.field_display_data
            )
            temp.form.id_value.data = temp_variable.id_value

    for key, value in call.__dict__.iteritems():
        if key != 'variables':
            setattr(getattr(form, key), 'data', value)

    form.id.data = call_id
    return form, count


def get_vars_for_call(submissions):
    data, count = [], []
    for key, value in submissions:
        temp = re.search('variable_(\d+?)-(\w.*)', key)
        if temp:
            if count:
                if not int(temp.group(1)) in count:
                    count.append(int(temp.group(1)))
            else:
                count.append(int(temp.group(1)))

    for placeholder in range(len(count)):
        data.append({'ignore': 'placeholder'})

    for key, value in submissions:
        temp = re.search('variable_(\d+?)-(\w.*)', key)
        if temp:
            if temp.group(2) != 'csrf_token':
                if str(temp.group(2)) == 'required':
                    if value[0]:
                        data[int(temp.group(1))][str(temp.group(2))] = bool(
                            value[0]
                        )
                elif str(temp.group(2)) == 'id_value':
                    if value[0]:
                        data[int(temp.group(1))][str(temp.group(2))] = int(
                            value[0]
                        )
                else:
                    data[int(temp.group(1))][str(temp.group(2))] = value[0]

    return_data = []
    for variable in data:
        if variable.get('variable_name'):
            temp_var = Variable(variable)
            return_data.append(temp_var.__dict__)

    return return_data


def generate_vars_for_call(product, call, request):
    data_package = None
    api_url = generate_api_url_for_call(product, request)
    if call.get('use_data'):
        if request.json.get('mock'):
            data_package = json.loads(call.get('data_object'))
        else:
            """
                Find escaped newlines and replace them with a non escaped
                newline in the raw string. Doing this in order to handle JSON
                escaped newlines from the request form so that it can be
                encoded again for the API request correctly
            """
            temp_data = re.sub(r'\\\\n', r'\\n', request.data)
            data_request = json.loads(temp_data)
            data_package = process_api_data_request(call, data_request)

    header = create_custom_header(call, request.json)
    return api_url, header, data_package


def generate_api_url_for_call(product, request):
    data_center = request.json.get('data_center')
    if data_center in ['uk', 'lon']:
        region_url = product.uk_api
    else:
        region_url = product.us_api

    temp_url = "%s%s" % (
        region_url,
        request.json.get('api_url')
    )
    if request.json.get('mock'):
        if data_center is None:
            api_url = temp_url
        else:
            api_url = process_api_url(temp_url, request)
    else:
        api_url = process_api_url(temp_url, request)

    return api_url


def process_api_url(url, request):
    """ Regex loop to replace the URL with the needed values """

    def evaluate_replace(m):
        if request.json.get(m.group(2)):
            return re.sub(
                m.group(1),
                request.json.get(m.group(2)).strip(),
                m.group(0)
            )
        else:
            return m.group(1)

    api_url = re.sub('(\{(.+?)\})', evaluate_replace, url)
    temp_filter = request.json.get('add_filter')
    if temp_filter and len(temp_filter) > 1:
        temp_filter = re.sub('\?', '', temp_filter)
        api_url = '%s?%s' % (api_url, temp_filter)

    return api_url


def check_variable_type(api_call, key_value):
    for var in api_call.get('variables'):
        if var.get('variable_name') == key_value:
            return var.get('field_type')

    return 'string'


def recursive_dict_object(
    parent_key,
    value,
    api_call,
    json_data,
    data_object,
    temp_dict,
    req_key,
    req_key_value
):
    if isinstance(value, dict):
        sub_dict = {}
        temp_parent = parent_key
        for sub_key, sub_value in value.iteritems():
            sub_dict = recursive_dict_object(
                sub_key,
                sub_value,
                api_call,
                json_data,
                data_object,
                sub_dict,
                req_key,
                req_key_value
            )

        if sub_dict:
            temp_dict[parent_key] = sub_dict
        else:
            if temp_parent == req_key:
                temp_dict[parent_key] = req_key_value

    elif isinstance(value, list):
        temp_list, temp_list_dict = [], {}
        sub_list = []
        for value_list in value:
            if isinstance(value_list, dict):
                for sub_dict_key, sub_dict_value in value_list.iteritems():
                    temp_list_dict = recursive_dict_object(
                        sub_dict_key,
                        sub_dict_value,
                        api_call,
                        json_data,
                        data_object,
                        temp_list_dict,
                        req_key,
                        req_key_value
                    )

                temp_list.append(copy.deepcopy(temp_list_dict))
            else:
                _key = re.match('\{(.+?)\}', value_list)
                if _key:
                    _value = json_data.get(_key.group(1))
                    if _value and _value != '':
                        var_type = check_variable_type(
                            api_call,
                            _key.group(1)
                        )
                        if var_type == 'integer':
                            sub_list.append(int(_value.strip()))
                        elif var_type == 'float':
                            sub_list.append(float(_value.strip()))
                        elif var_type == 'boolean':
                            if _value.lower() == 'false':
                                _value = ''
                            sub_list.append(bool(_value.strip()))
                        elif var_type == 'list':
                            _temp_store = []
                            for item in _value.strip().split(','):
                                _temp_store.append(item.strip())

                            sub_list.append(_temp_store)
                        elif var_type == 'text/integer':
                            try:
                                sub_list.append(int(_value.strip()))
                            except:
                                sub_list.append(_value.strip())
                        else:
                            sub_list.append(_value.strip())

        if sub_list:
            temp_dict[str(parent_key)] = sub_list

        if temp_list:
            temp_dict[str(parent_key)] = temp_list

    else:
        if value:
            _pkey = re.match('\{(.+?)\}', parent_key)
            if _pkey:
                _pkey_value = json_data.get(_pkey.group(1))
            else:
                _pkey_value = parent_key

            _key = re.match('\{(.+?)\}', value)
            if _key:
                _value = json_data.get(_key.group(1))
                if _value and _value != '':
                    var_type = check_variable_type(
                        api_call,
                        _key.group(1)
                    )
                    if _value != "null":
                        if var_type == 'integer':
                            temp_dict[str(_pkey_value)] = int(_value.strip())
                        elif var_type == 'float':
                            temp_dict[str(_pkey_value)] = float(_value.strip())
                        elif var_type == 'boolean':
                            if _value.lower() == 'false':
                                _value = ''
                            temp_dict[str(_pkey_value)] = bool(_value.strip())
                        elif var_type == 'list':
                            _temp_store = []
                            for item in _value.strip().split(','):
                                _temp_store.append(item.strip())

                            temp_dict[str(_pkey_value)] = _temp_store
                        elif var_type == 'text/integer':
                            try:
                                temp_dict[str(_pkey_value)] = int(
                                    _value.strip()
                                )
                            except:
                                temp_dict[str(_pkey_value)] = _value.strip()
                        else:
                            temp_dict[str(_pkey_value)] = _value.strip()
                    else:
                        temp_dict[str(_pkey_value)] = None

        if value == 'none' or value is None:
            temp_dict[str(_pkey_value)] = value

    return temp_dict


def process_api_data_request(api_call, json_data):
    data_object = api_call.get('data_object')

    """ Setup the data structure with the appropriate values """
    temp_json = json.loads(data_object)
    temp_dict = {}
    temp_list = []
    req_key = None
    req_key_value = None

    if api_call.get('required_key'):
        req_key = api_call.get('required_key_name')
        if api_call.get('required_key_type') == 'dict':
            req_key_value = {}
        elif api_call.get('required_key_type') == 'list':
            req_key_value = []

    if isinstance(temp_json, dict):
        for key, value in temp_json.iteritems():
            if value:
                temp_dict = recursive_dict_object(
                    key,
                    value,
                    api_call,
                    json_data,
                    temp_json,
                    temp_dict,
                    req_key,
                    req_key_value
                )
            if value is None:
                temp_dict[str(key)] = None

        return temp_dict

    elif isinstance(temp_json, list):
        for item in temp_json:
            if isinstance(item, dict):
                for key, value in item.iteritems():
                    if value:
                        temp_dict = recursive_dict_object(
                            key,
                            value,
                            api_call,
                            json_data,
                            temp_json,
                            temp_dict,
                            req_key,
                            req_key_value
                        )
                    if value is None:
                        temp_dict[str(key)] = None

                temp_list.append(temp_dict)
            else:
                def evaluate_replace(m):
                    if json_data.get(m.group(2)):
                        return re.sub(
                            m.group(1),
                            json_data.get(m.group(2)).strip(),
                            m.group(0)
                        )
                    else:
                        return m.group(1)

                value = re.sub('(\{(.+?)\})', evaluate_replace, item)
                temp_list.append(value)

        return temp_list


def create_custom_header(api_call, request):
    def evaluate_replace(m):
        return re.sub(m.group(1), request.get(m.group(2)), m.group(0))

    header = {}
    if not api_call.get('remove_content_type'):
        header['Content-Type'] = 'application/json'

    if not api_call.get('remove_token'):
        header['X-Auth-Token'] = request.get('api_token')

    if request.get('mock') and not api_call.get('remove_token'):
        header['X-Auth-Token'] = '{api-token}'

    if (
        api_call.get('change_content_type') and
        api_call.get('custom_content_type') is not None
    ):
        header['Content-Type'] = api_call.get('custom_content_type')

    if api_call.get('add_to_header'):
        temp_value = api_call.get('custom_header_value')
        key_value = re.sub('(\{(.+?)\})', evaluate_replace, temp_value)
        header[api_call.get('custom_header_key')] = key_value.strip()

    return header


def process_api_request(url, verb, data, headers, html_convert=True):
    try:
        if data:
            response = getattr(requests, verb.lower())(
                url,
                headers=headers,
                data=json.dumps(data),
                verify=False
            )
        else:
            response = getattr(requests, verb.lower())(
                url,
                headers=headers,
                verify=False
            )
    except Exception as e:
        return (
            headers,
            (
                "<span class='error-response'>An error occured "
                "with the request. Details are below</span>"
            ),
            str(e.message), ''
        )

    try:
        response_headers = json.loads(response.headers)
    except:
        response_headers = dict(response.headers)

    try:
        content_type = response_headers.get('content-type').split(';')
    except:
        content_type = []

    try:
        if (
            'application/xml' in content_type or
            'application/atom+xml' in content_type
        ):
            if html_convert:
                content = pretty_format_data(response.content, True)
            else:
                content = response.content
        else:
            if html_convert:
                content = pretty_format_data(json.loads(response.content))
            else:
                content = json.loads(response.content)
    except:
        temp = re.findall('<body>(.+?)<\/body>', response.content, re.S)
        if temp:
            formatted_content = re.sub(
                '\n|\r|\s\s+?|<br \/>|<h1>',
                '',
                temp[0]
            )
            content = re.sub('<\/h1>', '<br />', formatted_content)
        elif len(response.text) > 5:
            content = "%s Status Code: %s" % (
                str(response.text),
                str(response.status_code)
            )
        else:
            content = "No content recieved. Status Code: %s" % str(
                response.status_code
            )

    if html_convert:
        headers = pretty_format_data(headers)
        response_headers = pretty_format_data(response_headers)

    return headers, response_headers, content, response.status_code


def pretty_format_data(data, content_type=False):
    if data:
        if content_type:
            return highlight(data, XmlLexer(), HtmlFormatter())
        else:
            return highlight(
                json.dumps(data, indent=4),
                JsonLexer(),
                HtmlFormatter()
            )


def pretty_format_url(url):
    if url:
        temp_url = '<pre><span class="nt">%s</span></pre>' % url
        temp_url = re.sub('{', '<span class="s2">{', temp_url)
        temp_url = re.sub('}', '}</span>', temp_url)
        return temp_url


def log_api_call_request(
    req_headers,
    rep_headers,
    rep_body,
    rep_code,
    call,
    request,
    data_package,
    api_url,
    title
):
    if not request.get('api_verb') in ['PUT', 'POST', 'DELETE']:
        rep_body = None

    if data_package:
        data_package = process_api_data_request(
            call,
            sanitize_data_for_mongo(request)
        )
    try:
        g.db.history.insert(
            {
                'response': {
                    'code': rep_code,
                    'headers': rep_headers,
                    'body': rep_body
                },
                'request': {
                    'verb': request.get('api_verb'),
                    'url': api_url,
                    'data': data_package
                },
                'details': {
                    'id': call.get('_id'),
                    'title': call.get('title'),
                    'description': call.get('short_description'),
                    'doc_url': call.get('doc_url')
                },
                'ddi': request.get('ddi'),
                'data_center': request.get('region'),
                'username': session.get('username'),
                'completed_at': get_timestamp(),
                'product': title
            }
        )
    except:
        pass

    return


def sanitize_data_for_mongo(data):
    temp_dict = {}
    for k, v in data.iteritems():
        temp_dict[k] = re.sub('\.', '&#46;', v)

    return temp_dict


def gather_history():
    history = []
    history = g.db.history.find(
        {
            'username': session.get('username')
        }
    ).sort('completed_at', pymongo.DESCENDING).limit(100)

    return history


def gather_favorites(only_ids=False):
    favorites = []
    user_favorites = g.db.favorites.find_one(
        {
            'username': session.get('username')
        }
    )
    if user_favorites:
        for call in user_favorites.get('favorites'):
            query = {'_id': ObjectId(call.get('call_id'))}
            temp_call = getattr(g.db, call.get('db_name')).find_one(query)
            if temp_call:
                if only_ids:
                    favorites.append(call.get('call_id'))
                else:
                    temp_call['product-db_name'] = call.get('db_name')
                    temp_call['product-app_url'] = call.get('app_url')
                    favorites.append(temp_call)

    return favorites
