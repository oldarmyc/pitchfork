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

from flask import Blueprint, Flask, request, session, redirect, \
    url_for, render_template, flash, jsonify, g, current_app
from . import bp


import pymongo
import forms
import helpers as help
import json
import permissions


from urllib import unquote
from decorators import check_perms
from defaults import check_and_initialize
from bson.objectid import ObjectId


@bp.route('/settings/general', methods=['GET', 'POST'])
@check_perms(request)
def general_settings():
    error = True
    settings = check_and_initialize()
    title = "Application Settings"
    form = help.deploy_custom_form(
        'application_settings',
        application_title=settings.get('application_title'),
        application_email=settings.get('application_email'),
        application_footer=settings.get('application_footer'),
        application_well=settings.get('application_well')
    )
    if request.method == 'POST':
        g.db.settings.update(
            {
                '_id': settings.get('_id')
            }, {
                '$set': {
                    'application_title': request.form.get(
                        'application_title'
                    ),
                    'application_email': request.form.get(
                        'application_email'
                    ),
                    'application_footer': request.form.get(
                        'application_footer'
                    ),
                    'application_well': request.form.get(
                        'application_well'
                    )
                }
            }
        )
        flash('General Settings have been updated')
        return redirect(url_for('adminblueprint.general_settings'))
    else:
        return render_template(
            'admin/manage_settings.html',
            title=title,
            form=form,
            settings=settings
        )


@bp.route('/settings/admins', methods=['GET', 'POST'])
@check_perms(request)
def manage_admins():
    error = True
    settings = check_and_initialize()
    title = "Manage Administrators"
    form = help.deploy_custom_form('add_administrator')
    if request.method == 'POST' and form.validate_on_submit():
        found = g.db.settings.find_one(
            {
                'administrators.admin': request.form.get(
                    'administrator'
                )
            }
        )
        if found:
            flash('User is already in the Administrators List', 'error')
            form.administrator.errors.append('Duplicate user')
            return render_template(
                'admin/manage_admins.html',
                error=error,
                title=title,
                form=form,
                settings=settings
            )

        g.db.settings.update(
            {
                '_id': settings.get('_id')
            }, {
                '$push': {
                    'administrators': {
                        'admin': request.form.get('administrator'),
                        'admin_name': request.form.get('full_name').strip()
                    }
                }
            }
        )
        flash('User has been added as an Administrator')
        return redirect(url_for('adminblueprint.manage_admins'))
    elif request.method == 'POST' and not form.validate_on_submit():
            flash(
                'Form validation failed. Please check the form and try again',
                'error'
            )
            return render_template(
                'admin/manage_admins.html',
                error=error,
                title=title,
                form=form,
                settings=settings
            )

    else:
        return render_template(
            'admin/manage_admins.html',
            title=title,
            form=form,
            settings=settings
        )


@bp.route('/settings/remove/admin/<user>')
@check_perms(request)
def remove_admin(user):
    settings = g.db.settings.find_one()
    g.db.settings.update(
        {
            '_id': settings.get('_id')
        }, {
            '$pull': {
                'administrators': {
                    'admin': user
                }
            }
        }
    )
    flash('Administrator has been removed')
    return redirect(url_for('adminblueprint.manage_admins'))


