import re
from datetime import datetime
from db import SharedAddresses
from flask import request, render_template, redirect, url_for
from flask_login import current_user
from sqlalchemy import func

from app import app, db, limiter

public_address_counter = 0


def format_last_updated(last_updated):
    delta = datetime.utcnow() - last_updated
    days = delta.days
    seconds = delta.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        return f"{days} {'day' if days == 1 else 'days'} ago"
    elif hours > 0:
        return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
    elif minutes > 0:
        return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
    else:
        return f"{seconds} {'second' if seconds == 1 else 'seconds'} ago"


user_agent_regex = re.compile(r"\((.+?)\)|\S+")
def split_user_agent(user_agent):
    matches = user_agent_regex.finditer(user_agent)
    mozilla = next(matches).group()
    system_information = next(matches).group()
    gecko_version = next(matches).group()
    extensions = "".join([match.group() for match in matches])

    if "Windows" in system_information:
        system = "Windows"
    elif "Linux" in system_information:
        system = "Linux"
    elif "Macintosh" in system_information:
        system = "Macintosh"
    else:
        system = system_information

    if "Firefox" in extensions:
        browser = "Firefox"
    elif "Edg" in extensions:
        browser = "Edge"
    elif "OPR" in extensions:
        browser = "Opera"
    elif "Chrome" in extensions:
        browser = "Chrome"
    else:
        browser = ""

    return f"{browser} {system}"


@app.route('/')
@limiter.limit("1337 per day")
def root():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip_addr = request.environ['REMOTE_ADDR']
    else:
        ip_addr = request.environ['HTTP_X_FORWARDED_FOR']  # if behind a prox

    if current_user.is_authenticated:
        user_addrs = db.session.execute(
            db.select(SharedAddresses).filter_by(user=current_user.id).order_by(SharedAddresses.last_updated.desc())
        ).scalars()
    else:
        user_addrs = []

    public_addrs = db.session.execute(
        db.select(SharedAddresses).filter_by(user=0).order_by(SharedAddresses.last_updated.desc()).limit(42)
    ).scalars()

    return render_template(
        "index.html",
        ip_addr=ip_addr,
        user=current_user,
        user_addrs=user_addrs,
        public_addrs=public_addrs,
        format_last_updated=format_last_updated
    )


@app.route('/now')
@limiter.limit("10/minute", override_defaults=False)
def now():
    """Teilt Ip sofort"""
    global public_address_counter
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip_addr = request.environ['REMOTE_ADDR']
    else:
        ip_addr = request.environ['HTTP_X_FORWARDED_FOR']  # if behind a prox

    if current_user.is_authenticated:
        device_name = split_user_agent(request.headers.get("User-Agent"))
        shared_addr = SharedAddresses.query.filter_by(user=current_user.id, device_name=device_name).first()

        if shared_addr is None:
            # create new device
            shared_addr = SharedAddresses(user=current_user.id, device_name=device_name, address=ip_addr, last_updated=func.now())
            db.session.add(shared_addr)
            db.session.commit()
        else:
            # update old device
            shared_addr.address = ip_addr
            shared_addr.last_updated = func.now()
            db.session.commit()
    else:
        shared_addr = SharedAddresses.query.filter_by(user=0, address=ip_addr).first()
        if shared_addr is None:
            # create new device
            public_address_counter += 1
            shared_addr = SharedAddresses(user=0, device_name=str(public_address_counter), address=ip_addr, last_updated=func.now())
            db.session.add(shared_addr)
            db.session.commit()
        else:
            # update time
            shared_addr.last_updated = func.now()
            db.session.commit()

    return redirect(url_for('root'))


@app.route('/impressum')
def impressum():
    """Impressum"""
    return render_template("impressum.html", user=current_user)
