from flask_login import current_user

from app import app
from flask_socketio import SocketIO, emit, join_room

from app.utils import get_addresses, user_address_info, public_address_info
from app.views import share_ip_now

socketio = SocketIO(app, manage_session=False)  # ReadOnlySession


@socketio.on("connect")
def test_connect(_):
    if current_user.is_authenticated:
        join_room(current_user.id)
        emit("user table", get_addresses(current_user.id, user_address_info))

    emit("public table", get_addresses(0, public_address_info))


@socketio.on("now")
def now():
    share_ip_now()
