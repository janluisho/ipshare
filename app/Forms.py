from app.SessionLessCSRF import SessionLessCSRF
from db import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, ValidationError


class SessionLessCSRFForm(FlaskForm):
    """
    This CSRF Token doesn't really protect anything for now.
    It isn't very safe as well. So assume there is no token.
    """
    class Meta:
        csrf = True
        csrf_class = SessionLessCSRF


class RegisterForm(SessionLessCSRFForm):
    name = StringField(
        validators=[
            InputRequired(),
            Length(min=2, max=69)],
        render_kw={
            "placeholder": "PSEUDONYM",
            "autocomplete": "off",
            "data-desc": "Choose a PSEUDONYM to be remembered by. It is recommend not using your real name.",
            "data-heading": "PSEUDONYM",
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
            "data-desc": "Choose a PASSWORD to login with. It is strongly recommended not to reuse an existing password.",
            "data-heading": "PASSWORD",
            "tabindex": 2
        }
    )
    remember = BooleanField(
        render_kw={
            "data-desc": "If you want to be remembered by the website. This will use a remember-me-Cookie.",
            "data-heading": "REMEMBER ME",
            "tabindex": 3
        }
    )
    submit_register = SubmitField(
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


class LoginForm(SessionLessCSRFForm):
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
    submit_login = SubmitField('SIGN IN', render_kw={"data-letters": "SIGN IN"})


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
    submit_name = SubmitField('CHANGE PSEUDONYM', render_kw={"data-letters": "CHANGE PSEUDONYM"})


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
    submit_password = SubmitField('CHANGE PASSWORD', render_kw={"data-letters": "CHANGE PASSWORD"})


class InvalidateTokensForm(FlaskForm):
    submit_invalidate = SubmitField('INVALIDATE TOKENS', render_kw={"data-letters": "INVALIDATE TOKENS"})


class SettingsForm(FlaskForm):
    remember = BooleanField(
        render_kw={
            "data-desc": "REMEMBER ME",
            "data-heading": "REMEMBER ME",
        }
    )
    submit_remember = SubmitField('UPDATE', render_kw={"data-letters": "UPDATE"})


class DeleteForm(FlaskForm):
    confirm_delete = BooleanField()
    submit_delete = SubmitField('DELETE', render_kw={"data-letters": "DELETE"})


class ShareNowForm(SessionLessCSRFForm):
    risks = BooleanField(
        render_kw={
            "data-desc": "Publicly sharing an IP address poses potential privacy and security risks, especially when it comes to geolocation tracking. IP addresses can be used to determine the approximate physical location of a device, making it possible for third parties to gain insights into a user's whereabouts. This information can be exploited for targeted advertising, surveillance, or even malicious activities. Therefore, individuals should exercise caution when sharing their IP addresses online to safeguard their privacy and mitigate the risk of unwanted geolocation tracking.",
            "data-heading": "Understanding the Risks",
            "tabindex": 1
        }
    )
    # use_cooky = BooleanField(
    #     render_kw={
    #         "data-desc": "Use Cooky",
    #         "data-heading": "Use Cooky",
    #         "tabindex": 2
    #     }
    # )
    submit_risks = SubmitField(
        label='SHARE NOW',
        render_kw={
            "data-letters": "SHARE NOW",
            "tabindex": 3
        }
    )