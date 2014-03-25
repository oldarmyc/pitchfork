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