@bp.route('/settings/menu/<edit_menu_name>', methods=['GET', 'POST'])
@bp.route('/settings/menu', methods=['GET', 'POST'])
@check_perms(request)
def menu_settings(edit_menu_name=None):
    error = True
    settings = check_and_initialize()
    menu_list = help.get_and_sort(
        settings.get('menu'),
        'parent_order',
        'order'
    )
    top_level_menu = help.get_and_sort(
        settings.get('top_level_menu'),
        'order'
    )

    if edit_menu_name:
        menus = settings.get('menu')
        menu_edit = None
        for item in menus:
            if item.get('name') == edit_menu_name:
                menu_edit = item
                break

        if menu_edit:
            title = "Edit Menu Settings for %s" % \
                help.unslug(edit_menu_name)
            menu_form = help.deploy_custom_form(
                'menu_items_form',
                parent_menu=menu_edit.get('parent'),
                menu_display_name=menu_edit.get('display_name'),
                menu_item_url=menu_edit.get('url'),
                menu_permissions=menu_edit.get('view_permissions'),
                menu_item_status=menu_edit.get('active'),
                db_name=menu_edit.get('name'),
                action='edit'
            )
        else:
            title = "Application Menu Settings"
            menu_form = help.deploy_custom_form('menu_items_form')
            edit_menu_name = None
    else:
        title = "Application Menu Settings"
        menu_form = help.deploy_custom_form('menu_items_form')

    parent_menus = help.generate_parent_menu(settings.get('menu'))
    menu_form.parent_menu.choices = [
        (parent, parent) for parent in parent_menus
    ]

    active_roles = help.generate_active_roles(settings.get('roles'))
    menu_form.menu_permissions.choices = [
        (help.slug(role), role) for role in active_roles
    ]
    if request.method == 'POST' and menu_form.validate_on_submit():
        db_name = help.slug(
            str(request.form.get('db_name'))
        )
        existing_name = g.db.settings.find_one(
            {
                'menu.name': db_name
            }
        )
        if existing_name:
            if not (edit_menu_name and (menu_edit.get('name') == db_name)):
                flash(
                    'Name already exists, please choose another name',
                    'error'
                )
                return render_template(
                    'admin/manage_menu.html',
                    title=title,
                    menu_form=menu_form,
                    menu_list=menu_list,
                    top_level_menu=top_level_menu,
                    error=error
                )

        existing_url = g.db.settings.find_one(
            {
                'menu.url': request.form.get('menu_item_url')
            }
        )
        if existing_url:
            if not (edit_menu_name and
                    menu_edit.get('url') == request.form.get('menu_item_url')):
                flash(
                    'URL is already being used, '
                    'please check the URL and try again',
                    'error'
                )
                return render_template(
                    'admin/manage_menu.html',
                    title=title,
                    menu_form=menu_form,
                    menu_list=menu_list,
                    top_level_menu=top_level_menu,
                    error=error
                )

        if request.form.get('parent_menu') == "Add New Parent":
            if request.form.get('new_parent'):
                existing_parent = g.db.settings.find_one(
                    {
                        'top_level_menu.slug': help.slug(
                            request.form.get('new_parent')
                        )
                    }
                )
                if existing_parent:
                    flash(
                        'Parent is already in use, '
                        'please check the value and try again',
                        'error'
                    )
                    return render_template(
                        'admin/manage_menu.html',
                        title=title,
                        menu_form=menu_form,
                        menu_list=menu_list,
                        top_level_menu=top_level_menu,
                        error=error
                    )
                parent_menu = help.normalize(request.form.get('new_parent'))
            else:
                flash(
                    'New Parent cannot be blank when adding a new Parent Item',
                    'error'
                )
                return render_template(
                    'admin/manage_menu.html',
                    title=title,
                    menu_form=menu_form,
                    menu_list=menu_list,
                    top_level_menu=top_level_menu,
                    error=error
                )
        else:
            parent_menu = help.normalize(request.form.get('parent_menu'))

        status = False
        if request.form.get('menu_item_status'):
            status = True

        if edit_menu_name:
            g.db.settings.update(
                {
                    'menu.name': edit_menu_name
                }, {
                    '$set': {
                        'menu.$.name': db_name,
                        'menu.$.display_name': help.normalize(
                            request.form.get('menu_display_name')
                        ),
                        'menu.$.url': request.form.get('menu_item_url'),
                        'menu.$.view_permissions': request.form.get(
                            'menu_permissions'
                        ),
                        'menu.$.active': status,
                        'menu.$.parent': help.slug(parent_menu),
                        'menu.$.parent_order': help.get_parent_order(
                            parent_menu,
                            settings,
                            request.form.get('menu_display_name')
                        )
                    }
                }
            )
            if (
                (
                    menu_edit.get('display_name') != help.normalize(
                        request.form.get('menu_display_name')
                    )
                ) or (
                    menu_edit.get('parent') != help.slug(parent_menu)
                )
            ):
                help.check_top_level_to_remove(menu_edit)
            flash('Menu Item was edited successfully')
        else:
            g.db.settings.update(
                {
                    '_id': settings.get('_id')
                }, {
                    '$push': {
                        'menu': {
                            'name': db_name,
                            'display_name': help.normalize(
                                request.form.get('menu_display_name')
                            ),
                            'url': request.form.get('menu_item_url'),
                            'view_permissions': request.form.get(
                                'menu_permissions'
                            ),
                            'active': status,
                            'parent': help.slug(parent_menu),
                            'order': help.get_next_order_number(
                                menu_list, parent_menu
                            ),
                            'parent_order': help.get_parent_order(
                                parent_menu,
                                settings,
                                request.form.get('menu_display_name')
                            )
                        }
                    }
                }
            )
            flash('Menu Item successfully Added')

        return redirect(url_for('adminblueprint.menu_settings'))
    elif request.method == 'POST' and not (menu_form.validate_on_submit()):
        flash(
            'Form validation failed. Please check the form and try again',
            'error'
        )
        return render_template(
            'admin/manage_menu.html',
            title=title,
            menu_form=menu_form,
            menu_list=menu_list,
            top_level_menu=top_level_menu,
            error=error
        )
    else:
        if edit_menu_name:
            return render_template(
                'admin/_edit_settings_menu.html',
                menu_form=menu_form,
                name=menu_edit.get('name')
            )
        else:
            return render_template(
                'admin/manage_menu.html',
                title=title,
                menu_form=menu_form,
                menu_list=menu_list,
                top_level_menu=top_level_menu
            )


