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

from operator import itemgetter, attrgetter
from unicodedata import normalize
from flask import g, current_app, session
from bson.objectid import ObjectId
from dateutil import parser, tz
from datetime import timedelta


import re
import forms
import requests
import json
import datetime


def get_and_sort(items, *args):
    if items:
        return sorted(items, key=itemgetter(*args))


def generate_parent_menu(menu):
    parent_menus = ['']
    for item in menu:
        if not (item.get('parent') in parent_menus):
            parent_menus.append(item.get('parent'))
    parent_menus.append('Add New Parent')
    return parent_menus


def generate_active_roles(roles):
    active_roles = []
    for role in roles:
        if role.get('active'):
            active_roles.append(role.get('display_name'))
    return active_roles


def slug(string):
    temp = re.sub(' +', ' ', string.lower())
    return re.sub(' ', '_', temp)


def unslug(string):
    return re.sub('_', ' ', string.title())


def normalize(string):
    return re.sub('\s+', ' ', string)


def generate_multi_dict(choices):
    choices = re.sub('\r\n', ',', choices)
    temp = choices.split(',')
    return [(i, i) for i in temp]


def sanitize_route(route):
    temp = re.sub('<', '', str(route))
    temp = re.sub('>', '', temp)
    return str(temp)


def get_next_order_number(menu_list, parent_menu):
    last_order_number = 1
    for item in menu_list:
        if item.get('parent') == parent_menu:
            last_order_number = (int(item.get('order')) + 1)
    return last_order_number


def get_parent_order(parent_menu, settings, name):
    last, duplicate = 0, False
    if settings.get('top_level_menu'):
        menu_list = sorted(
            settings.get('top_level_menu'),
            key=itemgetter('order')
        )
        for item in menu_list:
            if item.get('order') > last:
                last = item.get('order')
            if parent_menu:
                if item.get('slug') == slug(normalize(parent_menu)):
                    return item.get('order')
            elif item.get('slug') == slug(normalize(name)):
                return item.get('order')

    if parent_menu:
        to_add = normalize(parent_menu)
    else:
        to_add = normalize(name)

    if not g.db.settings.find_one(
        {
            'top_level_menu.slug': slug(to_add)
        }
    ):
        g.db.settings.update(
            {
                '_id': settings.get('_id')
            }, {
                '$push': {
                    'top_level_menu': {
                        'name': to_add,
                        'order': (last + 1),
                        'slug': slug(to_add)
                    }
                }
            }
        )
    return (last + 1)


def generate_dynamic_form(routes, role):
    settings = g.db.settings.find_one(
        {
            'roles.name': role
        }
    )
    current_perms = []
    for role_item in settings.get('roles'):
        if role_item.get('name') == role:
            current_perms = role_item.get('perms')

    class F(forms.ManagePermissions):
        pass

    ordered = []
    admin = []
    for route in routes:
        if not re.search('\:|\/admin', str(route)):
            ordered.append(str(route))
        elif re.search('\/admin', str(route)):
            admin.append(str(route))

    for route in sorted(ordered):
        if current_perms:
            if str(route) in current_perms:
                setattr(
                    F,
                    str(route),
                    forms.fields.BooleanField(
                        sanitize_route(route),
                        default='y'
                    )
                )
            else:
                setattr(
                    F,
                    str(route),
                    forms.fields.BooleanField(
                        sanitize_route(route)
                    )
                )
        else:
            setattr(
                F,
                str(route),
                forms.fields.BooleanField(
                    sanitize_route(route)
                )
            )
    setattr(
        F,
        'admin',
        forms.fields.TextField('Admin')
    )

    for route in sorted(admin):
        if not re.search('\:', str(route)):
            if current_perms:
                if str(route) in current_perms:
                    setattr(
                        F,
                        str(route),
                        forms.fields.BooleanField(
                            sanitize_route(route),
                            default='y'
                        )
                    )
                else:
                    setattr(
                        F,
                        str(route),
                        forms.fields.BooleanField(
                            sanitize_route(route)
                        )
                    )
            else:
                setattr(
                    F,
                    str(route),
                    forms.fields.BooleanField(
                        sanitize_route(route)
                    )
                )
    setattr(
        F,
        'submit',
        forms.fields.SubmitField('Set Permissions')
    )
    return F()


