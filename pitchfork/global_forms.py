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

from flask import g
from flask.ext.wtf import Form
from wtforms import fields, validators


class MySelectField(fields.SelectField):
    def pre_validate(self, form):
        """
        Overrides pre validation since all choices are static
        Adding elements dynamically requires this

        """
        pass


class ManageProduct(Form):
    title = fields.TextField('Title:', validators=[validators.required()])
    app_url = fields.TextField('App. URL:', validators=[validators.required()])
    us_api = fields.TextField(
        'US API Endpoint:',
        validators=[validators.required()]
    )
    uk_api = fields.TextField(
        'UK API Endpoint:',
        validators=[validators.required()]
    )
    doc_url = fields.TextField('Docs URL:', validators=[validators.required()])
    require_dc = fields.BooleanField('Require DC:')
    active = fields.BooleanField('Active to Use:')
    submit = fields.SubmitField('Submit')


class CallVariables(Form):
    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(CallVariables, self).__init__(*args, **kwargs)

    variable_name = fields.TextField('Variable Name:')
    field_type = MySelectField(
        'Field Type:',
        choices=[
            ('text', 'text'),
            ('integer', 'integer'),
            ('boolean', 'boolean'),
            ('float', 'decimal'),
            ('list', 'list')
        ]
    )
    field_display = MySelectField(
        'Display Field:',
        choices=[
            ('TextField', 'Text Field'),
            ('SelectField', 'Select Field')
        ]
    )
    field_display_data = fields.TextAreaField('Select Data:')
    description = fields.TextField('Short Description:')
    required = fields.BooleanField('Required:')
    id_value = fields.HiddenField('id_value')


class ApiCall(Form):
    title = fields.TextField('Title:', validators=[validators.required()])
    short_description = fields.TextAreaField('Short Description:')
    verb = MySelectField(
        'Verb:',
        validators=[validators.required()],
        choices=[('', '')]
    )
    api_uri = fields.TextField('API URI:', validators=[validators.required()])
    doc_url = fields.TextField('Doc URL:')
    add_to_header = fields.BooleanField('Add to Header?:')
    custom_header_key = fields.TextField('Header Key:')
    custom_header_value = fields.TextField('Header Value:')
    use_data = fields.BooleanField('Use Data?:')
    data_object = fields.TextAreaField('Data Object:')
    remove_token = fields.BooleanField('Remove Token:')
    remove_content_type = fields.BooleanField('Remove Content Type:')
    required_key = fields.BooleanField('Required Key:')
    required_key_name = fields.TextField('Key Name:')
    required_key_type = MySelectField(
        'Key Type:',
        choices=[
            ('', ''),
            ('dict', 'Dictionary'),
            ('list', 'List')
        ]
    )
    tested = fields.BooleanField('Tested?:')