@bp.route('/settings/menu/top_level/promote', methods=['POST'])
@check_perms(request)
def promote_top_level_menu_item():
    settings = g.db.settings.find_one()
    menu_item = request.json.get('name')
    sorted_menu = help.get_and_sort(settings.get('top_level_menu'), 'order')
    found, new_position = 0, None
    for item in reversed(sorted_menu):
        if item.get('name') == menu_item:
            found = 1
            new_position = item.get('order') - 1
            g.db.settings.update(
                {
                    'top_level_menu.name': menu_item
                }, {
                    '$inc': {
                        'top_level_menu.$.order': -1
                    }
                }
            )
        elif (found == 1) and (item.get('order') == new_position):
            g.db.settings.update(
                {
                    'top_level_menu.name': item.get('name')
                }, {
                    '$inc': {
                        'top_level_menu.$.order': 1
                    }
                }
            )
    help.change_top_level_order(
        settings,
        new_position,
        (new_position + 1),
        menu_item
    )
    settings = g.db.settings.find_one()
    new_sorted = help.get_and_sort(settings.get('top_level_menu'), 'order')
    message = 'Top Level Menu Item has been promoted'
    return jsonify(message=message, menu_items=new_sorted)


@bp.route('/settings/menu/top_level/demote', methods=['POST'])
@check_perms(request)
def demote_top_level_menu_item():
    settings = g.db.settings.find_one()
    menu_item = request.json.get('name')
    sorted_menu = help.get_and_sort(settings.get('top_level_menu'), 'order')
    found, new_position = 0, None
    for item in sorted_menu:
        if item.get('name') == menu_item:
            found = 1
            new_position = item.get('order') + 1
            g.db.settings.update(
                {
                    'top_level_menu.name': menu_item
                }, {
                    '$inc': {
                        'top_level_menu.$.order': 1
                    }
                }
            )
        elif (found == 1) and (item.get('order') == new_position):
            g.db.settings.update(
                {
                    'top_level_menu.name': item.get('name')
                }, {
                    '$inc': {
                        'top_level_menu.$.order': -1
                    }
                }
            )
    help.change_top_level_order(
        settings,
        new_position,
        (new_position - 1),
        menu_item
    )
    settings = g.db.settings.find_one()
    new_sorted = help.get_and_sort(settings.get('top_level_menu'), 'order')
    message = 'Top Level Menu Item has been demoted'
    return jsonify(message=message)


@bp.route('/settings/menu/top_level/html')
@check_perms(request)
def menu_top_level_html_generate():
    settings = g.db.settings.find_one()
    sorted_menu = help.get_and_sort(settings.get('top_level_menu'), 'order')
    return render_template(
        'admin/_menu_parent.html',
        top_level_menu=sorted_menu
    )


@bp.route('/settings/menu/promote', methods=['POST'])
@check_perms(request)
def promote_menu_item():
    settings = g.db.settings.find_one()
    menu_item = request.json.get('name')
    sorted_menu = help.get_and_sort(
        settings.get('menu'),
        'parent_order',
        'order'
    )
    found = 0
    parent = 'Not Found'
    for item in reversed(sorted_menu):
        if item.get('name') == menu_item:
            found = 1
            parent = item.get('parent')
            new_position = item.get('order') - 1
            g.db.settings.update(
                {
                    'menu.name': menu_item
                }, {
                    '$inc': {
                        'menu.$.order': -1
                    }
                }
            )
        elif (found == 1) and (item.get('parent') == parent) and \
                (item.get('order') == new_position):
            g.db.settings.update(
                {
                    'menu.name': item.get('name')
                }, {
                    '$inc': {
                        'menu.$.order': 1
                    }
                }
            )
    message = 'Menu Item has been promoted'
    return jsonify(message=message)


