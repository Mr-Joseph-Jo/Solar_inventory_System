from flask import Blueprint, render_template, send_file
from flask_login import login_required, current_user
from db import get_db
import os

invoices_bp = Blueprint("invoices", __name__, url_prefix="/invoices")


@invoices_bp.route("/")
@login_required
def invoice_list():
    db = get_db()
    cur = db.cursor(dictionary=True)

    if current_user.role == "sales":
        cur.execute("""
            SELECT s.invoice_no, s.created_at, s.total_amount,
                   s.gst_applied, s.invoice_file, u.name AS sold_by
            FROM sales s
            JOIN users u ON s.sold_by = u.id
            WHERE s.sold_by = %s
            ORDER BY s.created_at DESC
        """, (current_user.id,))
    else:
        cur.execute("""
            SELECT s.invoice_no, s.created_at, s.total_amount,
                   s.gst_applied, s.invoice_file, u.name AS sold_by
            FROM sales s
            JOIN users u ON s.sold_by = u.id
            ORDER BY s.created_at DESC
        """)

    invoices = cur.fetchall()

    return render_template(
        "invoices.html",
        invoices=invoices,
        role=current_user.role
    )


@invoices_bp.route("/download/<invoice_no>")
@login_required
def download_invoice(invoice_no):
    db = get_db()
    cur = db.cursor(dictionary=True)

    if current_user.role == "sales":
        cur.execute("""
            SELECT invoice_file FROM sales
            WHERE invoice_no=%s AND sold_by=%s
        """, (invoice_no, current_user.id))
    else:
        cur.execute("""
            SELECT invoice_file FROM sales
            WHERE invoice_no=%s
        """, (invoice_no,))

    sale = cur.fetchone()

    if not sale or not sale["invoice_file"]:
        return "Invoice not found"

    if not os.path.exists(sale["invoice_file"]):
        return "File missing"

    return send_file(sale["invoice_file"], as_attachment=True)
