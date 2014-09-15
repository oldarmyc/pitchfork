
from flask import Blueprint


bp = Blueprint(
    'engine',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/engine'
)


import views # flake8: noqa
