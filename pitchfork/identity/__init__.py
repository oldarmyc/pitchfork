#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'identity',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/identity'
)


COLLECTION = 'cloud_identity'
BLUEPRINT = 'identity'
URL_LINK = 'identity'
TITLE = 'Cloud Identity'


import pymongo
import global_routes
