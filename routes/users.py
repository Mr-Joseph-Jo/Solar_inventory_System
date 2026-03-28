from flask import Blueprint, render_template, request, redirect, flash, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from db import get_db
from utils.audit import log_action

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/", methods=["GET", "POST"])
@login_required
def manage_users():
    if current_user.role != "owner":
        abort(403)

    db = get_db()
    cur = db.cursor(dictionary=True)

    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role     = request.form.get("role", "")

        errors = []
        if not name:
            errors.append("Full name is required.")
        if not username:
            errors.append("Username is required.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if role not in ("admin", "sales"):
            errors.append("Invalid role selected.")

        if errors:
            for e in errors:
                flash(e, "error")
            return redirect("/users")

        try:
            cur.execute("""
                INSERT INTO users (name, username, password_hash, role)
                VALUES (%s,%s,%s,%s)
            """, (name, username, generate_password_hash(password), role))
            db.commit()
            log_action(current_user, "User created", username)
            flash(f"User '{username}' created successfully.", "success")
        except Exception as e:
            db.rollback()
            # MySQL error 1062 = duplicate entry
            if hasattr(e, "errno") and e.errno == 1062:
                flash(f"Username '{username}' is already taken.", "error")
            else:
                flash("Failed to create user. Please try again.", "error")

        return redirect("/users")

    cur.execute("SELECT id, name, username, role, active FROM users")
    users = cur.fetchall()

    return render_template(
        "users.html",
        users=users,
        role=current_user.role
    )


@users_bp.route("/toggle/<int:user_id>", methods=["POST"])
@login_required
def toggle_user(user_id):
    if current_user.role != "owner":
        abort(403)

    db = get_db()
    cur = db.cursor()
    cur.execute("""
        UPDATE users SET active = NOT active
        WHERE id=%s AND role != 'owner'
    """, (user_id,))
    db.commit()

    log_action(current_user, "User toggled", f"id={user_id}")
    flash("User status updated.", "success")
    return redirect("/users")
