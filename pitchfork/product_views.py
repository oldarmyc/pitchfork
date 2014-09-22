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

from pitchfork import app
from flask import g, render_template, request, redirect
from flask import url_for, flash, jsonify
from flask.ext.classy import FlaskView, route
from models import Product, Call
from pitchfork.adminbp.decorators import check_perms
from bson.objectid import ObjectId


import global_helper
import global_forms
import pymongo


class ProductsView(FlaskView):
    decorators = [check_perms(request)]
    route_base = '/'

    @route('/<product>/')
    @route('/<product>/<testing>')
    def index(self, product, testing=None):
        testing_calls = False
        if testing is not None:
            testing_calls = True

        found_product = self.retrieve_product(product)
        if type(found_product) is str:
            flash('Product not found, please check the URL and try again')
            return redirect(url_for('index'))

        api_calls = global_helper.gather_api_calls(
            found_product,
            testing_calls
        )
        restrict_dcs, data_centers = global_helper.check_for_product_dcs(
            found_product
        )
        return render_template(
            'product_front.html',
            api_calls=api_calls,
            api_settings=found_product,
            data_centers=data_centers,
            title=found_product.title,
            api_process='/%s/api/call/process' % product,
            testing=testing_calls,
            require_dc=found_product.require_dc,
            restrict_dcs=restrict_dcs
        )

    """ Product API Call Fire """

    @route('/<product>/api/call/process', methods=['POST'])
    def execute_api_call(self, product):
        found_product = self.retrieve_product(product)
        if type(found_product) is str:
            flash('Product not found, please check the URL and try again')
            return redirect(url_for('index'))

        if request.json.get('testing') or request.json.get('mock'):
            api_call = getattr(g.db, found_product.db_name).find_one(
                {'_id': ObjectId(request.json.get('api_id'))}
            )
        else:
            api_call = getattr(g.db, found_product.db_name).find_and_modify(
                query={'_id': ObjectId(request.json.get('api_id'))},
                update={'$inc': {'accessed': 1}}
            )

        """ Change this to a jsonify call and have jquery handle it """
        if not api_call:
            flash('API Call was not found')
            return redirect(url_for('index'))

        """ Retrieve all of the elements for the call """
        api_url, header, data_package = global_helper.generate_vars_for_call(
            found_product,
            api_call,
            request
        )

        """ Send off the request and retrieve the data elements """
        if request.json.get('mock'):
            response_headers, response_body, response_code = None, None, None
            request_headers = header
        else:
            request_headers, response_headers, response_body, response_code = (
                global_helper.process_api_request(
                    api_url,
                    request.json.get('api_verb'),
                    data_package,
                    header
                )
            )

        if not (request.json.get('testing') or request.json.get('mock')):
            global_helper.log_api_call_request(
                request_headers,
                response_headers,
                response_body,
                response_code,
                api_call,
                request.json,
                data_package,
                api_url,
                found_product.title
            )

        """ Send the data structure back to the browser """
        return jsonify(
            request_headers=request_headers,
            response_headers=response_headers,
            response_body=response_body,
            response_code=response_code,
            api_url=api_url,
            data_package=data_package
        )

    """ Product Management """

    @route('/<product>/manage', methods=['GET', 'POST'])
    def manage_settings(self, product):
        product_data = self.retrieve_product(product)
        if type(product_data) is str:
            title = "%s Manage Settings" % product.title()
            post_url = "/%s/manage" % product
            product_data = None
            form = global_forms.ManageProduct()
        else:
            title = "%s Manage Settings" % product_data.title
            post_url = "%s/manage" % product_data.app_url
            form = global_forms.ManageProduct(obj=product_data)

        if request.method == 'POST' and form.validate_on_submit():
            to_save = Product(request.form.to_dict())
            to_save.set_db_name()
            g.db.api_settings.update(
                {}, {
                    '$set': {
                        product: to_save.__dict__
                    }
                }
            )
            if to_save.active:
                g.db.api_settings.update(
                    {}, {
                        '$addToSet': {'active_products': product}
                    }
                )
            else:
                g.db.api_settings.update(
                    {}, {
                        '$pull': {'active_products': product}
                    }
                )

            flash('Product was successfully updated', 'success')
            return redirect('/%s/manage' % product)
        else:
            if request.method == 'POST':
                flash('Form was not saved successfully', 'error')

            return render_template(
                'manage/manage_product.html',
                title=title,
                form=form,
                product=product_data,
                post_url=post_url
            )

    @route('/<product>/manage/api')
    def manage_api_calls(self, product):
        found_product = self.retrieve_product(product)
        if type(found_product) is str:
            flash(
                'Could not find product, please check the URL and try again',
                'error'
            )
            return redirect(url_for('index'))

        product_url = "/%s/manage/api" % product
        try:
            api_commands = getattr(g.db, found_product.db_name).find().sort(
                [
                    ['tested', pymongo.DESCENDING],
                    ['title', pymongo.ASCENDING]
                ]
            )
        except:
            api_commands = []

        return render_template(
            'manage/manage_api_calls.html',
            title="%s - API Calls" % found_product.title,
            api_commands=api_commands,
            product_url=product_url
        )

    @route('/<product>/manage/api/add', methods=['GET', 'POST'])
    @route('/<product>/manage/api/edit/<api_id>', methods=['GET', 'POST'])
    def manage_add_edit_call(self, product, api_id=None):
        edit, count, title = False, 1, 'Add API Call'
        api_settings = g.db.api_settings.find_one()
        found_product = self.retrieve_product(product)
        if type(found_product) is str:
            flash('Product not found, please check the URL and try again')
            return redirect(url_for('index'))

        if api_id:
            found_call = self.retrieve_api_call(found_product, api_id)
            if not found_call:
                flash('API Call was not found', 'error')
                return redirect('/%s/manage/api' % product)

            title = 'Edit API Call'
            edit = True
            post_url = "/%s/manage/api/edit/%s" % (product, api_id)
            form = global_helper.generate_edit_call_form(
                found_product,
                found_call,
                api_id
            )
        else:
            post_url = "/%s/manage/api/add" % product
            form = global_helper.add_fields_to_form(count)
            for i in range(count):
                temp = getattr(form, 'variable_%i' % i)
                temp.form.id_value.data = i

        form.verb.choices = [
            (verb.get('name'), verb.get('name'))
            for verb in api_settings.get('verbs')
        ]
        form.product.data = product
        if request.method == 'POST' and form.validate_on_submit():
            api_call = Call(request.form.to_dict())
            api_call.variables = global_helper.get_vars_for_call(
                list(request.form.iterlists())
            )
            if api_id:
                getattr(g.db, found_product.db_name).update(
                    {
                        '_id': ObjectId(api_id)
                    }, {
                        '$set': api_call.__dict__
                    }
                )
                flash('API Call was successfully updated', 'success')
            else:
                try:
                    getattr(g.db, found_product.db_name).insert(
                        api_call.__dict__
                    )
                    flash('API Call was added successfully', 'success')
                except:
                    flash(
                        'There was an issue storing the API Call. Check '
                        'the product and ensure the db_name is specified',
                        'error'
                    )

            return redirect('/%s/manage/api' % product)
        else:
            if request.method == 'POST':
                flash(
                    'Form validation error, please check the '
                    'form and try again',
                    'error'
                )

            return render_template(
                'manage/manage_call_add_edit.html',
                title=title,
                form=form,
                count=count,
                edit=edit,
                post_url=post_url,
                cancel_return='/%s/manage/api' % product,
            )

    @route('/<product>/manage/api/<action>/<api_id>')
    def manage_api_actions(self, product, action, api_id):
        action_map = {'delete': True, 'confirm': True, 'unconfirm': False}
        found_product = self.retrieve_product(product)
        if type(found_product) is not str:
            if action in action_map:
                if getattr(g.db, found_product.db_name).find_one(
                    {'_id': ObjectId(api_id)}
                ):
                    if action == 'delete':
                        getattr(g.db, found_product.db_name).remove(
                            {'_id': ObjectId(api_id)}
                        )
                        message = 'API call was successfully removed'
                    else:
                        getattr(g.db, found_product.db_name).update(
                            {
                                '_id': ObjectId(api_id)
                            }, {
                                '$set': {
                                    'tested': action_map.get(action)
                                }
                            }
                        )
                        message = 'API call was successfully updated'
                else:
                    flash(
                        'API call was not found and nothing removed',
                        'error'
                    )
                    return redirect('/%s/manage/api' % product)

                flash(message, 'success')
                return redirect('/%s/manage/api' % product)
            else:
                message = 'Invalid action provided, so no action taken'
        else:
            message = 'Product was not found, so no action taken'

        flash(message, 'error')
        return redirect('/%s/manage/api' % product)

    def retrieve_product(self, product):
        temp_product = g.db.api_settings.find_one()
        if temp_product and temp_product.get(product):
            return Product(temp_product.get(product))

        return str(product)

    def retrieve_api_call(self, product, api_id):
        temp_call = getattr(g.db, product.db_name).find_one(
            {'_id': ObjectId(api_id)}
        )
        if temp_call:
            return Call(temp_call)

        return temp_call


ProductsView.register(app)
