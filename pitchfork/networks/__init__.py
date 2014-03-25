#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'networks',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/networks'
)


COLLECTION = 'cloud_networks'
BLUEPRINT = 'networks'
URL_LINK = 'networks'
TITLE = 'Cloud Networks'


import pymongo
import global_routes
