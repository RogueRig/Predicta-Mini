"""Predicta Mini - Crypto Prediction Market Trading App.

Flask backend that integrates with Polymarket's CLOB API,
Polygon relayer for gasless transactions, and builder
order attribution.
"""

import os
import sys

from flask import Flask, send_from_directory
from flask_cors import CORS

# Add backend dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from routes.markets import markets_bp
from routes.trading import trading_bp
from routes.wallet import wallet_bp


def create_app():
    app = Flask(
        __name__,
        static_folder="../frontend/public",
        static_url_path="",
    )
    app.config.from_object(Config)

    # Enable CORS for frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register API blueprints
    app.register_blueprint(markets_bp)
    app.register_blueprint(trading_bp)
    app.register_blueprint(wallet_bp)

    # Health check
    @app.route("/api/health")
    def health():
        return {"status": "ok", "app": "predicta-mini"}

    # Serve frontend
    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/<path:path>")
    def static_files(path):
        return send_from_directory(app.static_folder, path)

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)
