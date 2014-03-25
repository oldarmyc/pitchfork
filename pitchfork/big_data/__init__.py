#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'big_data',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/big_data'
)


COLLECTION = 'big_data'
BLUEPRINT = 'big_data'
URL_LINK = 'big_data'
TITLE = 'Cloud Big Data'


import pymongo
import global_routes
