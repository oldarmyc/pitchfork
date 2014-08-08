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

from flask import render_template, redirect, url_for, request
from flask import flash, g, current_app, jsonify
from bson.objectid import ObjectId


import pymongo
import json
import requests
import pitchfork.global_forms as global_forms
import pitchfork.global_api_functions as globe


from . import bp, check_perms, COLLECTION, BLUEPRINT, URL_LINK, TITLE


"""
    Variables Explained:

    COLLECTION = Name of DB Collection (Used in all mongo calls)
    BLUEPRINT = Name of BP (Used in redirects)
    URL_LINK = Name of URL prefix
    TITLE = Title for the specified product

"""


@bp.route('/')
@check_perms(request)
def product():
    testing, restrict_dcs, require_dc = False, False, None
    tab_title = "%s API" % TITLE
    title = TITLE
    api_process = "/%s/api_call/process" % URL_LINK
    api_calls = getattr(g.db, COLLECTION).find(
        {
            'tested': True
        }
    ).sort(
        [
            ('accessed', pymongo.DESCENDING),
            ('title', pymongo.ASCENDING)
        ]
    )
    api_settings = g.db.api_settings.find_one()
    if api_settings:
        data_centers = api_settings.get('dcs')
        api_settings = api_settings.get(COLLECTION)
        require_dc = api_settings.get('require_dc')
        if require_dc:
            restrict_dcs = globe.check_url_endpoints(
                api_settings.get('us_api'),
                api_settings.get('uk_api')
            )
            if restrict_dcs:
                data_centers = [
                    {'abbreviation': 'US'},
                    {'abbreviation': 'UK'}
                ]
    else:
        data_centers = []
        api_settings = {}
    return render_template(
        'product_front.html',
        api_calls=api_calls,
        api_settings=api_settings,
        data_centers=data_centers,
        tab_title=tab_title,
        title=title,
        api_process=api_process,
        testing=testing,
        require_dc=bool(require_dc),
        restrict_dcs=restrict_dcs
    )


@bp.route('/testing')
@check_perms(request)
def product_testing():
    testing, restrict_dcs, require_dc = True, False, None
    tab_title = "%s API" % TITLE
    title = TITLE
    api_process = "/%s/api_call/process" % URL_LINK
    api_calls = getattr(g.db, COLLECTION).find(
        {
            '$or': [
                {'tested': False},
                {'tested': None}
            ]
        }
    ).sort(
        [
            ('accessed', pymongo.DESCENDING),
            ('title', pymongo.ASCENDING)
        ]
    )
    api_settings = g.db.api_settings.find_one()
    if api_settings:
        data_centers = api_settings.get('dcs')
        api_settings = api_settings.get(COLLECTION)
        require_dc = api_settings.get('require_dc')
        if require_dc:
            restrict_dcs = globe.check_url_endpoints(
                api_settings.get('us_api'),
                api_settings.get('uk_api')
            )
            if restrict_dcs:
                data_centers = [
                    {'abbreviation': 'US'},
                    {'abbreviation': 'UK'}
                ]
    else:
        data_centers = []
        api_settings = {}
    return render_template(
        'product_front.html',
        api_calls=api_calls,
        api_settings=api_settings,
        data_centers=data_centers,
        tab_title=tab_title,
        title=title,
        api_process=api_process,
        testing=testing,
        require_dc=bool(require_dc),
        restrict_dcs=restrict_dcs
    )


