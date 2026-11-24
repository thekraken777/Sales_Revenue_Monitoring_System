from models import db, ActivityLog


def log_activity(user, action, description):
    if user is None:
        return

    log = ActivityLog(
        user_id=user.id,
        username=user.username,
        action=action,
        description=description
    )

    db.session.add(log)
    db.session.commit()