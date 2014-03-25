#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'next_gen_servers',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/ng_servers'
)


COLLECTION = 'ng_servers'
BLUEPRINT = 'next_gen_servers'
URL_LINK = 'ng_servers'
TITLE = 'Next Generation Servers'


import pymongo
import global_routes