@bp.route('/settings/menu/demote', methods=['POST'])
@check_perms(request)
def demote_menu_item():
    settings = g.db.settings.find_one()
    menu_item = request.json.get('name')
    sorted_menu = help.get_and_sort(
        settings.get('menu'),
        'parent_order',
        'order'
    )
    found = 0
    parent = 'Not Found'
    for item in sorted_menu:
        if item.get('name') == menu_item:
            found = 1
            parent = item.get('parent')
            new_position = item.get('order') + 1
            g.db.settings.update(
                {
                    'menu.name': menu_item
                }, {
                    '$inc': {
                        'menu.$.order': 1
                    }
                }
            )
        elif (found == 1) and (item.get('parent') == parent) and \
                (item.get('order') == new_position):
            g.db.settings.update(
                {
                    'menu.name': item.get('name')
                }, {
                    '$inc': {
                        'menu.$.order': -1
                    }
                }
            )
    message = 'Menu Item has been demoted'
    return jsonify(message=message)


@bp.route('/settings/menu/child/html')
@check_perms(request)
def menu_children_html_generate():
    settings = g.db.settings.find_one()
    sorted_menu = help.get_and_sort(
        settings.get('menu'),
        'parent_order',
        'order'
    )
    return render_template(
        'admin/_menu_children.html',
        menu_list=sorted_menu
    )


@bp.route('/settings/menu/remove/<menu_item>')
@check_perms(request)
def remove_menu_item(menu_item):
    menu = g.db.settings.find_one()
    current_menu = None
    for item in menu.get('menu'):
        if item.get('name') == menu_item:
            current_menu = item
            break
    if current_menu:
        g.db.settings.update(
            {
                '_id': menu.get('_id')
            }, {
                '$pull': {
                    'menu': {
                        'name': menu_item
                    }
                }
            }
        )
        help.check_top_level_to_remove(current_menu)
        flash('Menu Item %s was successfully removed' % menu_item)
    return redirect(url_for('adminblueprint.menu_settings'))


@bp.route('/settings/menu/toggle/<task>/<menu_item>')
@check_perms(request)
def toggle_menu_item(task, menu_item):
    if task == "enable":
        g.db.settings.update(
            {
                'menu.name': menu_item
            }, {
                '$set': {
                    'menu.$.active': True
                }
            }
        )
    elif task == "disable":
        g.db.settings.update(
            {
                'menu.name': menu_item
            }, {
                '$set': {
                    'menu.$.active': False
                }
            }
        )
    flash('Menu Item %s status was changed' % menu_item)
    return redirect(url_for('adminblueprint.menu_settings'))


@bp.route('/settings/roles', methods=['GET', 'POST'])
@check_perms(request)
def manage_roles(edit_role_name=None):
    settings = check_and_initialize()
    error = True
    title = "Manage Application Roles"
    form = help.deploy_custom_form('manage_roles')

    if request.method == 'POST' and form.validate_on_submit():
        role_name = help.slug(request.form.get('display_name'))
        existing_role = g.db.settings.find_one(
            {
                'roles.name': role_name
            }
        )
        if existing_role:
            flash(
                'Role already exists, please check the name and try again',
                'error'
            )
            form.display_name.errors.append('Duplicate role')
            return render_template(
                'admin/manage_roles.html',
                title=title,
                form=form,
                roles=settings.get('roles'),
                error=error
            )
        else:
            g.db.settings.update(
                {
                    '_id': settings.get('_id')
                }, {
                    '$push': {
                        'roles': {
                            'name': role_name,
                            'display_name': help.normalize(
                                request.form.get('display_name')
                            ),
                            'active': bool(request.form.get('status'))
                        }
                    }
                }
            )
            flash('Role successfully Added')
        return redirect(url_for('adminblueprint.manage_roles'))
    elif request.method == 'POST' and not (form.validate_on_submit()):
        flash(
            'Form validation failed. Please check the form and try again',
            'error'
        )
        return render_template(
            'admin/manage_roles.html',
            title=title,
            form=form,
            roles=settings.get('roles'),
            error=error
        )
    else:
        return render_template(
            'admin/manage_roles.html',
            form=form,
            title=title,
            roles=settings.get('roles')
        )


