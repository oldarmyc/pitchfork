#!/usr/bin/env python

from functools import wraps, update_wrapper
from flask import flash, redirect, url_for


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
                else:
                    flash('Please login to the Application', 'error')
                return redirect(url_for('index'))

            return fn(*args, **kwargs)
        return update_wrapper(wrapped_function, fn)
    return decorator
