from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, PasswordField, FileField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField


# create post form
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = CKEditorField('Content', validators=[DataRequired()])
    picture = FileField('Upload picture', validators=[FileAllowed(['jpg', 'png'])])
    slug = StringField('Slug', validators=[DataRequired()])
    tags = StringField('Tags', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    searched = StringField('Searched', validators=[DataRequired()])
    submit = SubmitField('Submit')


class TagForm(FlaskForm):
    tag = StringField('Tag', validators=[DataRequired()])
    submit = SubmitField('Add tag')


class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')

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
