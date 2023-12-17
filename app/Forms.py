from db import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, ValidationError


class RegisterForm(FlaskForm):
    name = StringField(
        validators=[
            InputRequired(),
            Length(min=2, max=69)],
        render_kw={
            "placeholder": "PSEUDONYM",
            "autocomplete": "off",
            "data-desc": "PSEUDONYM",
            "data-heading": "PASSWORD",
            "tabindex": 1
        }
    )
    password = PasswordField(
        validators=[
            InputRequired(),
            Length(min=2, max=69)],
        render_kw={
            "placeholder": "PASSWORD",
            "autocomplete": "new-password",
            "data-desc": "PASSWORD",
            "data-heading": "PASSWORD",
            "tabindex": 2
        }
    )
    remember = BooleanField(
        render_kw={
            "data-desc": "REMEMBER ME",
            "data-heading": "REMEMBER ME",
            "tabindex": 3
        }
    )
    submit = SubmitField(
        label='REGISTER',
        render_kw={
            "data-letters": "REGISTER",
            "tabindex": 4
        }
    )

    def validate_username(self, name):
        existing_user_username = User.query.filter_by(name=name.data).first()
        if existing_user_username:
            raise ValidationError('That pseudonym is already used.')


class LoginForm(FlaskForm):
    name = StringField(
        validators=[
            InputRequired(),
            Length(min=2, max=69)
        ],
        render_kw={
            "placeholder": "PSEUDONYM",
            "autocomplete": "username"
        }
    )
    password = PasswordField(
        validators=[
            InputRequired(),
            Length(min=2, max=69)
        ],
        render_kw={
            "placeholder": "PASSWORD",
            "autocomplete": "current-password",
        }
    )
    submit = SubmitField('SIGN IN', render_kw={"data-letters": "SIGN IN"})


class ChangePseudonymForm(FlaskForm):
    name = StringField(
        validators=[
            InputRequired(),
            Length(min=2, max=69)
        ],
        render_kw={
            "placeholder": "PSEUDONYM",
            "autocomplete": "off",
        }
    )
    submit = SubmitField('CHANGE PSEUDONYM', render_kw={"data-letters": "CHANGE PSEUDONYM"})


class ChangePasswordForm(FlaskForm):
    password = PasswordField(
        validators=[
            InputRequired(),
            Length(min=2, max=69)
        ],
        render_kw={
            "placeholder": "PASSWORD",
            "autocomplete": "new-password",
        }
    )
    submit = SubmitField('CHANGE PASSWORD', render_kw={"data-letters": "CHANGE PASSWORD"})
