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


import re


def slug(string):
    if string:
        temp = re.sub(' +', ' ', string.lower())
        return re.sub(' ', '_', temp)
    return ''


class CustomSelectField(fields.SelectField):
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
    require_region = fields.BooleanField('Require Region:')
    active = fields.BooleanField('Active to Use:')


class SubmitFeedback(Form):
    category = fields.SelectField(
        choices=[
            ('', ''),
            ('not_working', 'Call not working'),
            ('deprecated', 'Deprecated'),
            ('doc_link', 'Documentation link broken'),
            ('missing', 'Missing call'),
            ('need_variable', 'Missing variable'),
            ('other', 'Other')
        ],
        validators=[validators.required()]
    )
    feedback = fields.TextAreaField(
        'Feedback:',
        validators=[validators.required()]
    )
    call_id = fields.HiddenField()
    product_db = fields.HiddenField()


class CallVariables(Form):
    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(CallVariables, self).__init__(*args, **kwargs)

    variable_name = fields.TextField('Variable Name:')
    field_type = CustomSelectField(
        'Field Type:',
        choices=[
            ('text', 'text'),
            ('integer', 'integer'),
            ('boolean', 'boolean'),
            ('float', 'decimal'),
            ('list', 'list'),
            ('text/integer', 'text/integer')
        ]
    )
    field_display = CustomSelectField(
        'Display Field:',
        choices=[
            ('TextField', 'Text Field'),
            ('SelectField', 'Select Field')
        ]
    )
    field_display_data = fields.TextAreaField('Select Data:')
    description = fields.TextField('Short Description:')
    required = fields.BooleanField('Required:')
    duplicate = fields.BooleanField('Allow Duplicate:', default=False)
    id_value = fields.HiddenField('id_value', default=0)


class ApiCall(Form):
    title = fields.TextField('Title:', validators=[validators.required()])
    short_description = fields.TextAreaField('Short Description:')
    verb = CustomSelectField(
        'Verb:',
        validators=[validators.required()],
        choices=[('', '')]
    )
    api_uri = fields.TextField('API URI:', validators=[validators.required()])
    doc_url = fields.TextField('Doc URL:')
    group = CustomSelectField(
        'Product Group:',
        choices=[('', ''), ('add_new_group', 'Add New Group')]
    )
    new_group = fields.TextField('Add Group:')
    add_to_header = fields.BooleanField('Add to Header?:')
    custom_header_key = fields.TextField('Header Key:')
    custom_header_value = fields.TextField('Header Value:')
    change_content_type = fields.BooleanField('Custom Content Type?:')
    custom_content_type = fields.TextField('Custom Content Type:')
    use_data = fields.BooleanField('Use Data?:')
    data_object = fields.TextAreaField('Data Object:')
    allow_filter = fields.BooleanField('Allow Filter?:')
    remove_token = fields.BooleanField('Remove Token:')
    remove_ddi = fields.BooleanField('Remove DDI:')
    remove_content_type = fields.BooleanField('Remove Content Type:')
    required_key = fields.BooleanField('Required Key:')
    required_key_name = fields.TextField('Key Name:')
    required_key_type = CustomSelectField(
        'Key Type:',
        choices=[
            ('', ''),
            ('dict', 'Dictionary'),
            ('list', 'List')
        ]
    )
    tested = fields.BooleanField('Tested?:')
    product = fields.HiddenField()
    id = fields.HiddenField()

    def validate_group(self, field):
        if self.group.data == 'add_new_group':
            if self.new_group.data in ['', None]:
                raise validators.ValidationError('No group specified')

            product = g.db.api_settings.find_one(
                {}, {self.product.data: 1, '_id': 0}
            )
            groups = product.get(self.product.data).get('groups')
            if not groups:
                groups = []

            for group in groups:
                if group.get('slug') == slug(self.new_group.data):
                    raise validators.ValidationError('Duplicate group')

    def validate_title(self, field):
        temp = self.title.data.strip().lower().title()
        found = getattr(g.db, self.product.data).find_one(
            {'title': temp}
        )
        if found and self.id.data != str(found.get('_id')):
            raise validators.ValidationError('Duplicate title found')

    def validate_api_uri(self, field):
        found = getattr(g.db, self.product.data).find_one(
            {
                'api_uri': self.api_uri.data.strip(),
                'verb': self.verb.data,
                'doc_url': self.doc_url.data
            }
        )
        if found and self.id.data != str(found.get('_id')):
            raise validators.ValidationError(
                'Duplicate URI, Verb, and Doc combination'
            )


class VerbSet(Form):
    name = fields.TextField('Verb:', validators=[validators.required()])
    active = fields.BooleanField('Active:', default=True)

    def validate_name(self, field):
        found = g.db.api_settings.find_one(
            {
                'verbs.name': self.name.data.upper()
            }
        )
        if found:
            raise validators.ValidationError('Duplicate verb')


class RegionSet(Form):
    name = fields.TextField('Name:', validators=[validators.required()])
    abbreviation = fields.TextField(
        'Abbreviation:',
        validators=[validators.required()]
    )

    def validate_abbreviation(self, field):
        found = g.db.api_settings.find_one(
            {
                'regions.abbreviation': self.abbreviation.data.upper()
            }
        )
        if found:
            raise validators.ValidationError('Duplicate abbreviation')

    def validate_name(self, field):
        regex = re.compile(
            '^%s$' % self.name.data,
            re.IGNORECASE
        )
        found = g.db.api_settings.find_one({'regions.name': regex})
        if found:
            raise validators.ValidationError('Duplicate name')
