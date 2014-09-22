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
from wtforms import fields, validators


class BuildForm(Form):
    name = fields.TextField('Form Name:', validators=[validators.required()])
    submission_url = fields.TextField(
        'Submit URL:',
        validators=[validators.required()]
    )
    active = fields.BooleanField('Active:')
    system_form = fields.BooleanField('System Form?:')
    submit = fields.SubmitField('Submit')


class BuildCustomForm(Form):
    form_id = fields.HiddenField('Form ID:')
    name = fields.TextField('Name:', validators=[validators.required()])
    label = fields.TextField('Label:', validators=[validators.required()])
    field_type = fields.SelectField(
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
    field_choices = fields.TextAreaField('Choices:')
    description = fields.TextField('Description:')
    default = fields.BooleanField('Default Value:', default=False)
    default_value = fields.TextField('Default Value:')
    required = fields.BooleanField('Required:', default=False)
    active = fields.BooleanField('Active:', default=True)
    order = fields.HiddenField('Order')
    submit = fields.SubmitField('Submit')


class BaseForm(Form):
    pass


class ManagePermissions(Form):
    pass
