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
from datetime import timedelta
from config import config


import re
import json


from adminbp import bp as admin_bp
from manage_globals import bp as manage_bp
from engine import bp as engine_bp


app = Flask(__name__)
app.config.from_object(config)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(manage_bp, url_prefix='/manage')
app.register_blueprint(engine_bp, url_prefix='/engine')


# Setup DB based on the app name
mongo, db = HapPyMongo(config)


from global_helper import (front_page_most_accessed, search_for_calls,
    gather_history)


import product_views


@app.template_filter()
def nl2br(value):
    if value:
        _newline_re = re.compile(r'(?:\r\n|\r|\n)')
        return _newline_re.sub('<br>', value)


@app.template_filter()
def tab2spaces(value):
    if value:
        text = re.sub('\t', '&nbsp;' * 4, value)
        return text


@app.template_filter()
def unslug(value):
    text = re.sub('_', ' ', value)
    return text


@app.template_filter()
def slug(value):
    text = re.sub('\s+', '_', value)
    return text


@app.template_filter()
def check_regex(value):
    if re.match('variable', value):
        return True
    else:
        return False


@app.template_filter()
def pretty_print_json(string):
    return json.dumps(
        string,
        sort_keys=False,
        indent=4,
        separators=(',', ':')
    )


@app.context_processor
def utility_processor():
    def unslug(string):
        return re.sub('_', ' ', string)

    def parse_field_data(value):
        choices = re.sub('\r\n', ',', value)
        return choices.split(',')

    def slugify(data):
        temp_string = re.sub(' +', ' ', str(data.strip()))
        return re.sub(' ', '_', temp_string)

    return dict(
        parse_field_data=parse_field_data,
        unslug=unslug,
        slugify=slugify
    )


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
