from datetime import datetime, timedelta

from flask_apscheduler import APScheduler

from app import app, db

scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()
TIME_TO_LIVE = 42  # in minutes


@scheduler.task('cron', id='clear_old_visitor_addrs', minute='*')  # call every minute
def clear_old_visitor_addrs():
    with app.app_context():
        from db import SharedAddresses
        threshold_time = datetime.utcnow() - timedelta(minutes=TIME_TO_LIVE)
        SharedAddresses.query.filter_by(user=0).filter(SharedAddresses.last_updated < threshold_time).delete()
        db.session.commit()
