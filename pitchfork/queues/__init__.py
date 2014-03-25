#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'queues',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/queues'
)


COLLECTION = 'queues'
BLUEPRINT = 'queues'
URL_LINK = 'queues'
TITLE = 'Cloud Queues'


import pymongo
import global_routes
