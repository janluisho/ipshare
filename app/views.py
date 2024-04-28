from flask_socketio import emit

from app.Forms import ShareNowForm
from app.utils import format_last_updated, split_user_agent, get_addresses, user_address_info, public_address_info
from db import SharedAddresses
from flask import request, render_template, redirect, url_for, Blueprint
from flask_login import current_user
from sqlalchemy import func

from app import db, limiter

public_address_counter = 0

ip_share_views = Blueprint('ip_share_views', __name__, template_folder='templates')


def share_ip_now():
    global public_address_counter
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip_addr = request.environ['REMOTE_ADDR']
    else:
        ip_addr = request.environ['HTTP_X_FORWARDED_FOR']  # if behind a proxy

    if current_user.is_authenticated:
        device_name = split_user_agent(request.headers.get("User-Agent"))
        shared_addr = SharedAddresses.query.filter_by(user=current_user.id, device_name=device_name).first()

        if shared_addr is None:
            # create new device
            shared_addr = SharedAddresses(user=current_user.id, device_name=device_name, address=ip_addr,
                                          last_updated=func.now())
            db.session.add(shared_addr)
            db.session.commit()
        else:
            # update old device
            shared_addr.address = ip_addr
            shared_addr.last_updated = func.now()
            db.session.commit()
        emit("user table", get_addresses(current_user.id, user_address_info),
             broadcast=True, namespace='/', to=current_user.id)
    else:
        shared_addr = SharedAddresses.query.filter_by(user=0, address=ip_addr).first()
        if shared_addr is None:
            # create new device
            public_address_counter += 1
            shared_addr = SharedAddresses(user=0, device_name=str(public_address_counter), address=ip_addr,
                                          last_updated=func.now())
            db.session.add(shared_addr)
            db.session.commit()
        else:
            # update time
            shared_addr.last_updated = func.now()
            db.session.commit()
        emit("public table", get_addresses(0, public_address_info), broadcast=True, namespace='/')


@ip_share_views.route('/')
@limiter.limit("1337 per day")
def root():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip_addr = request.environ['REMOTE_ADDR']
    else:
        ip_addr = request.environ['HTTP_X_FORWARDED_FOR']  # if behind a prox

    return render_template(
        "index.html",
        ip_addr=ip_addr,
        user=current_user
    )


@ip_share_views.route('/now', methods=['GET', 'POST'])
@limiter.limit("10/minute", override_defaults=False)
def now():
    """Teilt Ip sofort"""
    if current_user.is_authenticated:
        share_ip_now()
        return redirect(url_for('ip_share_views.root'))
    else:
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            ip_addr = request.environ['REMOTE_ADDR']
        else:
            ip_addr = request.environ['HTTP_X_FORWARDED_FOR']  # if behind a prox

        form = ShareNowForm(meta={'csrf_context': ip_addr})

        if form.validate_on_submit():
            if form.risks.data:
                share_ip_now()
                return redirect(url_for('ip_share_views.root'))

        return render_template('now.html', form=form, user=current_user, ip_addr=ip_addr)


@ip_share_views.route('/impressum')
def impressum():
    """Impressum"""
    return render_template("impressum.html", user=current_user)

@ip_share_views.route('/datenschutzerklaerung')
def datenschutzerklaerung():
    """Datenschutzerklaerung"""
    return render_template("datenschutzerklaerung.html", user=current_user)
