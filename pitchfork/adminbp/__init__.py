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

from flask import Blueprint, current_app, g, session


bp = Blueprint(
    'adminblueprint',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/admin'
)


from defaults import check_and_initialize
from operator import itemgetter


import helpers as help
import permissions
import re
import views


def utility_processor():
    settings = g.db.settings.find_one()
    if (settings is None):
        settings = check_and_initialize()

    def app_title():
        return settings.get('application_title')

    def app_well():
        return settings.get('application_well')

    def app_email():
        return settings.get('application_email')

    def app_footer():
        return settings.get('application_footer')

    def check_app_email():
        if settings.get('application_email') and session.get('username'):
            return True
        return False

    def check_if_admin():
        return permissions.is_admin()

    def get_menu():
        menu_items = settings.get('menu')
        active_menu = []
        for menu in menu_items:
            if menu.get('active'):
                if menu.get('view_permissions') == "all":
                    active_menu.append(menu)
                elif menu.get('view_permissions') == "logged_in" and \
                        not (session.get('username') is None):
                    active_menu.append(menu)
                elif menu.get('view_permissions') == "administrators" and \
                        permissions.is_admin():
                    active_menu.append(menu)
        return sorted(active_menu, key=itemgetter('parent_order', 'order'))

    def get_parent_name(parent_slug):
        parent_slug = re.sub('\s+', '_', parent_slug.lower())
        top_menu = g.db.settings.find_one(
            {
                'top_level_menu': {
                    '$elemMatch': {
                        'slug': parent_slug
                    }
                }
            }, {
                'top_level_menu.$': 1, '_id': 0
            }
        )
        if top_menu:
            return top_menu.get('top_level_menu')[0].get('name')

    return dict(
        app_title=app_title(),
        app_footer=app_footer(),
        app_email=app_email(),
        app_well=app_well(),
        check_app_email=check_app_email(),
        get_menu=get_menu(),
        check_if_admin=check_if_admin(),
        get_parent_name=get_parent_name
    )

bp.app_context_processor(utility_processor)
