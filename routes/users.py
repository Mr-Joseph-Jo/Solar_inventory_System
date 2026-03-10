from flask import Blueprint, render_template, request, redirect
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from db import get_db

users_bp = Blueprint("users", __name__, url_prefix="/users")


def log_action(user, action, details):
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO audit_logs (user_id, role, action, details, ip_address)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        user.id,
        user.role,
        action,
        details,
        request.remote_addr
    ))
    db.commit()


@users_bp.route("/", methods=["GET", "POST"])
@login_required
def manage_users():
    if current_user.role != "owner":
        return "Access denied"

    db = get_db()
    cur = db.cursor(dictionary=True)

    if request.method == "POST":
        cur.execute("""
            INSERT INTO users (name, username, password_hash, role)
            VALUES (%s,%s,%s,%s)
        """, (
            request.form["name"],
            request.form["username"],
            generate_password_hash(request.form["password"]),
            request.form["role"]
        ))
        db.commit()

        log_action(
            current_user,
            "User created",
            request.form["username"]
        )

        return redirect("/users")

    cur.execute("SELECT id, name, username, role, active FROM users")
    users = cur.fetchall()

    return render_template(
        "users.html",
        users=users,
        role=current_user.role
    )


@users_bp.route("/toggle/<int:user_id>")
@login_required
def toggle_user(user_id):
    if current_user.role != "owner":
        return "Access denied"

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        UPDATE users
        SET active = NOT active
        WHERE id=%s AND role!='owner'
    """, (user_id,))
    db.commit()

    log_action(
        current_user,
        "User toggled",
        f"id={user_id}"
    )

    return redirect("/users")
