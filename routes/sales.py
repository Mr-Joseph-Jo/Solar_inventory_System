from flask import Blueprint, render_template, request, redirect
from flask_login import login_required, current_user
from db import get_db
from datetime import datetime
from utils.invoice_generator import generate_invoice

sales_bp = Blueprint("sales", __name__, url_prefix="/sales")


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


def generate_invoice_no():
    return f"SOL-{datetime.now().strftime('%Y%m%d%H%M%S')}"


@sales_bp.route("/", methods=["GET", "POST"])
@login_required
def create_sale():
    if current_user.role not in ["owner", "admin", "sales"]:
        return "Access denied"

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT * FROM inventory_items WHERE quantity > 0")
    items = cur.fetchall()

    if request.method == "POST":
        item_id = int(request.form["item_id"])
        qty = int(request.form["quantity"])
        gst_applied = request.form.get("gst") == "yes"

        cur.execute("SELECT * FROM inventory_items WHERE id=%s", (item_id,))
        item = cur.fetchone()

        if not item or item["quantity"] < qty:
            return "Insufficient stock"

        subtotal = item["price"] * qty
        gst_amount = (subtotal * item["gst_rate"] / 100) if gst_applied else 0
        total = subtotal + gst_amount

        invoice_no = generate_invoice_no()
        invoice_path = f"invoices/{datetime.now().year}/{invoice_no}.pdf"

        try:
            cur.execute("""
                INSERT INTO sales
                (invoice_no, sold_by, gst_applied, subtotal, gst_amount, total_amount, invoice_file)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                invoice_no,
                current_user.id,
                gst_applied,
                subtotal,
                gst_amount,
                total,
                invoice_path
            ))

            sale_id = cur.lastrowid

            cur.execute("""
                INSERT INTO sale_items
                (sale_id, item_id, quantity, unit_price, gst_rate, gst_amount, line_total)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                sale_id,
                item_id,
                qty,
                item["price"],
                item["gst_rate"],
                gst_amount,
                total
            ))

            cur.execute("""
                UPDATE inventory_items
                SET quantity = quantity - %s
                WHERE id = %s
            """, (qty, item_id))

            db.commit()

        except Exception as e:
            db.rollback()
            return f"Sale failed: {e}"

        cur.execute("SELECT * FROM company_settings WHERE id=1")
        company = cur.fetchone()

        generate_invoice(
            invoice_no,
            company,
            {"subtotal": subtotal, "gst_amount": gst_amount, "total_amount": total},
            item,
            qty,
            gst_applied
        )

        log_action(
            current_user,
            "Sale created",
            invoice_no
        )

        return redirect("/sales")

    return render_template(
        "sales.html",
        items=items,
        role=current_user.role
    )
