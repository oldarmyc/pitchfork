#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'load_balancers',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/load_balancers'
)


COLLECTION = 'load_balancers'
BLUEPRINT = 'load_balancers'
URL_LINK = 'load_balancers'
TITLE = 'Cloud Load Balancers'


import pymongo
import global_routes
