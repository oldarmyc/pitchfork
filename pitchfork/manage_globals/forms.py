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


class VerbSet(Form):
    name = fields.TextField('Verb:', validators=[validators.required()])
    active = fields.BooleanField('Active:')
    submit = fields.SubmitField('Submit')


class RegionSet(Form):
    name = fields.TextField('Name:', validators=[validators.required()])
    abbreviation = fields.TextField(
        'Abbreviation:',
        validators=[validators.required()]
    )
    submit = fields.SubmitField('Submit')
