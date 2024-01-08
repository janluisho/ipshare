import json

from flask_login import current_user

from app import app, db
from flask_socketio import SocketIO, emit

from app.views import format_last_updated
from db import SharedAddresses

socketio = SocketIO(app, manage_session=False)  # ReadOnlySession


def user_address_info(addr):
    return [addr.address, format_last_updated(addr.last_updated)]


def public_address_info(addr):
    return [addr.device_name, addr.address, format_last_updated(addr.last_updated)]


def get_addresses(user, info_func):
    addrs = db.session.execute(
        db.select(SharedAddresses).filter_by(user=user).order_by(SharedAddresses.last_updated.desc()).limit(42)
    ).scalars()

    return json.dumps([info_func(addr) for addr in addrs])


@socketio.on("connect")
def test_connect(_):
    if current_user.is_authenticated:
        emit("user table", get_addresses(current_user.id, public_address_info))

    emit("public table", get_addresses(0, user_address_info))


# @socketio.on("refresh")
# def handle_refresh():
#     public_addrs = db.session.execute(
#         db.select(SharedAddresses).filter_by(user=0).order_by(SharedAddresses.last_updated.desc()).limit(42)
#     ).scalars()
#     print("refresh", public_addrs)
#     # emit("refresh")
