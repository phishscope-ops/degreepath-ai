"""مسارك (DegreePath AI) - application factory."""
import os

from flask import Flask, send_from_directory


def create_app(test_config=None):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(__name__, static_folder=os.path.join(base, "static"), static_url_path="")
    app.config["DATABASE"] = os.environ.get("DATABASE_URL") or os.path.join(
        base, "degreepath.sqlite3"
    )
    app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD", "")
    app.config["JSON_AS_ASCII"] = False
    if test_config:
        app.config.update(test_config)

    app.json.ensure_ascii = False
    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

    # Render terminates TLS at a proxy: trust exactly one hop for the client IP.
    if os.environ.get("RENDER") or os.environ.get("TRUST_PROXY") == "1":
        from werkzeug.middleware.proxy_fix import ProxyFix

        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=0)

    from . import security

    app.after_request(security.add_headers)

    from . import db

    db.init_app(app)
    db.init_db(app)

    from . import feed

    with app.app_context():
        feed.maybe_refresh(app, db.get_db())

    from .admin import bp as admin_bp
    from .api import bp as api_bp

    with app.app_context():
        security.purge_old()

    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    from . import keepalive

    keepalive.maybe_start(app)

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.get("/admin")
    def admin_page():
        return send_from_directory(app.static_folder, "admin.html")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
