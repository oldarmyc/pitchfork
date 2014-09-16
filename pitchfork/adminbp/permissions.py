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

from flask import session, g


def check_for_admin(user):
    if user:
        admin_search = g.db.settings.find(
            {
                'administrators.admin': user
            }
        )
        if admin_search.count():
            return True
    return False


def is_admin():
    if session.get('role') is not None:
        role = session.get('role')
        if role == 'administrators':
            return True
    return False


def role_has_access(path):
    if session.get('username'):
        if is_admin():
            return True, True
        elif session.get('role'):
            settings = g.db.settings.find_one(
                {
                    'roles.name': session.get('role')
                }, {
                    'roles.$.perms': 1
                }
            )
            if settings:
                if (
                    str(path) in settings.get('roles')[0].get('perms') and
                    settings.get('roles')[0].get('active')
                ):
                    return True, True
                else:
                    return False, True
            else:
                return False, True
    else:
        settings = g.db.settings.find_one(
            {
                'roles.name': 'all'
            }, {
                'roles.$.perms': 1
            }
        )
        if settings:
            if str(path) in settings.get('roles')[0].get('perms'):
                return True, False
            else:
                return False, False
        else:
            return False, False


def set_permissions_for_application(username):
    if username:
        if check_for_admin(username):
            session['role'] = 'administrators'
        else:
            session['role'] = 'logged_in'
    return
