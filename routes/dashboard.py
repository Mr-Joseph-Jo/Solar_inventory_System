from flask import Blueprint, render_template
from flask_login import login_required, current_user
from db import get_db

dash_bp = Blueprint("dash", __name__)


@dash_bp.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    cur = db.cursor(dictionary=True)

    # Summary stats
    cur.execute("SELECT COUNT(*) AS total_sales, COALESCE(SUM(total_amount),0) AS total_revenue FROM sales")
    row = cur.fetchone()

    cur.execute("SELECT COUNT(*) AS item_count FROM inventory_items")
    items = cur.fetchone()

    cur.execute("SELECT COUNT(*) AS low_stock FROM inventory_items WHERE quantity <= 5")
    low = cur.fetchone()

    stats = {
        "total_sales":   row["total_sales"],
        "total_revenue": float(row["total_revenue"]),
        "item_count":    items["item_count"],
        "low_stock":     low["low_stock"],
    }

    # Recent 5 sales
    if current_user.role == "sales":
        cur.execute("""
            SELECT s.invoice_no, s.created_at, s.total_amount, s.gst_applied,
                   i.name AS item_name
            FROM sales s
            LEFT JOIN sale_items si ON si.sale_id = s.id
            LEFT JOIN inventory_items i ON i.id = si.item_id
            WHERE s.sold_by = %s
            ORDER BY s.created_at DESC LIMIT 5
        """, (current_user.id,))
    else:
        cur.execute("""
            SELECT s.invoice_no, s.created_at, s.total_amount, s.gst_applied,
                   i.name AS item_name
            FROM sales s
            LEFT JOIN sale_items si ON si.sale_id = s.id
            LEFT JOIN inventory_items i ON i.id = si.item_id
            ORDER BY s.created_at DESC LIMIT 5
        """)

    recent_sales = cur.fetchall()

    return render_template(
        "dashboard.html",
        role=current_user.role,
        stats=stats,
        recent_sales=recent_sales,
    )
