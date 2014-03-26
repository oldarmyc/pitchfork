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

from flask.ext.wtf import Form
from wtforms import TextField, SelectField, IntegerField, BooleanField,\
    PasswordField, TextAreaField, SubmitField, HiddenField,\
    RadioField, FormField
from wtforms import validators


class MySelectField(SelectField):
    def pre_validate(self, form):
        """
        Overrides pre validation since all choices are static
        Adding elements dynamically requires this

        """
        pass


class ManageProduct(Form):
    title = TextField(
        'Title:',
        validators=[validators.required()]
    )
    app_url = TextField(
        'App. URL:',
        validators=[validators.required()]
    )
    url = TextField(
        'US API Endpoint:',
        validators=[validators.required()]
    )
    uk_url = TextField(
        'UK API Endpoint:',
        validators=[validators.required()]
    )
    doc_url = TextField(
        'Docs URL:',
        validators=[validators.required()]
    )
    require_dc = BooleanField('Require DC:')
    active = BooleanField('Active to Use:')
    submit = SubmitField('Submit')


class CallVariables(Form):
    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(CallVariables, self).__init__(*args, **kwargs)

    variable_name = TextField(
        'Variable Name:'
    )
    field_type = MySelectField(
        'Field Type:',
        choices=[
            ('text', 'text'),
            ('integer', 'integer'),
            ('boolean', 'boolean'),
            ('float', 'decimal')
        ]
    )
    field_display = MySelectField(
        'Display Field:',
        choices=[
            ('TextField', 'Text Field'),
            ('SelectField', 'Select Field')
        ]
    )
    field_display_data = TextAreaField('Select Data:')
    description = TextField(
        'Short Description:'
    )
    required = BooleanField('Required:')
    id_value = HiddenField('id_value')


class ApiCall(Form):
    title = TextField('Title:', validators=[validators.required()])
    short_description = TextAreaField('Short Description:')
    verb = SelectField('Verb:', validators=[validators.required()])
    api_uri = TextField('API URI:', validators=[validators.required()])
    doc_url = TextField('Doc URL:')
    add_to_header = BooleanField('Add to Header?:')
    custom_header_key = TextField('Header Key:')
    custom_header_value = TextField('Header Value:')
    use_data = BooleanField('Use Data?:')
    data_object = TextAreaField('Data Object:')
    remove_token = BooleanField('Remove Token:')
    required_key = BooleanField('Required Key:')
    required_key_name = TextField('Key Name:')
    required_key_type = MySelectField(
        'Key Type:',
        choices=[
            ('', ''),
            ('dict', 'Dictionary'),
            ('list', 'List')
        ]
    )
    tested = BooleanField('Tested?:')
