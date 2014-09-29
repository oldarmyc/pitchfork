from flask import Flask, g
from inspect import getmembers, isfunction
from happymongo import HapPyMongo
from config import config
from adminbp import bp as admin_bp
from manage_globals import bp as manage_bp
from engine import bp as engine_bp


import context_functions
import views
import template_filters


def create_app(testing=None):
    app = Flask(__name__)
    if testing:
        config.TESTING = True
        config.MONGO_DATABASE = '%s_test' % config.MONGO_DATABASE
        config.ADMIN = 'rusty.shackelford'

    app.config.from_object(config)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(manage_bp, url_prefix='/manage')
    app.register_blueprint(engine_bp, url_prefix='/engine')

    mongo, db = HapPyMongo(config)
    views.ProductsView.register(app)
    views.MiscView.register(app)

    custom_filters = {
        name: function for name, function in getmembers(template_filters)
        if isfunction(function)
    }
    app.jinja_env.filters.update(custom_filters)
    app.context_processor(context_functions.utility_processor)

    @app.before_request
    def before_request():
        g.db = db

    return app, db