@bp.route('/manage', methods=['GET', 'POST'])
@check_perms(request)
def product_manage():
    error = True
    title = "%s Manage Settings" % TITLE
    api_settings = g.db.api_settings.find_one()
    post_url = "/%s/manage" % URL_LINK
    if api_settings:
        if api_settings.get(COLLECTION):
            product_settings = api_settings.get(COLLECTION)
            form = global_forms.ManageProduct(
                url=api_settings.get(COLLECTION).get('us_api'),
                uk_url=api_settings.get(COLLECTION).get('uk_api'),
                doc_url=api_settings.get(COLLECTION).get('doc_url'),
                active=api_settings.get(COLLECTION).get('active'),
                require_dc=api_settings.get(COLLECTION).get('require_dc'),
                title=api_settings.get(COLLECTION).get('title'),
                app_url=api_settings.get(COLLECTION).get('app_url')
            )
        else:
            form = global_forms.ManageProduct()
            product_settings = []
    else:
        form = global_forms.ManageProduct()
        product_settings = []

    if request.method == 'POST' and form.validate_on_submit():
        active = bool(request.form.get('active'))
        require_dc = bool(request.form.get('require_dc'))
        if api_settings:
            g.db.api_settings.update(
                {
                    '_id': api_settings.get('_id')
                }, {
                    '$set': {
                        COLLECTION: {
                            'us_api': request.form.get('url'),
                            'uk_api': request.form.get('uk_url'),
                            'doc_url': request.form.get('doc_url'),
                            'active': active,
                            'require_dc': require_dc,
                            'app_url': request.form.get('app_url'),
                            'title': request.form.get('title')
                        }
                    }
                }
            )
            message = "Product variables successfully updated"

        active_products = api_settings.get('active_products')
        if active_products:
            if active:
                if COLLECTION not in active_products:
                    g.db.api_settings.update(
                        {
                            '_id': api_settings.get('_id')
                        }, {
                            '$push': {
                                'active_products': COLLECTION
                            }
                        }
                    )
            else:
                if COLLECTION in active_products:
                    g.db.api_settings.update(
                        {
                            '_id': api_settings.get('_id')
                        }, {
                            '$pull': {
                                'active_products': COLLECTION
                            }
                        }
                    )
        else:
            if active:
                g.db.api_settings.update(
                    {
                        '_id': api_settings.get('_id')
                    }, {
                        '$set': {
                            'active_products': [
                                COLLECTION
                            ]
                        }
                    }
                )

        flash(message)
        return redirect(url_for('%s.product_manage' % BLUEPRINT))

    elif request.method == 'POST' and not form.validate_on_submit():
        flash('Form validation error, please check the form and try again')
        return render_template(
            'manage_product.html',
            title=title,
            form=form,
            product_settings=product_settings,
            post_url=post_url,
            error=error
        )
    else:
        return render_template(
            'manage_product.html',
            title=title,
            form=form,
            product_settings=product_settings,
            post_url=post_url
        )


@bp.route('/manage/api', methods=['GET', 'POST'])
@check_perms(request)
def manage_api():
    title = "Manage API Calls"
    product_url = "/%s/manage/api" % URL_LINK
    api_commands = getattr(g.db, COLLECTION).find().sort(
        'tested', pymongo.DESCENDING
    )
    return render_template(
        'manage_api_calls.html',
        title=title,
        api_commands=api_commands,
        product_url=product_url
    )