@bp.route('/settings/roles/toggle/<task>/<role_name>')
@check_perms(request)
def toggle_role(task, role_name):
    if task == "enable":
        g.db.settings.update(
            {
                'roles.name': role_name
            }, {
                '$set': {
                    'roles.$.active': True
                }
            }
        )
    elif task == "disable":
        g.db.settings.update(
            {
                'roles.name': role_name
            }, {
                '$set': {
                    'roles.$.active': False
                }
            }
        )
    flash('Role %s status was changed' % role_name)
    return redirect(url_for('adminblueprint.manage_roles'))


@bp.route('/settings/roles/remove/<role_name>')
@check_perms(request)
def remove_role(role_name):
    settings = g.db.settings.find_one()
    g.db.settings.update(
        {
            '_id': settings.get('_id')
        }, {
            '$pull': {
                'roles': {
                    'name': role_name
                }
            }
        }
    )
    flash('Role has been removed')
    return redirect(url_for('adminblueprint.manage_roles'))


@bp.route('/settings/permissions/<role>', methods=['GET', 'POST'])
@check_perms(request)
def permissions_define(role):
    error = None
    title = "Manage Permissions for: %s" % help.unslug(role)
    form = forms.ManagePermissions()
    url_root = request.url_root[:-1]
    url_routes = current_app.url_map.iter_rules()
    form = help.generate_dynamic_form(url_routes, role)

    if request.method == 'POST' and form.validate_on_submit():
        set_perms = help.evaluate_permissions(request.form.iterlists())
        g.db.settings.update(
            {
                'roles.name': role
            }, {
                '$unset': {
                    'roles.$.perms': 1
                }
            }
        )
        g.db.settings.update(
            {
                'roles.name': role
            }, {
                '$set': {
                    'roles.$.perms': set_perms
                }
            }
        )
        flash('Permissions have been updated for %s role' % help.unslug(role))
        return redirect(url_for('adminblueprint.manage_roles'))
    elif request.method == 'POST' and not (form.validate_on_submit()):
        flash(
            'Form validation failed, please check the form and try again',
            'error'
        )
        return render_template(
            'admin/manage_permissions.html',
            title=title,
            form=form,
            error=error
        )
    else:
        return render_template(
            'admin/manage_permissions.html',
            title=title,
            form=form
        )


"""
    Custom forms management
"""


