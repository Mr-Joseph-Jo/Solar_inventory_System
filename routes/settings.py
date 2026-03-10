from flask import Blueprint, render_template, request, redirect
from flask_login import login_required, current_user
from db import get_db

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if current_user.role not in ["owner", "admin"]:
        return "Access denied"

    db = get_db()
    cur = db.cursor(dictionary=True)

    if request.method == "POST":
        cur.execute("""
            UPDATE company_settings
            SET company_name=%s, gstin=%s, address=%s, phone=%s, email=%s
            WHERE id=1
        """, (
            request.form["company_name"],
            request.form["gstin"],
            request.form["address"],
            request.form["phone"],
            request.form["email"]
        ))
        db.commit()
        return redirect("/settings")

    cur.execute("SELECT * FROM company_settings WHERE id=1")
    data = cur.fetchone()

    return render_template(
        "settings.html",
        data=data,
        role=current_user.role
    )