def evaluate_permissions(submissions):
    perm_data = []
    for key, answer in submissions:
        if not (key == 'csrf_token' or key == 'submit'):
            if answer[0] == 'y':
                perm_data.append(key)

    return perm_data


def change_top_level_order(settings, new_position, old_position, menu_item):
    menu_item = slug(menu_item)
    for menu in settings.get('menu'):
        if menu.get('parent_order') == new_position:
            g.db.settings.update(
                {
                    'menu.name': menu.get('name')
                }, {
                    '$set': {
                        'menu.$.parent_order': old_position
                    }
                }
            )
        if menu.get('parent') and menu.get('parent') != '':
            if slug(menu.get('parent')) == menu_item:
                g.db.settings.update(
                    {
                        'menu.name': menu.get('name')
                    }, {
                        '$set': {
                            'menu.$.parent_order': new_position
                        }
                    }
                )
        elif slug(menu.get('display_name')) == menu_item:
            g.db.settings.update(
                {
                    'menu.name': menu.get('name')
                }, {
                    '$set': {
                        'menu.$.parent_order': new_position
                    }
                }
            )
    return


def check_top_level_to_remove(menu_item):
    settings = g.db.settings.find_one()
    deleted, found = False, False
    if menu_item.get('parent') and menu_item.get('parent') != "":
        for item in settings.get('menu'):
            if item.get('parent') == menu_item.get('parent'):
                found = True
        if not found:
            to_delete = slug(menu_item.get('parent'))
    else:
        to_delete = slug(menu_item.get('display_name'))

    if not found:
        deleted = True
        g.db.settings.update(
            {
            }, {
                '$pull': {
                    'top_level_menu': {
                        'slug': to_delete
                    }
                }
            }
        )

    if deleted:
        settings = g.db.settings.find_one()
        for top_level in \
                get_and_sort(settings.get('top_level_menu'), 'order'):
            if menu_item.get('parent_order') < top_level.get('order'):
                g.db.settings.update(
                    {
                        'top_level_menu.slug': top_level.get('slug')
                    }, {
                        '$inc': {
                            'top_level_menu.$.order': -1
                        }
                    }
                )
                count = g.db.settings.find(
                    {
                        'menu.parent': top_level.get('slug')
                    }
                ).count()
                if count > 0:
                    for menu_element in settings.get('menu'):
                        if menu_element.get('parent') == top_level.get('slug'):
                            g.db.settings.update(
                                {
                                    'menu.name': menu_element.get('name')
                                }, {
                                    '$inc': {
                                        'menu.$.parent_order': -1
                                    }
                                }
                            )
                else:
                    g.db.settings.update(
                        {
                            'menu.name': top_level.get('slug'),
                        }, {
                            '$inc': {
                                'menu.$.parent_order': -1
                            }
                        }
                    )
    return


"""
    Custom forms helper functions
"""


