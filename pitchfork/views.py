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

from flask import (
    g, render_template, request, redirect, session, url_for,
    flash, jsonify, abort
)
from flask.ext.classy import FlaskView, route
from flask.ext.cloudadmin.decorators import check_perms
from models import Product, Call, Verb, Region, Favorite, Feedback
from bson.objectid import ObjectId


import helper
import forms
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
            return redirect('/')

        api_calls = helper.gather_api_calls(
            found_product,
            testing_calls,
            found_product.get_sorted_groups()
        )
        restrict_regions, regions = helper.check_for_product_regions(
            found_product
        )
        favorites = helper.gather_favorites(True)
        temp_groups = found_product.get_sorted_groups()
        temp_groups.insert(0, '')
        feedback_form = forms.SubmitFeedback()
        return render_template(
            'product_front.html',
            api_calls=api_calls,
            api_settings=found_product,
            api_groups=temp_groups,
            regions=regions,
            title=found_product.title,
            api_process='/%s/api/call/process' % product,
            testing=testing_calls,
            require_region=found_product.require_region,
            restrict_regions=restrict_regions,
            favorites=favorites,
            feedback_form=feedback_form
        )

    """ Product API Call Fire """

    @route('/<product>/api/call/process', methods=['POST'])
    def execute_api_call(self, product):
        found_product = self.retrieve_product(product)
        if type(found_product) is str:
            flash('Product not found, please check the URL and try again')
            return redirect('/')

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
            return redirect('/')

        """ Retrieve all of the elements for the call """
        api_url, header, data_package = helper.generate_vars_for_call(
            found_product,
            api_call,
            request
        )

        """ Send off the request and retrieve the data elements """
        if request.json.get('mock'):
            response_headers, response_body, response_code = None, None, None
            request_headers = helper.pretty_format_data(header)
        else:
            request_headers, response_headers, response_body, response_code = (
                helper.process_api_request(
                    api_url,
                    request.json.get('api_verb'),
                    data_package,
                    header
                )
            )

        if (
            request.json.get('mock') is None and
            request.json.get('testing') == 'false'
        ):
            helper.log_api_call_request(
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
            api_url=helper.pretty_format_url(api_url),
            data_package=helper.pretty_format_data(data_package)
        )

    """ Product Management """

    @route('/<product>/manage', methods=['GET', 'POST'])
    def manage_settings(self, product):
        product_data = self.retrieve_product(product)
        if type(product_data) is str:
            title = "%s Manage Settings" % product.title()
            product_data = None
            form = forms.ManageProduct()
        else:
            title = "%s Manage Settings" % product_data.title
            form = forms.ManageProduct(obj=product_data)

        if request.method == 'POST' and form.validate_on_submit():
            to_save = Product(request.form.to_dict())
            if product_data and product_data.db_name:
                to_save.db_name = product_data.db_name
                to_save.groups = product_data.groups
            else:
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
            )

    @route('/<product>/manage/api')
    def manage_api_calls(self, product):
        found_product = self.retrieve_product(product)
        if type(found_product) is str:
            flash(
                'Could not find product, please check the URL and try again',
                'error'
            )
            return redirect('/')

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
            return redirect('/')

        if api_id:
            found_call = self.retrieve_api_call(found_product, api_id)
            if not found_call:
                flash('API Call was not found', 'error')
                return redirect('/%s/manage/api' % product)

            title = 'Edit API Call'
            edit = True
            post_url = "/%s/manage/api/edit/%s" % (product, api_id)
            form, count = helper.generate_edit_call_form(
                found_product,
                found_call,
                api_id
            )
        else:
            post_url = "/%s/manage/api/add" % product
            form = helper.add_fields_to_form(count)
            for i in range(count):
                temp = getattr(form, 'variable_%i' % i)
                temp.form.id_value.data = i

        form.verb.choices = [
            (verb.get('name'), verb.get('name'))
            for verb in api_settings.get('verbs')
        ]
        form.group.choices = helper.generate_group_choices(found_product)
        form.product.data = product
        if request.method == 'POST' and form.validate_on_submit():
            api_call = Call(request.form.to_dict())
            api_call.variables = helper.get_vars_for_call(
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

    @route('/<product>/groups/<group>/<action>')
    def group_actions(self, product, group, action):
        action_map = ['promote', 'demote']
        found_product = self.retrieve_product(product)
        if type(found_product) is not str:
            if action in action_map:
                found = g.db.api_settings.find_one(
                    {
                        '%s.groups.slug' % product: group
                    }, {
                        '%s.groups.$' % product: 1
                    }
                )
                if found:
                    old_position = (
                        found.get(product).get('groups')[0].get('order')
                    )
                    if action == 'promote':
                        count = -1
                    elif action == 'demote':
                        count = 1

                    helper.change_group_order(
                        found_product.groups,
                        old_position + count,
                        old_position,
                        group,
                        product
                    )
                    return render_template(
                        'manage/_product_groups.html',
                        product=self.retrieve_product(product)
                    )
        abort(400)

    @route('/<product>/favorites/<action>', methods=['POST'])
    def favorites_action(self, product, action):
        actions = ['add', 'remove']
        if action not in actions:
            abort(404)

        found_product = self.retrieve_product(product)
        if type(found_product) is not str:
            db_name = found_product.db_name
            api_call = getattr(g.db, db_name).find_one(
                {
                    '_id': ObjectId(request.json.get('call_id'))
                }
            )
            if not api_call:
                abort(404)

            user_favorites = g.db.favorites.find_one(
                {
                    'username': session.get('username')
                }
            )
            if not user_favorites and action == 'add':
                user_favorites = {'username': session.get('username')}
            elif user_favorites is None:
                return jsonify(code=200)

            favorite = Favorite(user_favorites)
            if action == 'add':
                favorite.add_to_favorites(
                    request.json.get('call_id'),
                    db_name,
                    found_product.app_url,
                    session.get('username')
                )
            elif action == 'remove':
                favorite.remove_favorite(
                    request.json.get('call_id'),
                    session.get('username')
                )

            return jsonify(code=200)
        abort(404)

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


class MiscView(FlaskView):
    decorators = [check_perms(request)]
    route_base = '/'

    def index(self):
        call_favorites = helper.gather_favorites()
        favorites = helper.gather_favorites(True)
        restrict_regions, regions = helper.check_for_product_regions()
        feedback_form = forms.SubmitFeedback()
        return render_template(
            'index.html',
            api_calls=call_favorites,
            favorites=favorites,
            restrict_regions=restrict_regions,
            testing=False,
            regions=regions,
            using_favorites=True,
            feedback_form=feedback_form
        )

    @route('/history')
    @check_perms(request)
    def history(self):
        active_products = None
        api_settings = g.db.api_settings.find_one()
        if api_settings:
            active_products = api_settings.get('active_products')

        history = helper.gather_history()
        return render_template(
            'history.html',
            history=history,
            api_settings=api_settings,
            active_products=active_products
        )

    @route('/favorites')
    def favorites(self):
        call_favorites = helper.gather_favorites()
        favorites = helper.gather_favorites(True)
        restrict_regions, regions = helper.check_for_product_regions()
        feedback_form = forms.SubmitFeedback()
        return render_template(
            'favorites.html',
            api_calls=call_favorites,
            favorites=favorites,
            restrict_regions=restrict_regions,
            testing=False,
            regions=regions,
            using_favorites=True,
            feedback_form=feedback_form
        )


class FeedbackView(FlaskView):
    decorators = [check_perms(request)]
    route_base = '/feedback'

    def index(self):
        if session.get('role') == 'administrators':
            feedback = g.db.feedback.find({'complete': False})
            return render_template(
                'feedback.html',
                feedback=feedback
            )
        else:
            flash(
                'You do not have the correct permissions to access this page',
                'error'
            )
            return redirect('/')

    def post(self):
        try:
            feedback = Feedback(request.json)
            g.db.feedback.insert(feedback.__dict__)
        except:
            abort(400)

        return jsonify(code=200)

    def put(self):
        if session.get('role') == 'administrators':
            try:
                g.db.feedback.update(
                    {
                        '_id': ObjectId(request.json.get('feedback_id'))
                    }, {
                        '$set': {'complete': True}
                    }
                )
                return jsonify(code=200)
            except:
                abort(400)
        else:
            abort(404)


class GlobalManageView(FlaskView):
    decorators = [check_perms(request)]
    route_base = '/manage'

    @route('/verbs', methods=['GET', 'POST'])
    def define_available_verbs(self):
        api_settings = g.db.api_settings.find_one()
        form = forms.VerbSet()
        if request.method == 'POST' and form.validate_on_submit():
            verb = Verb(request.form)
            g.db.api_settings.update(
                {
                    '_id': api_settings.get('_id')
                }, {
                    '$push': {
                        'verbs': verb.__dict__
                    }
                }
            )
            flash('Verb successfully added to system', 'success')
            return redirect(url_for('GlobalManageView:define_available_verbs'))
        else:
            if request.method == 'POST':
                flash(
                    'There was a form validation error, please '
                    'check the required values and try again.',
                    'error'
                )

        return render_template(
            'manage/manage_verbs.html',
            form=form,
            api_settings=api_settings
        )

    @route('/regions', methods=['GET', 'POST'])
    def define_available_regions(self):
        api_settings = g.db.api_settings.find_one()
        form = forms.RegionSet()
        if request.method == 'POST' and form.validate_on_submit():
            region = Region(request.form)
            if api_settings.get('regions'):
                g.db.api_settings.update(
                    {
                        '_id': api_settings.get('_id')
                    }, {
                        '$push': {
                            'regions': region.__dict__
                        }
                    }
                )
            else:
                g.db.api_settings.update(
                    {
                        '_id': api_settings.get('_id')
                    }, {
                        '$set': {
                            'regions': [region.__dict__]
                        }
                    }
                )
            flash('Region successfully added to system', 'success')
            return redirect(
                url_for('GlobalManageView:define_available_regions')
            )
        else:
            if request.method == 'POST':
                flash(
                    'There was a form validation error, please '
                    'check the required values and try again.',
                    'error'
                )

            return render_template(
                'manage/manage_regions.html',
                form=form,
                api_settings=api_settings
            )

    @route('/<key>/<action>/<value>')
    def data_type_actions(self, key, action, value):
        actions = ['activate', 'deactivate', 'delete']
        maps = {
            'verbs': {
                'search': 'verbs.name',
                'change': 'verbs.$.active',
                'redirect': '/manage/verbs'
            },
            'regions': {
                'search': 'regions.abbreviation',
                'redirect': '/manage/regions'
            }
        }
        if maps.get(key):
            work = maps.get(key)
            if action in actions:
                found = g.db.api_settings.find_one(
                    {
                        work.get('search'): value
                    }
                )
                if found:
                    if action == 'delete':
                        keys = work.get('search').split('.')
                        change = {'$pull': {keys[0]: {keys[1]: value}}}
                    else:
                        if action == 'activate':
                            change = {'$set': {work.get('change'): True}}
                        elif action == 'deactivate':
                            change = {'$set': {work.get('change'): False}}

                    g.db.api_settings.update(
                        {
                            work.get('search'): value
                        },
                        change
                    )
                    flash(
                        '%s was %sd successfully' % (
                            value.title(),
                            action
                        ),
                        'success'
                    )
                else:
                    flash(
                        '%s was not found so no action taken' % value.title(),
                        'error'
                    )
            else:
                flash('Invalid action given so no action taken', 'error')
            return redirect(work.get('redirect'))
        else:
            flash('Invalid data key given so no action taken', 'error')
            return redirect('/')
