from flask import request
from db import get_db


def log_action(user, action, details=""):
    """Write an audit log entry for the current request."""
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO audit_logs (user_id, role, action, details, ip_address)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        user.id,
        user.role,
        action,
        details,
        request.remote_addr
    ))
    db.commit()
