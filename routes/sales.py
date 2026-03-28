import uuid
from flask import Blueprint, render_template, request, redirect, flash, abort
from flask_login import login_required, current_user
from db import get_db
from utils.invoice_generator import generate_invoice
from utils.audit import log_action

sales_bp = Blueprint("sales", __name__, url_prefix="/sales")


def generate_invoice_no():
    return f"SOL-{uuid.uuid4().hex[:12].upper()}"


@sales_bp.route("/", methods=["GET", "POST"])
@login_required
def create_sale():
    if current_user.role not in ["owner", "admin", "sales"]:
        abort(403)

    db  = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT * FROM inventory_items WHERE quantity > 0")
    items = cur.fetchall()
    cur.execute("SELECT rate FROM gst_rates ORDER BY rate ASC")
    tax_rates = [float(r["rate"]) for r in cur.fetchall()] or [0,2.5,6,9,14,18,28]

    if request.method == "POST":
        item_ids   = request.form.getlist("item_id[]")
        quantities = request.form.getlist("quantity[]")

        gst_applied  = request.form.get("gst") == "yes"
        buyer_name   = request.form.get("buyer_name",   "").strip()
        buyer_addr   = request.form.get("buyer_address","").strip()
        payment_mode = request.form.get("payment_mode", "").strip()
        destination  = request.form.get("destination",  "").strip()
        vehicle_no   = request.form.get("vehicle_no",   "").strip()
        driver_name  = request.form.get("driver_name",  "").strip()

        try:
            discount = round(float(request.form.get("discount", 0) or 0), 2)
            if discount < 0:
                raise ValueError
        except (ValueError, TypeError):
            flash("Discount must be a positive number.", "error")
            return redirect("/sales")

        if not item_ids:
            flash("Please add at least one item.", "error")
            return redirect("/sales")

        line_inputs = []
        for item_id, qty_str in zip(item_ids, quantities):
            try:
                item_id = int(item_id)
                qty     = int(qty_str)
                if qty < 1:
                    raise ValueError
            except (ValueError, TypeError):
                flash("All quantities must be whole numbers greater than 0.", "error")
                return redirect("/sales")
            line_inputs.append((item_id, qty))

        if len(set(i for i, _ in line_inputs)) != len(line_inputs):
            flash("The same item appears more than once. Combine them into a single row.", "error")
            return redirect("/sales")

        try:
            resolved = []
            for item_id, qty in line_inputs:
                cur.execute(
                    "SELECT * FROM inventory_items WHERE id=%s FOR UPDATE",
                    (item_id,)
                )
                item = cur.fetchone()

                if not item:
                    flash(f"Item ID {item_id} not found.", "error")
                    db.rollback()
                    return redirect("/sales")

                if item["quantity"] < qty:
                    flash(
                        f"Insufficient stock for '{item['name']}'. "
                        f"Requested {qty}, only {item['quantity']} available.",
                        "error"
                    )
                    db.rollback()
                    return redirect("/sales")

                line_base  = float(item["price"]) * qty
                line_gst   = round(line_base * float(item["gst_rate"]) / 100, 2) if gst_applied else 0
                line_total = round(line_base + line_gst, 2)

                resolved.append({
                    "item":       item,
                    "qty":        qty,
                    "unit_price": float(item["price"]),
                    "gst_rate":   float(item["gst_rate"]),
                    "line_base":  line_base,
                    "line_gst":   line_gst,
                    "line_total": line_total,
                })

            subtotal    = round(sum(r["line_base"] for r in resolved), 2)
            gst_amount  = round(sum(r["line_gst"]  for r in resolved), 2)
            total       = round(subtotal + gst_amount, 2)
            final_total = round(total - discount, 2)
            invoice_no  = generate_invoice_no()

            cur.execute("SELECT * FROM company_settings WHERE id=1")
            company = cur.fetchone()

            sale_data = {
                "subtotal":      subtotal,
                "gst_amount":    gst_amount,
                "total_amount":  total,
                "discount":      discount,
                "buyer_name":    buyer_name,
                "buyer_address": buyer_addr,
                "payment_mode":  payment_mode,
                "destination":   destination,
                "vehicle_no":    vehicle_no,
                "driver_name":   driver_name,
            }

            invoice_path = None
            try:
                invoice_path = generate_invoice(
                    invoice_no, company, sale_data, resolved, gst_applied,
                    gst_rate_list=tax_rates
                )
            except Exception:
                pass

            cur.execute("""
                INSERT INTO sales
                (invoice_no, sold_by, gst_applied, subtotal, gst_amount,
                 total_amount, invoice_file, buyer_name, buyer_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                invoice_no, current_user.id, gst_applied,
                subtotal, gst_amount, final_total,
                invoice_path, buyer_name, buyer_addr
            ))

            sale_id = cur.lastrowid

            for r in resolved:
                cur.execute("""
                    INSERT INTO sale_items
                    (sale_id, item_id, quantity, unit_price, gst_rate,
                     gst_amount, line_total)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    sale_id, r["item"]["id"], r["qty"],
                    r["unit_price"], r["gst_rate"],
                    r["line_gst"], r["line_total"]
                ))

                cur.execute("""
                    UPDATE inventory_items
                    SET quantity = quantity - %s WHERE id = %s
                """, (r["qty"], r["item"]["id"]))

            db.commit()

        except Exception:
            db.rollback()
            flash("Sale could not be completed. Please try again.", "error")
            return redirect("/sales")

        log_action(current_user, "Sale created", invoice_no)

        if invoice_path is None:
            flash(f"Sale {invoice_no} recorded, but PDF generation failed.", "warning")
        else:
            flash(f"Sale {invoice_no} completed successfully.", "success")

        return redirect("/sales")

    return render_template("sales.html", items=items, tax_rates=tax_rates, role=current_user.role)
