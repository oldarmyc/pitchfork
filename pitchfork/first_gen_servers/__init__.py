#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'first_gen_servers',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/fg_servers'
)


COLLECTION = 'fg_servers'
BLUEPRINT = 'first_gen_servers'
URL_LINK = 'fg_servers'
TITLE = 'First Gen Servers'


import pymongo
import global_routes
