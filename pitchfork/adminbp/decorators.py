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

from functools import update_wrapper
from flask import flash, redirect, url_for, request


import permissions as perm


def check_perms(route):
    def decorator(fn):
        def wrapped_function(*args, **kwargs):
            answer, logged_in = perm.role_has_access(route.url_rule)
            if not answer:
                if logged_in:
                    flash(
                        'You do not have the correct '
                        'permissions to access this page',
                        'error'
                    )
                    return redirect('/')
                else:
                    flash('Please login to the Application', 'error')
                    return redirect(
                        url_for(
                            'adminblueprint.login',
                            next=request.path
                        )
                    )
            return fn(*args, **kwargs)
        return update_wrapper(wrapped_function, fn)
    return decorator
