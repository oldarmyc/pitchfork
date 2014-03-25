#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'autoscale',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/autoscale'
)


COLLECTION = 'autoscale'
BLUEPRINT = 'autoscale'
URL_LINK = 'autoscale'
TITLE = 'Cloud Auto Scaling'


import pymongo
import global_routes
