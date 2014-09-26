
import re


def utility_processor():
    def unslug(string):
        return re.sub('_', ' ', string)

    def parse_field_data(value):
        choices = re.sub('\r\n', ',', value)
        return choices.split(',')

    def slugify(data):
        temp_string = re.sub(' +', ' ', str(data.strip()))
        return re.sub(' ', '_', temp_string)

    return dict(
        parse_field_data=parse_field_data,
        unslug=unslug,
        slugify=slugify
    )
