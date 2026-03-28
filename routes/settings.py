from flask import Blueprint, render_template, request, redirect, flash, abort
from flask_login import login_required, current_user
from db import get_db

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if current_user.role not in ["owner", "admin"]:
        abort(403)

    db = get_db()
    cur = db.cursor(dictionary=True)

    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()
        if not company_name:
            flash("Company name is required.", "error")
            return redirect("/settings")

        try:
            cur.execute("""
                UPDATE company_settings
                SET company_name=%s, gstin=%s, address=%s, phone=%s, email=%s,
                    bank_name=%s, account_no=%s, ifsc=%s, branch=%s, pin_code=%s
                WHERE id=1
            """, (
                company_name,
                request.form.get("gstin",     "").strip(),
                request.form.get("address",   "").strip(),
                request.form.get("phone",     "").strip(),
                request.form.get("email",     "").strip(),
                request.form.get("bank_name", "").strip(),
                request.form.get("account_no","").strip(),
                request.form.get("ifsc",      "").strip(),
                request.form.get("branch",    "").strip(),
                request.form.get("pin_code",  "").strip(),
            ))
            db.commit()
            flash("Settings saved successfully.", "success")
        except Exception:
            db.rollback()
            flash("Failed to save settings. Please try again.", "error")

        return redirect("/settings")

    cur.execute("SELECT * FROM company_settings WHERE id=1")
    data = cur.fetchone()

    cur.execute("SELECT id, rate FROM gst_rates ORDER BY rate ASC")
    tax_rates = cur.fetchall()

    return render_template(
        "settings.html",
        data=data,
        tax_rates=tax_rates,
        role=current_user.role
    )


# ---------------------------------------------------------------------------
# Tax rate management
# ---------------------------------------------------------------------------

@settings_bp.route("/settings/tax-rates/add", methods=["POST"])
@login_required
def add_tax_rate():
    if current_user.role not in ["owner", "admin"]:
        abort(403)

    try:
        rate = float(request.form.get("rate", "").strip())
        if not (0 <= rate <= 100):
            raise ValueError
    except ValueError:
        flash("Enter a valid rate between 0 and 100.", "error")
        return redirect("/settings")

    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO gst_rates (rate) VALUES (%s)", (rate,))
        db.commit()
        flash(f"{rate}% tax rate added.", "success")
    except Exception as e:
        db.rollback()
        if hasattr(e, "errno") and e.errno == 1062:
            flash(f"{rate}% already exists.", "error")
        else:
            flash("Failed to add rate.", "error")

    return redirect("/settings")


@settings_bp.route("/settings/tax-rates/edit/<int:rate_id>", methods=["POST"])
@login_required
def edit_tax_rate(rate_id):
    if current_user.role not in ["owner", "admin"]:
        abort(403)

    try:
        new_rate = float(request.form.get("rate", "").strip())
        if not (0 <= new_rate <= 100):
            raise ValueError
    except ValueError:
        flash("Enter a valid rate between 0 and 100.", "error")
        return redirect("/settings")

    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("UPDATE gst_rates SET rate=%s WHERE id=%s", (new_rate, rate_id))
        db.commit()
        flash(f"Tax rate updated to {new_rate}%.", "success")
    except Exception as e:
        db.rollback()
        if hasattr(e, "errno") and e.errno == 1062:
            flash(f"{new_rate}% already exists.", "error")
        else:
            flash("Failed to update rate.", "error")

    return redirect("/settings")


@settings_bp.route("/settings/tax-rates/delete/<int:rate_id>", methods=["POST"])
@login_required
def delete_tax_rate(rate_id):
    if current_user.role not in ["owner", "admin"]:
        abort(403)

    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT rate FROM gst_rates WHERE id=%s", (rate_id,))
        row = cur.fetchone()
        if not row:
            flash("Rate not found.", "error")
            return redirect("/settings")

        cur.execute("DELETE FROM gst_rates WHERE id=%s", (rate_id,))
        db.commit()
        flash(f"{row['rate']}% removed.", "success")
    except Exception:
        db.rollback()
        flash("Failed to remove rate.", "error")

    return redirect("/settings")
