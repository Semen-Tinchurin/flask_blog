from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, PasswordField, FileField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField


# create post form
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = CKEditorField('Content', validators=[DataRequired()])
    image = FileField('Upload image', validators=[FileAllowed(['jpg', 'png'])])
    slug = StringField('Slug', validators=[DataRequired()])
    tags = SelectMultipleField('Tags', coerce=int)
    submit = SubmitField('Submit')
    preview = SubmitField('Preview')


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


class LetterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email address', validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

# class UserForm(FlaskForm):
#     user_name = StringField('Enter name', validators=[DataRequired()])
#     user_email = StringField('Enter email', validators=[DataRequired()])
#     password_hash = PasswordField('Enter Password',
#                                   validators=[
#                                       DataRequired(),
#                                       EqualTo('password_hash2',
#                                               message='Passwords Must Match!')])
#     password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
#     submit = SubmitField('Submit')
