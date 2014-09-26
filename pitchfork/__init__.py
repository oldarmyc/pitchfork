# Copyright 2014 Dave Kludt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask, render_template, g, request
from happymongo import HapPyMongo
from config import config
from adminbp import bp as admin_bp
from manage_globals import bp as manage_bp
from engine import bp as engine_bp
from global_helper import front_page_most_accessed, search_for_calls
from global_helper import gather_history
from inspect import getmembers, isfunction


import context_functions
import product_views
import template_filters


app = Flask(__name__)
app.config.from_object(config)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(manage_bp, url_prefix='/manage')
app.register_blueprint(engine_bp, url_prefix='/engine')

# Setup DB based on the app name
mongo, db = HapPyMongo(config)
product_views.ProductsView.register(app)
custom_filters = {
    name: function for name, function in getmembers(template_filters)
    if isfunction(function)
}
app.jinja_env.filters.update(custom_filters)
app.context_processor(context_functions.utility_processor)

views.ProductsView.register(app)
views.MiscView.register(app)


@app.before_request
def before_request():
    g.db = db
