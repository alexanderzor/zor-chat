from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import Required, Length


class JoinForm(Form):
    room = StringField('Room:', validators=[Required()])
    password = PasswordField('Password:', validators=[Required()])
    submit = SubmitField('Enter Chatroom')


class SearchForm(Form):
    room = StringField('Search a room:', validators=[Required()])
    submit = SubmitField('Search')


class EditProfileForm(Form):
    name = StringField('Real name:', validators=[Length(0, 64)])
    location = StringField('Location:', validators=[Length(0, 64)])
    about_me = TextAreaField('About me:')
    submit = SubmitField('Submit')