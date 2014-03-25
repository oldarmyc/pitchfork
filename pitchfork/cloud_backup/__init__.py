#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'cloud_backup', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/cloud_backup'
)


COLLECTION = 'cloud_backup'
BLUEPRINT = 'cloud_backup'
URL_LINK = 'cloud_backup'
TITLE = 'Cloud Backup'


import pymongo
import global_routes
