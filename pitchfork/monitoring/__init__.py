#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'monitoring',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/monitoring'
)


COLLECTION = 'monitoring'
BLUEPRINT = 'monitoring'
URL_LINK = 'monitoring'
TITLE = 'Cloud Monitoring'


import pymongo
import global_routes
