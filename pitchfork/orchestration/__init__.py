#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'orchestration',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/orchestration'
)


COLLECTION = 'orchestration'
BLUEPRINT = 'orchestration'
URL_LINK = 'orchestration'
TITLE = 'Cloud Orchestration'


import pymongo
import global_routes
