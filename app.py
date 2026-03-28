import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import SECRET_KEY
from db import get_db, close_db
from models import User

app = Flask(__name__)
app.secret_key = SECRET_KEY

# CSRF protection — covers every POST form globally
CSRFProtect(app)

# Return DB connection to pool after every request, even on error
app.teardown_appcontext(close_db)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(
        "SELECT id, role FROM users WHERE id=%s AND active=1",
        (user_id,)
    )
    user = cur.fetchone()
    if user:
        return User(user["id"], user["role"])
    return None


# --- Blueprints ---
from routes.auth import auth_bp
from routes.dashboard import dash_bp
from routes.inventory import inventory_bp
from routes.invoices import invoices_bp
from routes.sales import sales_bp
from routes.settings import settings_bp
from routes.users import users_bp
from routes.audit_log import audit_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dash_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(invoices_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(users_bp)
app.register_blueprint(audit_bp)


# --- Health check ---
@app.route("/health")
def health():
    try:
        db = get_db()
        db.cursor().execute("SELECT 1")
        return {"status": "ok"}, 200
    except Exception:
        return {"status": "error", "detail": "db unreachable"}, 503


# --- Error handlers ---
@app.errorhandler(403)
def forbidden(e):
    return render_template("errors/403.html"), 403

@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("errors/500.html"), 500


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug)
