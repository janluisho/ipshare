from flask import request
from flask_login import current_user
from sqlalchemy import func

from app import app, db
from flask_socketio import SocketIO, emit, join_room, leave_room

from app.utils import get_addresses, user_address_info, public_address_info, validate_device_name, validate_address
from app.views import share_ip_now
from db import SharedAddresses

socketio = SocketIO(app, manage_session=False)  # ReadOnlySession


@socketio.on("connect")
def connect(_):
    if current_user.is_authenticated:
        emit("user authenticated")
        join_room(current_user.id)
        emit("user table", get_addresses(current_user.id, user_address_info))

    emit("public table", get_addresses(0, public_address_info))


@socketio.on("disconnect")
def disconnect():
    if current_user.is_authenticated:
        leave_room(current_user.id)
    else:
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            ip_addr = request.environ['REMOTE_ADDR']
        else:
            ip_addr = request.environ['HTTP_X_FORWARDED_FOR']  # if behind a proxy

        addr = SharedAddresses.query.filter_by(user=0, address=ip_addr).first()

        if addr is not None:
            db.session.delete(addr)
            db.session.commit()

    emit("public table", get_addresses(0, public_address_info), broadcast=True)


@socketio.on("now")
def now():
    share_ip_now()


@socketio.on("save")
def save(data):
    if "name" in data and "addr" in data:
        addr = SharedAddresses.query.filter_by(user=current_user.id, device_name=validate_device_name(data["name"])).first()
        if addr is None:
            addr = SharedAddresses(
                user=current_user.id,
                device_name=validate_device_name(data["name"]),
                address=validate_address(data["addr"]),
                last_updated=func.now()
            )
            db.session.add(addr)
        else:
            addr.address = validate_address(data["addr"])
        db.session.commit()

    if current_user.is_authenticated:
        emit("user table", get_addresses(current_user.id, user_address_info), broadcast=True)

    emit("public table", get_addresses(0, public_address_info))


@socketio.on("del")
def delete(data):
    if current_user.is_authenticated:
        if "name" in data and "addr" in data:
            addr = SharedAddresses.query.filter_by(user=current_user.id, device_name=validate_device_name(data["name"])).first()
            if addr is not None:
                db.session.delete(addr)
                db.session.commit()

        emit("user table", get_addresses(current_user.id, user_address_info))

    emit("public table", get_addresses(0, public_address_info))
