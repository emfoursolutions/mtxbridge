# ABOUTME: Authentication forms for login
# ABOUTME: Simple WTForms for username/password authentication

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """Login form for LDAP/AD authentication"""

    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=2, max=255)],
        render_kw={'placeholder': 'Enter your username'}
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Enter your password'}
    )

    remember_me = BooleanField('Remember Me')

    submit = SubmitField('Login')
