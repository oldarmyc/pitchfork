
import re
import json


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
