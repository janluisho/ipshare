from uuid import UUID

import jwt
from flask import request
from sqlalchemy import func

from app import app, limiter, db
from app.utils import validate_address
from db import SharedAddresses, User


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


@app.route('/v1', methods=['GET'])
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
            return "", 404

        return addr.address, 200


@app.route('/v1', methods=['PUT'])
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
            return "", 201
        else:
            addr.address = validate_address(request.data.decode("UTF-8"))
            db.session.commit()
            return "", 200


@app.route('/v1', methods=['DELETE'])
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
            return "", 200
