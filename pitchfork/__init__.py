
from flask import Flask, render_template, g, request
from happymongo import HapPyMongo
from datetime import timedelta
from config import config


import re
import json


# Start import for all blueprints
from adminbp import bp as admin_bp
from cloud_backup import bp as backup_bp
from block_storage import bp as cbs_bp
from databases import bp as db_bp
from dns import bp as dns_bp
from first_gen_servers import bp as fg_bp
from load_balancers import bp as lb_bp
from networks import bp as networks_bp
from identity import bp as identity_bp
from next_gen_servers import bp as ng_bp
from monitoring import bp as mon_bp
from queues import bp as queue_bp
from autoscale import bp as autoscale_bp
from images import bp as images_bp
from big_data import bp as bigdata_bp
from orchestration import bp as orchestration_bp
from manage_globals import bp as manage_bp
from reporting import bp as report_bp
# End Blueprint import


app = Flask(__name__)
app.config.from_object(config)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(backup_bp, url_prefix='/cloud_backup')
app.register_blueprint(cbs_bp, url_prefix='/block_storage')
app.register_blueprint(db_bp, url_prefix='/databases')
app.register_blueprint(dns_bp, url_prefix='/dns')
app.register_blueprint(fg_bp, url_prefix='/fg_servers')
app.register_blueprint(lb_bp, url_prefix='/load_balancers')
app.register_blueprint(networks_bp, url_prefix='/networks')
app.register_blueprint(identity_bp, url_prefix='/identity')
app.register_blueprint(ng_bp, url_prefix='/ng_servers')
app.register_blueprint(mon_bp, url_prefix='/monitoring')
app.register_blueprint(queue_bp, url_prefix='/queues')
app.register_blueprint(autoscale_bp, url_prefix='/autoscale')
app.register_blueprint(images_bp, url_prefix='/images')
app.register_blueprint(bigdata_bp, url_prefix='/big_data')
app.register_blueprint(orchestration_bp, url_prefix='/orchestration')
app.register_blueprint(manage_bp, url_prefix='/manage')
app.register_blueprint(report_bp, url_prefix='/reporting')


# Setup DB based on the app name
mongo, db = HapPyMongo(config)


from global_api_functions import front_page_most_accessed, \
    search_for_calls, gather_history


@app.template_filter()
def nl2br(value):
    _newline_re = re.compile(r'(?:\r\n|\r|\n)')
    return _newline_re.sub('<br>', value)


@app.template_filter()
def tab2spaces(value):
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


@app.context_processor
def utility_processor():
    def parse_field_data(value):
        choices = re.sub('\r\n', ',', value)
        return choices.split(',')

    def to_json(value):
        temp = json.dumps(
            value,
            sort_keys=False,
            indent=4,
            separators=(',', ':')
        )
        return temp

    return dict(
        parse_field_data=parse_field_data,
        to_json=to_json
    )


# Set g to the db so that each blueprint can use it
@app.before_request
def before_request():
    g.mongo = mongo
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
        '_api_call_wrapper_template.html',
        most_accessed=api_results
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


if __name__ == '__main__':
    app.run(debug=True)
