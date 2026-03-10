from flask import Flask
from flask_login import LoginManager
from db import get_db
from models import User
from routes.inventory import inventory_bp
from routes.sales import sales_bp



app = Flask(__name__)
app.secret_key = "change-this-key"

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


# 🔴 IMPORTANT: imports go AFTER everything above
from routes.auth import auth_bp
from routes.dashboard import dash_bp
from routes.settings import settings_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dash_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(sales_bp)
from routes.users import users_bp
app.register_blueprint(users_bp)
from routes.invoices import invoices_bp
app.register_blueprint(invoices_bp)




if __name__ == "__main__":
    app.run(debug=True)
