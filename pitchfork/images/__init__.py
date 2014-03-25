#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'images',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/images'
)


COLLECTION = 'images'
BLUEPRINT = 'images'
URL_LINK = 'images'
TITLE = 'Cloud Images'


import pymongo
import global_routes
