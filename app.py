# app.py
import os
from flask import Flask
from models import db
from routes.auth       import auth_bp
from routes.dashboard  import dashboard_bp
from routes.clients    import clients_bp
from routes.invoices   import invoices_bp
from routes.line_items import items_bp
from routes.pdf        import pdf_bp
from routes.profile    import profile_bp
from routes.settings   import settings_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET", "secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///invoica.db"

    # optional cookie‐domain for your tunnel
    cd = os.getenv("SESSION_COOKIE_DOMAIN")
    if cd:
        app.config["SESSION_COOKIE_DOMAIN"]  = cd
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        app.config["SESSION_COOKIE_SECURE"]   = True

    db.init_app(app)

    # register all blueprints
    app.register_blueprint(auth_bp)        # handles /, /setup, /login, /logout, etc.
    app.register_blueprint(dashboard_bp)   # handles /dashboard
    app.register_blueprint(clients_bp)     # prefix '/clients'
    app.register_blueprint(invoices_bp)    # prefix '/invoices'
    app.register_blueprint(items_bp)       # prefix '/invoices/<invoice_id>/items'
    app.register_blueprint(pdf_bp)         # prefix '/invoices'
    app.register_blueprint(profile_bp)     # prefix '/profile'
    app.register_blueprint(settings_bp)    # prefix '/settings'

    # ensure tables exist on startup
    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    # listen on 0.0.0.0 for LAN/tunnel access
    app.run(host="0.0.0.0", port=5001, debug=True)
