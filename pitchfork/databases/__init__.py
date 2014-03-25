#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'databases',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/databases'
)


COLLECTION = 'cloud_db'
BLUEPRINT = 'databases'
URL_LINK = 'databases'
TITLE = 'Cloud Databases'


import pymongo
import global_routes