def deploy_custom_form(form_name, **args):
    class F(forms.BaseForm):
        pass

    form = g.db.forms.find_one({'name': form_name})
    if form:
        if not form.get('fields'):
            return F()

        for field in get_and_sort(form.get('fields'), 'order'):
            if field.get('active'):
                method = getattr(forms.fields, field.get('field_type'))
                choices, default = None, None
                if field.get('default_value'):
                    default = field.get('default_value')

                # Args for edit override original default to set correct value
                if args.get(field.get('name')):
                    default = args.get(field.get('name'))

                if field.get('field_choices'):
                    choices = generate_multi_dict(
                        field.get('field_choices')
                    )

                if (
                    field.get('field_type') != "SelectField" and
                    field.get('field_type') != "RadioField" and
                    field.get('field_type') != "SelectMultipleField"
                ):
                    if field.get('required'):
                        setattr(
                            F,
                            field.get('name'),
                            method(
                                field.get('label'),
                                validators=[
                                    forms.validators.required()
                                ],
                                default=default,
                                description=field.get('description')
                            )
                        )
                    else:
                        setattr(
                            F,
                            field.get('name'),
                            method(
                                field.get('label'),
                                default=default,
                                description=field.get('description')
                            )
                        )

                else:
                    if choices:
                        if field.get('required'):
                            setattr(
                                F,
                                field.get('name'),
                                method(
                                    field.get('label'),
                                    validators=[
                                        forms.validators.required()
                                    ],
                                    choices=choices,
                                    default=default,
                                    description=field.get('description')
                                )
                            )
                        else:
                            setattr(
                                F,
                                field.get('name'),
                                method(
                                    field.get('label'),
                                    choices=choices,
                                    default=default,
                                    description=field.get('description')
                                )
                            )
                    else:
                        if field.get('required'):
                            setattr(
                                F,
                                field.get('name'),
                                method(
                                    field.get('label'),
                                    validators=[
                                        forms.validators.required()
                                    ],
                                    default=default,
                                    description=field.get('description')
                                )
                            )
                        else:
                            setattr(
                                F,
                                field.get('name'),
                                method(
                                    field.get('label'),
                                    default=default,
                                    description=field.get('description')
                                )
                            )
    return F()


def get_form_field_order(form_id):
    last_order_number = 1
    form = g.db.forms.find_one({'_id': ObjectId(form_id)})
    if form.get('fields'):
        for item in form.get('fields'):
            if item.get('order') >= last_order_number:
                last_order_number = (int(item.get('order')) + 1)
    return last_order_number


def reorder_fields(form_id, form_fields, field_name):
    fields = get_and_sort(form_fields.get('fields'), 'order')
    found = 0
    if len(fields) > 1:
        for field in fields:
            if field.get('name') == field_name:
                found = 1
            elif found == 1:
                g.db.forms.update(
                    {
                        '_id': ObjectId(form_id),
                        'fields.name': field.get('name')
                    }, {
                        '$inc': {
                            'fields.$.order': -1
                        }
                    }
                )


def process_auth_request(data):
    auth_url = 'https://identity.api.rackspacecloud.com/v2.0/tokens'
    auth_header = {
        'Content-Type': 'application/json',
    }
    response = getattr(requests, 'post')(
        auth_url,
        headers=auth_header,
        data=json.dumps(data)
    )
    response_headers = dict(response.headers)
    content = json.loads(response.content)

    if content:
        if content.get('access'):
            access_data_token = content.get('access').get('token')
            if access_data_token:
                token = access_data_token.get('id')
                account_number = access_data_token.get('tenant').get('id')
                expiration = access_data_token.get('expires')
                return token, account_number, expiration

    raise('Authentication Failed')


def cloud_authenticate(request):
    from pitchfork import app

    def remove_micro(expire_date):
        return expire_date - datetime.timedelta(
            microseconds=expire_date.microsecond
        )

    def find_deltas(expire_date):
        now = datetime.datetime.now(tz.tzutc())
        return expire_date - remove_micro(now)

    username = request.form.get('username')
    password = request.form.get('password')
    auth_data = {
        'auth': {
            'RAX-KSKEY:apiKeyCredentials': {
                'username': username,
                'apiKey': password
            }
        }
    }
    try:
        session['cloud_token'], session['ddi'], \
            expiration = process_auth_request(auth_data)
        session.permanent = True
        if expiration:
            expiration = parser.parse(expiration)
            app.permanent_session_lifetime = find_deltas(expiration)

    except:
        return False
    else:
        session['username'] = username
        return True
