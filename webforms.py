from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


# create post form
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content',
                          validators=[DataRequired()],
                          widget=TextArea())
    slug = StringField('Slug', validators=[DataRequired()])
    # tags =
    submit = SubmitField('Submit')


# class UserForm(FlaskForm):
#     user_name = StringField('Enter name', validators=[DataRequired()])
#     user_email = StringField('Enter email', validators=[DataRequired()])
#     color = StringField('Enter Color')
#     password_hash = PasswordField('Enter Password',
#                                   validators=[
#                                       DataRequired(),
#                                       EqualTo('password_hash2',
#                                               message='Passwords Must Match!')])
#     password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
#     submit = SubmitField('Submit')
#
#
# class NameForm(FlaskForm):
#     name = StringField('Enter name', validators=[DataRequired()])
#     submit = SubmitField('Submit')
#
#
# class PasswordForm(FlaskForm):
#     email = StringField('Enter email', validators=[DataRequired()])
#     password_hash = PasswordField('Enter password', validators=[DataRequired()])
#     submit = SubmitField('Submit')
