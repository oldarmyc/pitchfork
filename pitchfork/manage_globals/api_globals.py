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

from . import bp, check_perms
from flask import render_template, redirect, url_for, \
    request, flash, g, current_app


import forms


@bp.route('/verbs', methods=['GET', 'POST'])
@check_perms(request)
def define_available_verbs():
    error = True
    api_settings = g.db.api_settings.find_one()
    title = "Available API Verbs"
    form = forms.VerbSet()
    if request.method == 'POST' and form.validate_on_submit():
        active = bool(request.form.get('active'))
        verb = request.form.get('name').upper()
        if api_settings:
            if not g.db.api_settings.find_one(
                {
                    'verbs.name': verb
                }
            ):
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
                message = "Verb successfully added to system"
            else:
                message = (
                    'Verb %s is already setup, no '
                    'need to add it again' % verb
                )
                flash(message)
                return render_template(
                    'manage_verbs.html',
                    title=title,
                    form=form,
                    api_settings=api_settings,
                    error=error
                )
        flash(message)
        return redirect(url_for('manage_globals.define_available_verbs'))
    elif request.method == 'POST' and not form.validate_on_submit():
        flash(
            'There was a form validation error, please '
            'check the required values and try again.'
        )
        return render_template(
            'manage_verbs.html',
            title=title,
            form=form,
            api_settings=api_settings,
            error=error
        )
    else:
        return render_template(
            'manage_verbs.html',
            title=title,
            form=form,
            api_settings=api_settings
        )


@bp.route('/verbs/<action>/<verb>', methods=['GET', 'POST'])
@check_perms(request)
def verb_actions(action, verb):
    if action == 'delete':
        g.db.api_settings.update(
            {
                'verbs.name': verb
            }, {
                '$pull': {
                    'verbs': {
                        'name': verb
                    }
                }
            }
        )
        message = ("Verb %s was removed successfully" % verb)
    elif action == 'deactivate':
        g.db.api_settings.update(
            {
                'verbs.name': verb
            }, {
                '$set': {
                    'verbs.$.active': False
                }
            }
        )
        message = ("Verb %s was deactivated successfully" % verb)
    elif action == 'activate':
        g.db.api_settings.update(
            {
                'verbs.name': verb
            }, {
                '$set': {
                    'verbs.$.active': True
                }
            }
        )
        message = ("Verb %s was activated successfully" % verb)
    flash(message)
    return redirect(url_for('manage_globals.define_available_verbs'))


@bp.route('/dcs', methods=['GET', 'POST'])
@check_perms(request)
def define_available_dcs():
    error = True
    api_settings = g.db.api_settings.find_one()
    title = "Available Data Centers"
    form = forms.DCSet()
    if request.method == 'POST' and form.validate_on_submit():
        abbreviation = request.form.get('abbreviation').upper()
        dc = request.form.get('name').title()
        if api_settings:
            if api_settings.get('dcs'):
                if not g.db.api_settings.find_one(
                    {
                        'dcs.name': dc
                    }
                ):
                    g.db.api_settings.update(
                        {
                            '_id': api_settings.get('_id')
                        }, {
                            '$push': {
                                'dcs': {
                                    'name': dc,
                                    'abbreviation': abbreviation
                                }
                            }
                        }
                    )
                    message = "DC successfully added to system"
                else:
                    message = (
                        'DC %s is already setup, no '
                        'need to add it again' % dc
                    )
                    flash(message)
                    return render_template(
                        'manage_dcs.html',
                        title=title,
                        form=form,
                        api_settings=api_settings,
                        error=error
                    )
            else:
                g.db.api_settings.update(
                    {
                        '_id': api_settings.get('_id')
                    }, {
                        '$set': {
                            'dcs': [
                                {
                                    'name': dc,
                                    'abbreviation': abbreviation
                                }
                            ]
                        }
                    }
                )
                message = "DC successfully added to system"
        flash(message)
        return redirect(url_for('manage_globals.define_available_dcs'))
    elif request.method == 'POST' and not form.validate_on_submit():
        flash(
            'There was a form validation error, please '
            'check the required values and try again.',
            'error'
        )
        return render_template(
            'manage_dcs.html',
            title=title,
            form=form,
            api_settings=api_settings,
            error=error
        )
    else:
        return render_template(
            'manage_dcs.html',
            title=title,
            form=form,
            api_settings=api_settings
        )


@bp.route('/dcs/<action>/<dc>')
@check_perms(request)
def dc_actions(action, dc):
    if action == 'delete':
        g.db.api_settings.update(
            {
                'dcs.name': dc
            }, {
                '$pull': {
                    'dcs': {
                        'name': dc
                    }
                }
            }
        )
    flash('Data center was successfully removed')
    return redirect(url_for('manage_globals.define_available_dcs'))
