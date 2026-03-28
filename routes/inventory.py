from flask import Blueprint, render_template, request, redirect, flash, abort
from flask_login import login_required, current_user
from db import get_db
from utils.audit import log_action

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")


def get_tax_rates(cur):
    cur.execute("SELECT rate FROM gst_rates ORDER BY rate ASC")
    return [float(r["rate"]) for r in cur.fetchall()]


def validate_item_fields(form):
    errors = []
    name     = form.get("name",     "").strip()
    category = form.get("category", "").strip()
    price    = form.get("price",    "").strip()
    gst      = form.get("gst",      "").strip()
    quantity = form.get("quantity", "0").strip()

    if not name:
        errors.append("Item name is required.")
    if not category:
        errors.append("Category is required.")
    try:
        price = float(price)
        if price < 0: raise ValueError
    except ValueError:
        errors.append("Price must be a positive number.")
        price = None
    try:
        gst = float(gst)
        if not (0 <= gst <= 100): raise ValueError
    except ValueError:
        errors.append("GST must be a valid rate.")
        gst = None
    try:
        quantity = int(quantity)
        if quantity < 0: raise ValueError
    except ValueError:
        errors.append("Quantity must be a non-negative whole number.")
        quantity = None

    return errors, name, category, price, gst, quantity


@inventory_bp.route("/")
@login_required
def inventory_list():
    if current_user.role not in ["owner", "admin"]:
        abort(403)

    db  = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM inventory_items ORDER BY name")
    items = cur.fetchall()
    rates = get_tax_rates(cur)

    return render_template(
        "inventory.html",
        items=items,
        tax_rates=rates,
        role=current_user.role
    )


@inventory_bp.route("/add", methods=["POST"])
@login_required
def add_item():
    if current_user.role not in ["owner", "admin"]:
        abort(403)

    errors, name, category, price, gst, quantity = validate_item_fields(request.form)
    if errors:
        for e in errors:
            flash(e, "error")
        return redirect("/inventory")

    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            INSERT INTO inventory_items
            (name, category, hsn_code, unit, price, gst_rate, quantity)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            name, category,
            request.form.get("hsn",  "").strip(),
            request.form.get("unit", "").strip(),
            price, gst, quantity
        ))
        db.commit()
        log_action(current_user, "Inventory item added", name)
        flash(f"'{name}' added to inventory.", "success")
    except Exception:
        db.rollback()
        flash("Failed to add item. Please try again.", "error")

    return redirect("/inventory")


@inventory_bp.route("/edit/<int:item_id>", methods=["POST"])
@login_required
def edit_item(item_id):
    if current_user.role not in ["owner", "admin"]:
        abort(403)

    errors, name, category, price, gst, quantity = validate_item_fields(request.form)
    if errors:
        for e in errors:
            flash(e, "error")
        return redirect("/inventory")

    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute("SELECT name FROM inventory_items WHERE id=%s", (item_id,))
        item = cur.fetchone()
        if not item:
            flash("Item not found.", "error")
            return redirect("/inventory")

        cur.execute("""
            UPDATE inventory_items
            SET name=%s, category=%s, hsn_code=%s, unit=%s,
                price=%s, gst_rate=%s, quantity=%s
            WHERE id=%s
        """, (
            name, category,
            request.form.get("hsn",  "").strip(),
            request.form.get("unit", "").strip(),
            price, gst, quantity, item_id
        ))
        db.commit()
        log_action(current_user, "Inventory item edited", name)
        flash(f"'{name}' updated successfully.", "success")
    except Exception:
        db.rollback()
        flash("Failed to update item. Please try again.", "error")

    return redirect("/inventory")


@inventory_bp.route("/restock/<int:item_id>", methods=["POST"])
@login_required
def restock_item(item_id):
    if current_user.role not in ["owner", "admin"]:
        abort(403)

    try:
        add_qty = int(request.form.get("add_qty", 0))
        if add_qty <= 0: raise ValueError
    except ValueError:
        flash("Please enter a valid quantity greater than 0.", "error")
        return redirect("/inventory")

    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT name, quantity FROM inventory_items WHERE id=%s", (item_id,))
        item = cur.fetchone()
        if not item:
            flash("Item not found.", "error")
            return redirect("/inventory")

        cur.execute("""
            UPDATE inventory_items SET quantity = quantity + %s WHERE id=%s
        """, (add_qty, item_id))
        db.commit()

        new_qty = item["quantity"] + add_qty
        log_action(current_user, "Stock updated", f"{item['name']}: +{add_qty} (now {new_qty})")
        flash(f"Added {add_qty} units to '{item['name']}'. New stock: {new_qty}.", "success")
    except Exception:
        db.rollback()
        flash("Failed to update stock. Please try again.", "error")

    return redirect("/inventory")


@inventory_bp.route("/delete/<int:item_id>", methods=["POST"])
@login_required
def delete_item(item_id):
    if current_user.role not in ["owner", "admin"]:
        abort(403)

    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT name FROM inventory_items WHERE id=%s", (item_id,))
        item = cur.fetchone()
        if not item:
            flash("Item not found.", "error")
            return redirect("/inventory")

        cur.execute("SELECT COUNT(*) AS cnt FROM sale_items WHERE item_id=%s", (item_id,))
        if cur.fetchone()["cnt"] > 0:
            flash(
                f"'{item['name']}' cannot be deleted — it appears in existing sales. "
                "Set stock to 0 to hide it from new sales.",
                "error"
            )
            return redirect("/inventory")

        cur.execute("DELETE FROM inventory_items WHERE id=%s", (item_id,))
        db.commit()
        log_action(current_user, "Inventory item deleted", item["name"])
        flash(f"'{item['name']}' removed from inventory.", "success")
    except Exception:
        db.rollback()
        flash("Failed to delete item. Please try again.", "error")

    return redirect("/inventory")
