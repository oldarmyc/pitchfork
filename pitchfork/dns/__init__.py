#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'dns',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/dns'
)


COLLECTION = 'cloud_dns'
BLUEPRINT = 'dns'
URL_LINK = 'dns'
TITLE = 'Cloud DNS'


import pymongo
import global_routes