@bp.route('/manage/api/add', methods=['GET', 'POST'])
@bp.route('/manage/api/edit/<api_id>', methods=['GET', 'POST'])
@check_perms(request)
def add_edit_api(api_id=None):
    error = True
    edit = False
    cancel = "/%s/manage/api" % URL_LINK
    api_settings = g.db.api_settings.find_one()
    api_commands = getattr(g.db, COLLECTION).find()
    if api_id:
        edit = True
        api_call = getattr(g.db, COLLECTION).find_one(
            {
                '_id': ObjectId(api_id)
            }
        )
        title = "Edit API Call %s" % api_call.get('title')
        post_url = "/%s/manage/api/edit/%s" % (URL_LINK, api_id)
        form = global_forms.ApiCall()
        count = len(api_call.get('variables'))
        if count > 0:
            form = globe.add_fields_to_form(count)
            for i in range(count):
                temp = getattr(form, 'variable_%i' % i)
                current_var = api_call.get('variables')[i]
                temp.form.field_type.data = current_var.get('field_type')
                temp.form.required.data = current_var.get('required')
                temp.form.description.data = current_var.get('description')
                temp.form.variable_name.data = current_var.get(
                    'variable_name'
                )
                temp.form.field_display.data = current_var.get(
                    'field_display'
                )
                temp.form.field_display_data.data = current_var.get(
                    'field_display_data'
                )
                temp.form.id_value.data = i
        else:
            form = globe.add_fields_to_form(1)

        form.title.data = api_call.get('title')
        form.verb.data = api_call.get('verb')
        form.api_uri.data = api_call.get('api_uri')
        form.short_description.data = api_call.get('short_description')
        form.use_data.data = bool(api_call.get('use_data'))
        form.data_object.data = api_call.get('data_object')
        form.doc_url.data = api_call.get('doc_url')
        form.tested.data = bool(api_call.get('tested'))
        form.remove_token.data = bool(api_call.get('remove_token'))
        form.remove_content_type.data = bool(
            api_call.get('remove_content_type')
        )
        form.required_key.data = bool(api_call.get('required_key'))
        form.required_key_name.data = api_call.get('required_key_name')
        form.required_key_type.data = api_call.get('required_key_type', '')
        form.add_to_header.data = bool(api_call.get('add_to_header'))
        form.custom_header_key.data = api_call.get('custom_header_key')
        form.custom_header_value.data = api_call.get('custom_header_value')

    else:
        title = "Add API Call"
        post_url = "/%s/manage/api/add" % URL_LINK
        count = 1
        form = globe.add_fields_to_form(count)
        for i in range(count):
            temp = getattr(form, 'variable_%i' % i)
            temp.form.id_value.data = i

    form.verb.choices = [
        (verb.get('name'), verb.get('name'))
        for verb in api_settings.get('verbs')
    ]
    if request.method == 'POST' and form.validate_on_submit():
        cust_header_key, cust_header_value = '', ''
        title = request.form.get('title').lower().title()
        api_uri = request.form.get('api_uri')
        verb = request.form.get('verb')
        short_description = request.form.get('short_description')
        if request.form.get('custom_header_key'):
            cust_header_key = request.form.get('custom_header_key').strip()

        if request.form.get('custom_header_value'):
            cust_header_value = request.form.get('custom_header_value').strip()

        variables = globe.get_vars_for_call(list(request.form.iterlists()))
        temp_title = getattr(g.db, COLLECTION).find_one({'title': title})
        if temp_title:
            if api_id is None or (
                api_id and temp_title.get('title') != api_call.get('title')
            ):
                flash(
                    'Duplicate title for API call already exists'
                    ', please check the name and try again'
                )
                return render_template(
                    'api_call_add_edit.html',
                    title=title,
                    form=form,
                    api_commands=api_commands,
                    edit=edit,
                    post_url=post_url,
                    cancel=cancel,
                    error=error
                )

        temp_url = getattr(g.db, COLLECTION).find_one(
            {
                'api_uri': api_uri,
                'verb': verb,
                'data_object': request.form.get('data_object')
            }
        )
        if temp_url:
            if (
                (
                    api_id and
                    temp_url.get('api_uri') != api_call.get('api_uri')
                ) or (
                    temp_url and api_id is None
                )
            ):
                flash(
                    'Duplicate API URI and Verb combination already exists, '
                    'please check the URI and verb and try again'
                )
                return render_template(
                    'api_call_add_edit.html',
                    title=title,
                    form=form,
                    api_commands=api_commands,
                    edit=edit,
                    post_url=post_url,
                    cancel=cancel,
                    error=error
                )

        if api_id:
            getattr(g.db, COLLECTION).update(
                {
                    '_id': ObjectId(api_id)
                }, {
                    '$set': {
                        'title': title,
                        'verb': verb,
                        'api_uri': api_uri,
                        'short_description': short_description,
                        'variables': variables,
                        'use_data': bool(request.form.get('use_data')),
                        'data_object': request.form.get('data_object'),
                        'doc_url': request.form.get('doc_url'),
                        'tested': bool(request.form.get('tested')),
                        'remove_token': bool(
                            request.form.get('remove_token')
                        ),
                        'remove_content_type': bool(
                            request.form.get('remove_content_type')
                        ),
                        'required_key': bool(
                            request.form.get('required_key')
                        ),
                        'required_key_name': request.form.get(
                            'required_key_name'
                        ),
                        'required_key_type': request.form.get(
                            'required_key_type'
                        ),
                        'add_to_header': bool(
                            request.form.get('add_to_header')
                        ),
                        'custom_header_key': cust_header_key,
                        'custom_header_value': cust_header_value
                    }
                }
            )
            message = "API Call was successfully updated"
        else:
            getattr(g.db, COLLECTION).insert(
                {
                    'title': title,
                    'verb': verb,
                    'api_uri': api_uri,
                    'short_description': short_description,
                    'variables': variables,
                    'use_data': bool(request.form.get('use_data')),
                    'data_object': request.form.get('data_object'),
                    'doc_url': request.form.get('doc_url'),
                    'remove_token': bool(
                        request.form.get('remove_token')
                    ),
                    'remove_content_type': bool(
                        request.form.get('remove_content_type')
                    ),
                    'required_key': bool(
                        request.form.get('required_key')
                    ),
                    'required_key_name': request.form.get(
                        'required_key_name'
                    ),
                    'required_key_type': request.form.get(
                        'required_key_type'
                    ),
                    'add_to_header': bool(request.form.get('add_to_header')),
                    'custom_header_key': request.form.get(
                        'custom_header_key'
                    ),
                    'custom_header_value': request.form.get(
                        'custom_header_value'
                    )
                }
            )
            message = "API Call was successfully added"

        flash(message)
        return redirect(url_for('%s.manage_api' % BLUEPRINT))
    elif request.method == 'POST' and not form.validate_on_submit():
        flash('Form validation error, please check the form and try again')
        return render_template(
            'api_call_add_edit.html',
            title=title,
            form=form,
            api_commands=api_commands,
            count=count,
            edit=edit,
            post_url=post_url,
            cancel=cancel,
            error=error
        )
    else:
        return render_template(
            'api_call_add_edit.html',
            title=title,
            form=form,
            api_commands=api_commands,
            count=count,
            edit=edit,
            post_url=post_url,
            cancel=cancel,
        )


