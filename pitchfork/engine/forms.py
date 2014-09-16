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
from wtforms import TextField, SelectField, BooleanField
from wtforms import TextAreaField, SubmitField
from wtforms import validators


class ReportFields(Form):
    field_name = TextField(
        'Field Name:',
        validators=[validators.required()]
    )
    data_type = SelectField(
        'Data Type:',
        validators=[validators.required()],
        choices=[
            ('', ''),
            ('text', 'Text'),
            ('integer', 'Integer'),
            ('boolean', 'Boolean'),
            ('datetime', 'DateTime'),
            ('user_select', 'User Select')
        ]
    )
    field_display = SelectField(
        'Display Field:',
        choices=[
            ('TextField', 'Text Field'),
            ('SelectField', 'Select Field'),
            ('BooleanField', 'Boolean Field'),
        ]
    )
    field_display_data = TextAreaField('Select Data:')
    field_display_label = TextField('Display Label:')
    description = TextAreaField('Description:')
    searchable = BooleanField('Searchable:')
    graphable = BooleanField('Generate Graph:')
    submit = SubmitField('Submit')


class ReportGlobal(Form):
    collection = TextField(
        'Collection Name:',
        validators=[validators.required()]
    )
    description = TextAreaField(
        'Description:',
        validators=[validators.required()]
    )
    enabled = BooleanField('Enabled:')
    submit = SubmitField('Submit')


class Reporting(Form):
    pass
