"""
Forms for User related things
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from bigbeta.models import User


class RegistrationForm(FlaskForm):
    """
    Form for Registration page
    """

    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign Up!')


    def validate_username(self, username):
        """
            Validates username doesn't already exist
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('User already exists :(')


    def validate_email(self, email):
        """
            Validates email doesn't already exist
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists :(')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picutre', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Account')


    def validate_username(self, username):
        """
            Validates username doesn't already exist
        """
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('User already exists :(')


    def validate_email(self, email):
        """
            Validates email doesn't already exist
        """
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already exists :(')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        """
            Validates email doesn't already exist
        """
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("Ain't no account with that email")


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Reset Password")
