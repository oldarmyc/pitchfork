from flask.ext.wtf import Form
from wtforms import TextField, SelectField, IntegerField, BooleanField,\
    PasswordField, TextAreaField, SubmitField, HiddenField,\
    RadioField, FormField
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
            ('datetime', 'DateTime')
        ]
    )
    field_display = SelectField(
        'Display Field:',
        choices=[
            ('TextField', 'Text Field'),
            ('SelectField', 'Select Field')
        ]
    )
    field_display_data = TextAreaField('Select Data:')
    description = TextAreaField('Description:')
    searchable = BooleanField('Searchable:')
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
