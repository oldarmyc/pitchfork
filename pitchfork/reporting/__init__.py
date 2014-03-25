#!/usr/bin/env python

from flask import Blueprint, current_app, render_template, g
from pitchfork.adminbp.decorators import check_perms


bp = Blueprint(
    'reporting',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/reporting'
)


import pymongo
import reporting
