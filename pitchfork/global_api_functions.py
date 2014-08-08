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

from flask import g, session, current_app
from dateutil import tz


import re
import requests
import json
import global_forms
import pymongo
import datetime


UTC = tz.tzutc()


def get_timestamp():
    return datetime.datetime.now(UTC)


def check_url_endpoints(us, uk):
    us_find = re.findall('\{(.+?)\}', us)
    uk_find = re.findall('\{(.+?)\}', uk)
    if 'data_center' in us_find:
        return False

    if 'data_center' in uk_find:
        return False

    return True


def add_fields_to_form(count):
    class F(global_forms.ApiCall):
        pass

    for i in range(count):
        setattr(
            F,
            'variable_%i' % i,
            global_forms.FormField(global_forms.CallVariables)
        )

    setattr(
        F,
        'submit',
        global_forms.SubmitField('Submit')
    )
    return F()


def get_vars_for_call(submissions):
    data = []
    count = []

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
        variable.pop('ignore', None)
        if variable.get('variable_name') or \
                variable.get('variable_name') != '':
            return_data.append(variable)

    return return_data


def process_api_url(url, request):
    """ Regex loop to replace the URL with the needed values """

    def evaluate_replace(m):
        return re.sub(
            m.group(1),
            request.json.get(m.group(2)).strip(),
            m.group(0)
        )

    api_url = re.sub('(\{(.+?)\})', evaluate_replace, url)

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
        temp_list = {}
        sub_list = []
        for value_list in value:
            if isinstance(value_list, dict):
                for sub_dict_key, sub_dict_value in value_list.iteritems():
                    temp_list = recursive_dict_object(
                        sub_dict_key,
                        sub_dict_value,
                        api_call,
                        json_data,
                        data_object,
                        temp_list,
                        req_key,
                        req_key_value
                    )
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
                        else:
                            sub_list.append(_value.strip())

        if sub_list:
            temp_dict[str(parent_key)] = sub_list

        if temp_list:
            temp_dict[str(parent_key)] = [temp_list]

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

        return temp_list


def create_custom_header(api_call, request):
    def evaluate_replace(m):
        return re.sub(m.group(1), request.get(m.group(2)), m.group(0))

    header = {}
    if not api_call.get('remove_content_type'):
        header['Content-Type'] = 'application/json'

    if not api_call.get('remove_token'):
        header['X-Auth-Token'] = session.get('cloud_token')

    if request.get('mock') and not request.get('api_token'):
        header['X-Auth-Token'] = '{api-token}'

    if api_call.get('add_to_header'):
        temp_value = api_call.get('custom_header_value')
        key_value = re.sub('(\{(.+?)\})', evaluate_replace, temp_value)
        header[api_call.get('custom_header_key')] = key_value.strip()

    return header


def process_api_request(url, verb, data, headers):
    try:
        if data:
            response = getattr(requests, verb.lower())(
                url,
                headers=headers,
                data=json.dumps(data)
            )
        else:
            response = getattr(requests, verb.lower())(
                url,
                headers=headers
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
            content = response.content
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
        else:
            content = "No content recieved. Status Code: %s" % str(
                response.status_code
            )

    return headers, response_headers, content, response.status_code


def front_page_most_accessed(active_products):
    temp_products = []
    if active_products:
        for product in active_products:
            product_accessed = getattr(g.db, product).find(
                {
                    'tested': True
                }
            ).sort('accessed', pymongo.DESCENDING).limit(2)
            product_details = g.db.api_settings.find_one({}, {product: 1})
            for call in product_accessed:
                call['app_link'] = product_details.get(product).get('app_url')
                call['endpoint'] = product_details.get(product).get('us_api')
                call['prod_title'] = product_details.get(product).get('title')
                temp_products.append(call)

        sorted_products = reversed(
            sorted(
                temp_products,
                key=lambda k: k.get('accessed')
            )
        )
        return sorted_products
    else:
        return []


def search_for_calls(search_string):
    data = []
    api_settings = g.db.api_settings.find_one()
    if api_settings:
        products = api_settings.get('active_products')
        if len(products) > 0:
            for product in products:
                product_details = g.db.api_settings.find_one({}, {product: 1})
                search_results = getattr(g.db, product).find(
                    {
                        'tested': True,
                        '$or': [
                            {
                                'title': {
                                    '$regex': search_string,
                                    '$options': 'i'
                                }
                            }, {
                                'short_description': {
                                    '$regex': search_string,
                                    '$options': 'i'
                                }
                            }
                        ]
                    }
                ).limit(3)

                for item in search_results:
                    item['app_link'] = product_details.get(product).get(
                        'app_url'
                    )
                    item['endpoint'] = product_details.get(product).get(
                        'us_api'
                    )
                    item['prod_title'] = product_details.get(product).get(
                        'title'
                    )
                    item['_id'] = str(item.get('_id'))
                    data.append(item)
        else:
            return 'No Active Products to Search'
    else:
        return 'No Results Found'

    return data


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
            'data_center': request.get('data_center'),
            'username': session.get('username'),
            'completed_at': get_timestamp(),
            'product': title
        }
    )
    return


def gather_history():
    history = []
    username = session.get('username')

    history = g.db.history.find(
        {
            'username': session.get('username')
        }
    ).sort('completed_at', pymongo.DESCENDING).limit(20)

    return history
