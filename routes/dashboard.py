from flask import Blueprint, render_template
from flask_login import login_required, current_user

dash_bp = Blueprint("dash", __name__)


@dash_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        role=current_user.role
    )