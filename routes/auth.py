from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from werkzeug.security import check_password_hash
from db import get_db
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET", "POST"])
def login():
    # Prevent logged-in users from seeing login page
    if current_user.is_authenticated:
        return redirect(url_for("dash.dashboard"))

    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM users WHERE username=%s AND active=1",
            (username,)
        )
        user = cur.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            login_user(User(user["id"], user["role"]))

            cur.execute("""
                INSERT INTO audit_logs (user_id, role, action, ip_address)
                VALUES (%s,%s,'Login',%s)
            """, (user["id"], user["role"], request.remote_addr))
            db.commit()

            return redirect(url_for("dash.dashboard"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


@auth_bp.route("/logout")
@login_required
def logout():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        INSERT INTO audit_logs (user_id, role, action, ip_address)
        VALUES (%s,%s,'Logout',%s)
    """, (
        current_user.id,
        current_user.role,
        request.remote_addr
    ))
    db.commit()

    logout_user()
    return redirect(url_for("auth.login"))
