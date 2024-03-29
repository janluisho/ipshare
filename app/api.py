import urllib
from uuid import UUID

import jwt
from flask import request, Blueprint
from flask_login import login_required, current_user
from flask_socketio import emit
from sqlalchemy import func

from app import app, limiter, db
from app.utils import validate_address, get_addresses, user_address_info
from db import SharedAddresses, User

api_views = Blueprint('api_views', __name__, template_folder='templates')


def authorize_and_decode():
    """
    Authorize and decode jwt token
    :return: Success, decoded or error message
    """
    if 'Authorization' not in request.headers:
        return False, ("Header is missing Authorization", 401)

    if not request.headers.get('Authorization').startswith("Bearer "):
        return False, ("Authorization should start with 'Bearer '", 401)

    token = request.headers.get('Authorization')[7:]  # cut "Bearer "

    try:
        decoded = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms="HS256")
    except jwt.exceptions.InvalidSignatureError:
        return False, ("Authorization failed Invalid Signature", 401)
    except jwt.exceptions.DecodeError:
        return False, ("Authorization Decoding Error", 401)

    return True, decoded


@api_views.route('/', methods=['GET'])
@limiter.limit("1337 per day")
def apiv1_get():
    success, decoded_or_error = authorize_and_decode()
    if not success:
        return decoded_or_error  # error
    else:
        decoded = decoded_or_error
        user = User.query.filter_by(alternative_id=UUID(hex=decoded["user"]).bytes).first()

        if user is None:
            return "Authorization failed Invalid Token", 401

        addr = SharedAddresses.query.filter_by(user=user.id, device_name=decoded["device_name"]).first()

        if addr is None:
            return f"{decoded['device_name']} Not Found", 404

        return addr.address, 200


@api_views.route('/', methods=['PUT'])
@limiter.limit("1337 per day")
def apiv1_put():
    success, decoded_or_error = authorize_and_decode()
    if not success:
        return decoded_or_error  # error
    else:
        decoded = decoded_or_error
        user = User.query.filter_by(alternative_id=UUID(hex=decoded["user"]).bytes).first()

        if user is None:
            return "Authorization failed Invalid Token", 401

        addr = SharedAddresses.query.filter_by(user=user.id, device_name=decoded["device_name"]).first()

        if addr is None:
            addr = SharedAddresses(
                user=user.id,
                device_name=decoded["device_name"],
                address=validate_address(request.data.decode("UTF-8")),
                last_updated=func.now()
            )
            db.session.add(addr)
            db.session.commit()
            emit("user table", get_addresses(user.id, user_address_info),
                 broadcast=True, namespace='/', to=user.id)

            return "", 201
        else:
            addr.address = validate_address(request.data.decode("UTF-8"))
            db.session.commit()
            emit("user table", get_addresses(user.id, user_address_info),
                 broadcast=True, namespace='/', to=user.id)

            return "", 200


@api_views.route('/', methods=['DELETE'])
@limiter.limit("420 per day")
def apiv1_delete():
    success, decoded_or_error = authorize_and_decode()
    if not success:
        return decoded_or_error  # error
    else:
        decoded = decoded_or_error
        user = User.query.filter_by(alternative_id=UUID(hex=decoded["user"]).bytes).first()

        if user is None:
            return "Authorization failed Invalid Token", 401

        addr = SharedAddresses.query.filter_by(user=user.id, device_name=decoded["device_name"]).first()

        if addr is None:
            return "", 404
        else:
            db.session.delete(addr)
            db.session.commit()

            emit("user table", get_addresses(user.id, user_address_info),
                 broadcast=True, namespace='/', to=user.id)

            return "", 200


@api_views.route('/token/<path:device_name>', methods=['GET'])
@login_required
@limiter.limit("1337 per day")
def get_token(device_name):
    if current_user.is_authenticated:
        return jwt.encode({
                "user": current_user.alternative_id.hex(),
                "device_name": urllib.parse.unquote_plus(device_name)
            },
            app.config['JWT_SECRET_KEY'],
            algorithm="HS256"
            ), 200
    return "", 401
