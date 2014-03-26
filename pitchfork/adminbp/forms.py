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
    PasswordField, TextAreaField, SubmitField, HiddenField, RadioField,\
    SelectMultipleField
from wtforms import validators


class BuildForm(Form):
    name = TextField('Form Name:', validators=[validators.required()])
    submission_url = TextField(
        'Submit URL:',
        validators=[validators.required()]
    )
    active = BooleanField('Active:')
    system_form = BooleanField('System Form?:')
    submit = SubmitField('Submit')


class BuildCustomForm(Form):
    form_id = HiddenField('Form ID:')
    name = TextField('Name:', validators=[validators.required()])
    label = TextField('Label:', validators=[validators.required()])
    field_type = SelectField(
        'Type of Field:',
        validators=[validators.required()],
        choices=[
            ('', ''),
            ('TextField', 'Text Field'),
            ('TextAreaField', 'Text Area Field'),
            ('SelectField', 'Select Field'),
            ('SelectMultipleField', 'Select Multiple Field'),
            ('BooleanField', 'Boolean Field'),
            ('PasswordField', 'Password Field'),
            ('RadioField', 'Radio Field'),
            ('HiddenField', 'HiddenField'),
            ('SubmitField', 'Submit Field')
        ]
    )
    field_choices = TextAreaField('Choices:')
    description = TextField('Description:')
    default = BooleanField('Default Value:', default=False)
    default_value = TextField('Default Value:')
    required = BooleanField('Required:', default=False)
    active = BooleanField('Active:', default=True)
    order = HiddenField('Order')
    submit = SubmitField('Submit')


class BaseForm(Form):
    pass


class ManagePermissions(Form):
    pass
