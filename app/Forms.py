from db import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError


class RegisterForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(min=2, max=69)],
                       render_kw={"placeholder": "PSEUDONYM", "data-desc": "PSEUDONYM"})
    password = PasswordField(validators=[InputRequired(), Length(min=2, max=69)],
                             render_kw={"placeholder": "PASSWORD", "data-desc": "PASSWORD"})
    submit = SubmitField('REGISTER', render_kw={"data-letters": "REGISTER"})

    def validate_username(self, name):
        existing_user_username = User.query.filter_by(name=name.data).first()
        if existing_user_username:
            raise ValidationError('That pseudonym is already used.')


class LoginForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(min=2, max=69)], render_kw={"placeholder": "PSEUDONYM"})
    password = PasswordField(validators=[InputRequired(), Length(min=2, max=69)], render_kw={"placeholder": "PASSWORD"})
    submit = SubmitField('SIGN IN', render_kw={"data-letters": "SIGN IN"})
