#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'cloud_feeds',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/cloud_feeds'
)


COLLECTION = 'cloud_feeds'
BLUEPRINT = 'cloud_feeds'
URL_LINK = 'cloud_feeds'
TITLE = 'Cloud Feeds'


import pymongo
import global_routes
