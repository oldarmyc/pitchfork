from flask.ext.wtf import Form
from wtforms import TextField, SelectField, IntegerField, BooleanField,\
    PasswordField, TextAreaField, SubmitField, HiddenField, RadioField
from wtforms import validators


class VerbSet(Form):
    name = TextField('Verb:', validators=[validators.required()])
    active = BooleanField('Active:')
    submit = SubmitField('Submit')


class DCSet(Form):
    name = TextField('Name:', validators=[validators.required()])
    abbreviation = TextField(
        'Abbreviation:',
        validators=[validators.required()]
    )
    submit = SubmitField('Submit')
