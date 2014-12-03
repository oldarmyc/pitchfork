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

import re
import helper


def nl2br(value):
    if value:
        _newline_re = re.compile(r'(?:\r\n|\r|\n)')
        return _newline_re.sub('<br>', value)


def tab2spaces(value):
    if value:
        text = re.sub('\t', '&nbsp;' * 4, value)
        return text


def unslug(value):
    text = re.sub('_', ' ', value)
    return text


def slug(value):
    text = re.sub('\s+', '_', value)
    return text


def check_regex(value):
    if re.match('variable', value):
        return True
    else:
        return False


def pretty_print_json(string):
    return json.dumps(
        string,
        sort_keys=False,
        indent=4,
        separators=(',', ':')
    )


def remove_slash(string):
    if string:
        return re.sub('\/', '', string)