@bp.route('/forms/fields/<form_id>/<field_name>', methods=['GET', 'POST'])
@bp.route('/forms/fields/<form_id>', methods=['GET', 'POST'])
@check_perms(request)
def manage_form_fields(form_id, field_name=None):
    error = True
    custom_form = g.db.forms.find_one({'_id': ObjectId(form_id)})
    sorted_fields = help.get_and_sort(custom_form.get('fields'), 'order')
    title = "Manage Fields for %s" % custom_form.get('display_name').title()
    if field_name:
        fields = g.db.forms.find_one(
            {
                '_id': ObjectId(form_id),
                'fields': {
                    '$elemMatch': {
                        'name': field_name
                    }
                }
            }
        ).get('fields')

        edit_field = None
        for field in fields:
            if field.get('name') == field_name:
                edit_field = field
                break

        if edit_field:
            form = forms.BuildCustomForm(
                form_id=custom_form.get('_id'),
                name=field_name,
                label=edit_field.get('label'),
                field_type=edit_field.get('field_type'),
                default=edit_field.get('default'),
                default_value=edit_field.get('default_value'),
                style_id=edit_field.get('style_id'),
                description=edit_field.get('description'),
                required=edit_field.get('required'),
                active=edit_field.get('active'),
                field_choices=edit_field.get('field_choices'),
                order=edit_field.get('order')
            )
    else:
        form = forms.BuildCustomForm(form_id=custom_form.get('_id'))

    if request.method == 'POST' and form.validate_on_submit():
        sani_name = help.slug(request.form.get('name'))
        active, required, default = False, False, False

        if field_name:
            if not sani_name == field_name:
                if g.db.forms.find(
                    {
                        '_id': ObjectId(form_id),
                        'fields': {
                            '$elemMatch': {
                                'name': sani_name
                            }
                        }
                    }
                ).count() > 0:
                    flash(
                        'Field name already exists, '
                        'please check the name and try again',
                        'error'
                    )
                    return render_template(
                        'admin/manage_form_fields.html',
                        form=form,
                        title=title,
                        fields=sorted_fields,
                        form_id=form_id,
                        error=error
                    )
        else:
            if g.db.forms.find(
                {
                    '_id': ObjectId(form_id),
                    'fields.name': sani_name
                }
            ).count() > 0:
                flash(
                    'Field name already exists, '
                    'please check the name and try again',
                    'error'
                )
                return render_template(
                    'admin/manage_form_fields.html',
                    form=form,
                    title=title,
                    fields=sorted_fields,
                    form_id=form_id,
                    error=error
                )

        if field_name:
            g.db.forms.update(
                {
                    '_id': ObjectId(form_id),
                    'fields.name': field_name
                },
                {
                    '$set': {
                        'fields.$.name': sani_name,
                        'fields.$.label': request.form.get('label'),
                        'fields.$.field_type': request.form.get('field_type'),
                        'fields.$.field_choices': request.form.get(
                            'field_choices'
                        ),
                        'fields.$.default': bool(request.form.get('default')),
                        'fields.$.default_value': request.form.get(
                            'default_value'
                        ),
                        'fields.$.style_id': request.form.get('style_id'),
                        'fields.$.required': bool(
                            request.form.get('required')
                        ),
                        'fields.$.active': bool(request.form.get('active')),
                        'fields.$.order': int(request.form.get('order')),
                        'fields.$.description': request.form.get('description')
                    }
                }
            )
            flash('Field successfully updated')
            return redirect(
                url_for(
                    'adminblueprint.manage_form_fields',
                    form_id=form_id
                )
            )
        else:
            g.db.forms.update(
                {
                    '_id': ObjectId(form_id)},
                {
                    "$push": {
                        'fields': {
                            'name': sani_name,
                            'label': request.form.get('label'),
                            'field_type': request.form.get('field_type'),
                            'field_choices': request.form.get('field_choices'),
                            'default': bool(request.form.get('default')),
                            'default_value': request.form.get('default_value'),
                            'style_id': request.form.get('style_id'),
                            'required': bool(request.form.get('required')),
                            'active': bool(request.form.get('active')),
                            'order': help.get_form_field_order(form_id),
                            'description': request.form.get('description')
                        }
                    }
                }
            )
            flash('Field successfully added to form')
            return redirect(
                url_for(
                    'adminblueprint.manage_form_fields',
                    form_id=form_id
                )
            )
    elif request.method == 'POST' and not form.validate_on_submit():
        flash(
            'Form validation error. Please check the form and try again',
            'error'
        )
        return render_template(
            'admin/manage_form_fields.html',
            form=form,
            title=title,
            fields=sorted_fields,
            form_id=form_id,
            error=error
        )
    else:
        if form_id and field_name:
            show_default_field, show_field_type = False, False
            if (
                field.get('field_type') == 'SelectField' or
                field.get('field_type') == 'RadioField' or
                field.get('field_type') == 'SelectMultipleField'
            ):
                show_field_type = True

            if field.get('default'):
                show_default_field = True

            return render_template(
                'admin/_edit_custom_fields.html',
                form=form,
                form_id=form_id,
                field_name=field_name,
                show_default_field=show_default_field,
                show_field_type=show_field_type
            )
        else:
            return render_template(
                'admin/manage_form_fields.html',
                form=form,
                title=title,
                fields=sorted_fields,
                form_id=form_id
            )


@bp.route('/forms/fields/promote', methods=['POST'])
@check_perms(request)
def promote_form_field():
    form_id = request.json.get('form_id')
    field_name = request.json.get('field_name')
    form = g.db.forms.find_one({'_id': ObjectId(form_id)})
    fields = help.get_and_sort(form.get('fields'), 'order')
    found = 0
    for item in reversed(fields):
        if item.get('name') == field_name:
            found = 1
            new_position = int(item.get('order')) - 1
            g.db.forms.update(
                {
                    '_id': ObjectId(form_id),
                    'fields.name': field_name
                }, {
                    '$inc': {
                        'fields.$.order': -1
                    }
                }
            )
        elif (found == 1) and (item.get('order') == new_position):
            g.db.forms.update(
                {
                    '_id': ObjectId(form_id),
                    'fields.name': item.get('name')
                }, {
                    '$inc': {
                        'fields.$.order': 1
                    }
                }
            )
    message = '%s field has been promoted' % field_name.title()
    return jsonify(message=message)


