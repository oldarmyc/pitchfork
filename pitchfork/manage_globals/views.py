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

from . import bp
from pitchfork.adminbp.decorators import check_perms
from flask import render_template, redirect, url_for, request, flash, g


import forms


@bp.route('/verbs', methods=['GET', 'POST'])
@check_perms(request)
def define_available_verbs():
    api_settings = g.db.api_settings.find_one()
    form = forms.VerbSet()
    if request.method == 'POST' and form.validate_on_submit():
        active = bool(request.form.get('active'))
        verb = request.form.get('name').upper()
        if g.db.api_settings.find_one(
            {
                'verbs.name': verb
            }
        ):
            flash(
                'Verb %s is already setup, no need to add it again' % verb,
                'error'
            )
            return render_template(
                'manage/manage_verbs.html',
                form=form,
                api_settings=api_settings
            )

        g.db.api_settings.update(
            {
                '_id': api_settings.get('_id')
            }, {
                '$push': {
                    'verbs': {
                        'name': verb,
                        'active': active
                    }
                }
            }
        )
        flash('Verb successfully added to system', 'success')
        return redirect(url_for('manage_globals.define_available_verbs'))
    else:
        if request.method == 'POST':
            flash(
                'There was a form validation error, please '
                'check the required values and try again.',
                'error'
            )

    return render_template(
        'manage/manage_verbs.html',
        form=form,
        api_settings=api_settings
    )


@bp.route('/regions', methods=['GET', 'POST'])
@check_perms(request)
def define_available_regions():
    api_settings = g.db.api_settings.find_one()
    form = forms.RegionSet()
    if request.method == 'POST' and form.validate_on_submit():
        abbreviation = request.form.get('abbreviation').upper()
        region = request.form.get('name').title()
        if api_settings.get('regions'):
            if g.db.api_settings.find_one(
                {
                    'regions.name': region
                }
            ):
                flash(
                    'Region %s is already setup, no '
                    'need to add it again' % region,
                    'error'
                )
                return render_template(
                    'manage/manage_regions.html',
                    form=form,
                    api_settings=api_settings
                )

            g.db.api_settings.update(
                {
                    '_id': api_settings.get('_id')
                }, {
                    '$push': {
                        'regions': {
                            'name': region,
                            'abbreviation': abbreviation
                        }
                    }
                }
            )
            flash('Region successfully added to system', 'success')
        else:
            g.db.api_settings.update(
                {
                    '_id': api_settings.get('_id')
                }, {
                    '$set': {
                        'regions': [
                            {
                                'name': region,
                                'abbreviation': abbreviation
                            }
                        ]
                    }
                }
            )
            flash('Region successfully added to system', 'success')

        return redirect(url_for('manage_globals.define_available_regions'))
    else:
        if request.method == 'POST':
            flash(
                'There was a form validation error, please '
                'check the required values and try again.',
                'error'
            )

        return render_template(
            'manage/manage_regions.html',
            form=form,
            api_settings=api_settings
        )


@bp.route('/<key>/<action>/<value>')
@check_perms(request)
def data_type_actions(key, action, value):
    actions = ['activate', 'deactivate', 'delete']
    maps = {
        'verbs': {
            'search': 'verbs.name',
            'change': 'verbs.$.active',
            'redirect': '/manage/verbs'
        },
        'regions': {
            'search': 'regions.name',
            'redirect': '/manage/regions'
        }
    }
    if maps.get(key):
        work = maps.get(key)
        if action in actions:
            found = g.db.api_settings.find_one(
                {
                    work.get('search'): value
                }
            )
            if found:
                if action == 'delete':
                    keys = work.get('search').split('.')
                    change = {'$pull': {keys[0]: {keys[1]: value}}}
                else:
                    if action == 'activate':
                        change = {'$set': {work.get('change'): True}}
                    elif action == 'deactivate':
                        change = {'$set': {work.get('change'): False}}

                g.db.api_settings.update({work.get('search'): value}, change)
                flash(
                    '%s was %sd successfully' % (
                        value.title(),
                        action
                    ),
                    'success'
                )
            else:
                flash(
                    '%s was not found so no action taken' % value.title(),
                    'error'
                )
        else:
            flash('Invalid action given so no action taken', 'error')
        return redirect(work.get('redirect'))
    else:
        flash('Invalid data key given so no action taken', 'error')
        return redirect('/')
