import json
import re
from datetime import datetime

from app import db
from db import SharedAddresses


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


def public_address_info(addr):
    return [addr.address, format_last_updated(addr.last_updated)]


def user_address_info(addr):
    return [addr.device_name, addr.address, format_last_updated(addr.last_updated)]


def get_addresses(user, info_func):
    addrs = db.session.execute(
        db.select(SharedAddresses)
        .filter_by(user=user)
        .order_by(SharedAddresses.last_updated.desc())
        .limit(42)
    ).scalars()

    return json.dumps([info_func(addr) for addr in addrs])
