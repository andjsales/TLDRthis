from flask_wtf import FlaskForm
from wtforms import StringField, URLField, PasswordField
from wtforms.validators import DataRequired, Length, Email


class SummarizeContent(FlaskForm):
    """
    TLDR form
    """
    title = StringField("Title: ")
    url = URLField("Site Url: ")


class LoginForm(FlaskForm):
    """
    Login form
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class SignupForm(FlaskForm):
    """
    Sign up form
    """
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])


class EditProfileForm(FlaskForm):
    """
    Edit profile form
    """
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
