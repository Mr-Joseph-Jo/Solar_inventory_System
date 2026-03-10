from flask import Blueprint, render_template, request, redirect
from flask_login import login_required, current_user
from db import get_db

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")


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


@inventory_bp.route("/")
@login_required
def inventory_list():
    if current_user.role not in ["owner", "admin"]:
        return "Access denied"

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT * FROM inventory_items")
    items = cur.fetchall()

    return render_template(
        "inventory.html",
        items=items,
        role=current_user.role
    )


@inventory_bp.route("/add", methods=["POST"])
@login_required
def add_item():
    if current_user.role not in ["owner", "admin"]:
        return "Access denied"

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        INSERT INTO inventory_items
        (name, category, hsn_code, unit, price, gst_rate, quantity)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        request.form["name"],
        request.form["category"],
        request.form["hsn"],
        request.form["unit"],
        request.form["price"],
        request.form["gst"],
        request.form["quantity"]
    ))

    db.commit()

    log_action(
        current_user,
        "Inventory item added",
        request.form["name"]
    )

    return redirect("/inventory")