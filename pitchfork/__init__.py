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


@app.before_request
def before_request():
    g.db = db


@app.route('/')
def index():
    active_products, data_centers, = [], []
    api_settings = db.api_settings.find_one()
    if api_settings:
        active_products = api_settings.get('active_products')

    most_accessed = front_page_most_accessed(active_products)
    if api_settings:
        data_centers = api_settings.get('dcs')

    return render_template(
        'index.html',
        api_settings=api_settings,
        active_products=active_products,
        most_accessed=most_accessed,
        data_centers=data_centers
    )


@app.route('/search', methods=['POST'])
def search():
    search_string = request.json.get('search_string')
    api_results = search_for_calls(search_string)
    return render_template(
        '_api_call_template.html',
        call_loop=api_results
    )


@app.route('/history')
def history():
    active_products = None
    api_settings = g.db.api_settings.find_one()
    if api_settings:
        active_products = api_settings.get('active_products')

    history = gather_history()
    return render_template(
        'history.html',
        history=history,
        api_settings=api_settings,
        active_products=active_products
    )