@bp.route('/forms/fields/demote', methods=['POST'])
@check_perms(request)
def demote_form_field():
    form_id = request.json.get('form_id')
    field_name = request.json.get('field_name')
    form = g.db.forms.find_one({'_id': ObjectId(form_id)})
    fields = help.get_and_sort(form.get('fields'), 'order')
    found = 0
    for item in fields:
        if item.get('name') == field_name:
            found = 1
            new_position = int(item.get('order')) + 1
            g.db.forms.update(
                {
                    '_id': ObjectId(form_id),
                    'fields.name': field_name
                }, {
                    '$inc': {
                        'fields.$.order': 1
                    }
                }
            )
        elif (found == 1) and (item.get('order') == new_position):
            g.db.forms.update(
                {
                    '_id': ObjectId(form_id),
                    'fields.name': item.get('name')
                }, {
                    '$inc': {
                        'fields.$.order': -1
                    }
                }
            )
    message = '%s field has been demoted' % field_name.title()
    return jsonify(message=message)


@bp.route('/forms/fields/html/<form_id>')
@check_perms(request)
def form_html_generate(form_id):
    custom_form = g.db.forms.find_one({'_id': ObjectId(form_id)})
    sorted_fields = help.get_and_sort(custom_form.get('fields'), 'order')
    return render_template(
        'admin/_form_fields.html',
        form_id=form_id,
        fields=sorted_fields
    )


@bp.route('/forms/fields/delete/<form_id>/<field_name>')
@check_perms(request)
def remove_custom_field_from_form(form_id, field_name):
    found_field = g.db.forms.find_one(
        {
            '_id': ObjectId(form_id),
            'fields.name': field_name
        }
    )
    if found_field:
        help.reorder_fields(form_id, found_field, field_name)
        g.db.forms.update(
            {
                '_id': ObjectId(form_id)
            }, {
                '$pull': {
                    'fields': {
                        'name': field_name
                    }
                }
            }
        )
        flash('Custom field was removed successfully')
        return redirect(
            url_for(
                'adminblueprint.manage_form_fields',
                form_id=form_id
            )
        )
    else:
        flash('Custom field was not found, and not removed', 'error')
        return redirect(
            url_for(
                'adminblueprint.manage_form_fields',
                form_id=form_id
            )
        )


@bp.route('/forms/fields/<method>/<form_id>/<field_name>')
@check_perms(request)
def toggle_custom_fields(method, form_id, field_name):
    if method == 'activate':
        g.db.forms.update(
            {
                '_id': ObjectId(form_id),
                'fields.name': field_name
            }, {
                '$set': {
                    'fields.$.active': True
                }
            }
        )
    elif method == 'deactivate':
        g.db.forms.update(
            {
                '_id': ObjectId(form_id),
                'fields.name': field_name
            }, {
                '$set': {
                    'fields.$.active': False
                }
            }
        )
    flash('Successfully %sd Custom Field' % method)
    return redirect(
        url_for(
            'adminblueprint.manage_form_fields',
            form_id=form_id
        )
    )


