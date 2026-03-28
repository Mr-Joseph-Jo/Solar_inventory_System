from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user
from db import get_db

audit_bp = Blueprint("audit", __name__, url_prefix="/audit")

ACTIONS_PER_PAGE = 50


@audit_bp.route("/")
@login_required
def audit_log():
    if current_user.role not in ["owner", "admin"]:
        abort(403)

    db  = get_db()
    cur = db.cursor(dictionary=True)

    filter_user   = request.args.get("user_id", "").strip()
    filter_action = request.args.get("action",  "").strip()

    try:
        page = max(1, int(request.args.get("page", 1)))
    except ValueError:
        page = 1

    offset = (page - 1) * ACTIONS_PER_PAGE

    # Build WHERE clause
    where  = []
    params = []

    if filter_user:
        where.append("al.user_id = %s")
        params.append(filter_user)
    if filter_action:
        where.append("al.action LIKE %s")
        params.append(f"%{filter_action}%")

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    # Count total matching rows
    cur.execute(
        f"SELECT COUNT(*) AS total FROM audit_logs al {where_sql}",
        params or None
    )
    total       = cur.fetchone()["total"]
    total_pages = max(1, (total + ACTIONS_PER_PAGE - 1) // ACTIONS_PER_PAGE)

    # Fetch the page
    cur.execute(
        f"""
        SELECT
            al.id,
            al.action,
            al.details,
            al.role,
            al.ip_address,
            al.created_at,
            u.name     AS user_name,
            u.username AS username
        FROM audit_logs al
        LEFT JOIN users u ON u.id = al.user_id
        {where_sql}
        ORDER BY al.created_at DESC
        LIMIT %s OFFSET %s
        """,
        (params + [ACTIONS_PER_PAGE, offset]) if params else [ACTIONS_PER_PAGE, offset]
    )
    logs = cur.fetchall()

    cur.execute("SELECT id, name, username FROM users ORDER BY name")
    users = cur.fetchall()

    return render_template(
        "audit_log.html",
        logs=logs,
        users=users,
        filter_user=filter_user,
        filter_action=filter_action,
        page=page,
        total_pages=total_pages,
        total=total,
        role=current_user.role,
    )