@bp.route('/manage/api/test/<action>/<api_id>')
@check_perms(request)
def toggle_api_call(action, api_id):
    toggle_val = None
    api_call = getattr(g.db, COLLECTION).find_one({'_id': ObjectId(api_id)})
    if api_call:
        if action == 'confirm':
            toggle_val = True
            message = "API Call has been mark as tested"
        elif action == 'unconfirm':
            toggle_val = False
            message = "API Call has been mark as untested"

        if toggle_val is not None:
            getattr(g.db, COLLECTION).update(
                {
                    '_id': ObjectId(api_id)
                }, {
                    '$set': {
                        'tested': toggle_val
                    }
                }
            )
        flash(message)
    return redirect(url_for('%s.manage_api' % BLUEPRINT))


@bp.route('/manage/api/delete/<api_id>', methods=['GET', 'POST'])
@check_perms(request)
def delete_api_call(api_id):
    api_call = getattr(g.db, COLLECTION).find_one({'_id': ObjectId(api_id)})
    if api_call:
        getattr(g.db, COLLECTION).remove({'_id': ObjectId(api_id)})
        message = "API call removed successfully"
    else:
        message = "API call was not found and nothing removed"
    flash(message)
    return redirect(url_for('%s.manage_api' % BLUEPRINT))


@bp.route('/api_call/process', methods=['POST'])
@check_perms(request)
def api_call_execute():
    data_package = None
    api_settings = g.db.api_settings.find_one()
    product_settings = api_settings.get(COLLECTION)
    data_center = request.json.get('data_center')
    if data_center == 'uk' or data_center == 'lon':
        dc_url = product_settings.get('uk_api')
    else:
        dc_url = product_settings.get('us_api')

    temp_url = "%s%s" % (
        dc_url,
        request.json.get('api_url')
    )

    if not request.json.get('testing'):
        api_call = getattr(g.db, COLLECTION).find_and_modify(
            query={
                '_id': ObjectId(request.json.get('api_id'))
            },
            update={
                '$inc': {
                    'accessed': 1
                }
            }
        )
    else:
        api_call = getattr(g.db, COLLECTION).find_one(
            {
                '_id': ObjectId(request.json.get('api_id'))
            }
        )

    api_url = globe.process_api_url(temp_url, request)

    """ Process data structure if there is one provided in the setup """
    if api_call.get('use_data'):
        data_package = globe.process_api_data_request(api_call, request.json)

    header = globe.create_custom_header(api_call, request.json)

    """ Send off the request and retrieve the data elements """
    request_headers, response_headers, \
        response_body, response_code = globe.process_api_request(
            api_url,
            request.json.get('api_verb'),
            data_package,
            header
        )

    if not request.json.get('testing'):
        globe.log_api_call_request(
            request_headers,
            response_headers,
            response_body,
            response_code,
            api_call,
            request.json,
            data_package,
            api_url,
            product_settings.get('title')
        )

    """ Send the data structure back to the browser """
    return jsonify(
        request_headers=request_headers,
        response_headers=response_headers,
        response_body=response_body,
        response_code=response_code,
        api_url=api_url,
        data_package=data_package
    )
