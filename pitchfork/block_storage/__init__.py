#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'block_storage',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/block_storage'
)


COLLECTION = 'cbs'
BLUEPRINT = 'block_storage'
URL_LINK = 'block_storage'
TITLE = 'Cloud Block Storage'


import pymongo
import global_routes