@bp.route('/forms/<form_id>', methods=['GET', 'POST'])
@bp.route('/forms', methods=['GET', 'POST'])
@check_perms(request)
def manage_forms(form_id=None):
    error, edit_form = True, None
    all_forms = g.db.forms.find()
    if form_id:
        edit_form = g.db.forms.find_one({'_id': ObjectId(form_id)})
        form = forms.BuildForm(
            name=edit_form.get('name'),
            submission_url=edit_form.get('submission_url'),
            active=edit_form.get('active'),
            system_form=edit_form.get('system_form')
        )
    else:
        form = forms.BuildForm()

    if request.method == 'POST' and form.validate_on_submit():
        sani_name = help.slug(request.form.get('name'))
        active, system_form = False, False

        active = bool(request.form.get('active'))
        system_form = bool(request.form.get('system_form'))

        if edit_form:
            if not edit_form.get('name') == sani_name:
                if g.db.forms.find_one({'name': sani_name}):
                    flash(
                        'Form name already exists, please check '
                        'the name and try again',
                        'error'
                    )
                    return render_template(
                        'admin/manage_forms.html',
                        form=form,
                        all_forms=all_forms,
                        error=error
                    )
            if not edit_form.get('submission_url') == \
                    request.form.get('submission_url'):
                if g.db.forms.find_one(
                    {
                        'submission_url': request.form.get(
                            'submission_url'
                        )
                    }
                ):
                    flash(
                        'Another form posts to the same URL. '
                        'Please check the URL and try again',
                        'error'
                    )
                    return render_template(
                        'admin/manage_forms.html',
                        form=form,
                        all_forms=all_forms,
                        error=error
                    )

            g.db.forms.update(
                {
                    '_id': ObjectId(form_id)
                }, {
                    '$set': {
                        'name': sani_name,
                        'display_name': help.unslug(sani_name),
                        'submission_url': request.form.get('submission_url'),
                        'active': active,
                        'system_form': system_form
                    }
                }
            )
        else:
            if g.db.forms.find_one({'name': sani_name}):
                flash(
                    'Form name already exists, please check'
                    ' the name and try again',
                    'error'
                )
                return render_template(
                    'admin/manage_forms.html',
                    form=form,
                    all_forms=all_forms,
                    error=error
                )
            elif g.db.forms.find_one(
                    {
                        'submission_url': request.form.get(
                            'submission_url'
                        )
                    }):
                flash(
                    'Another form posts to the same URL.'
                    ' Please check the URL and try again',
                    'error'
                )
                return render_template(
                    'admin/manage_forms.html',
                    form=form,
                    all_forms=all_forms,
                    error=error
                )

            g.db.forms.insert(
                {
                    'name': sani_name,
                    'display_name': help.unslug(sani_name),
                    'submission_url': request.form.get('submission_url'),
                    'active': active,
                    'system_form': system_form
                }
            )
        if edit_form:
            flash('Successfully updated Custom Form')
            return redirect(url_for('adminblueprint.manage_forms'))
        else:
            flash('Successfully added Custom Form')
            return redirect(url_for('adminblueprint.manage_forms'))
    elif request.method == 'POST' and not form.validate_on_submit():
        flash(
            'Form Validation failed. Please check the form and try again',
            'error'
        )
        return render_template(
            'admin/manage_forms.html',
            form=form,
            all_forms=all_forms,
            error=error
        )
    else:
        if form_id:
            return render_template(
                'admin/_edit_custom_forms.html',
                form=form,
                form_id=form_id
            )
        else:
            return render_template(
                'admin/manage_forms.html',
                form=form,
                all_forms=all_forms
            )


@bp.route('/forms/delete/<form_id>')
@check_perms(request)
def remove_custom_form(form_id):
    form = g.db.forms.find_one({'_id': ObjectId(form_id)})
    if not form.get('system_form'):
        g.db.forms.remove({'_id': ObjectId(form_id)})
        flash('Successfully removed Custom Form')
        return redirect(url_for('adminblueprint.manage_forms'))
    else:
        flash('System form cannot be removed', 'error')
        return redirect(url_for('adminblueprint.manage_forms'))


@bp.route('/forms/<method>/<form_id>')
@check_perms(request)
def toggle_custom_forms(method, form_id):
    if method == 'activate':
        g.db.forms.update(
            {
                '_id': ObjectId(form_id)
            }, {
                '$set': {
                    'active': True
                }
            }
        )
    elif method == 'deactivate':
        g.db.forms.update(
            {
                '_id': ObjectId(form_id)
            }, {
                '$set': {
                    'active': False
                }
            }
        )
    flash('Successfully %sd Custom Form' % method)
    return redirect(url_for('adminblueprint.manage_forms'))


"""
    Login and Logout
"""


@bp.route('/login', methods=['GET', 'POST'])
def login():
    results, title, placeholder = None, None, None
    form = help.deploy_custom_form('login_form')
    title = 'Log In'
    placeholder = 'API Key or User Password'

    if request.method == 'POST':
        if form.validate_on_submit():
            results = help.cloud_authenticate(request)
        else:
            flash('Form validation error, please check the form and try again')
            return render_template(
                'admin/login.html',
                title=title,
                form=form,
                placeholder=placeholder,
                error=True
            )

    if results:
        permissions.set_permissions_for_application(session.get('username'))
        return redirect(url_for('index'))
    else:
        return render_template(
            'admin/login.html',
            title=title,
            form=form,
            placeholder=placeholder,
            testing=current_app.config.get('TESTING')
        )


@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('index'))
