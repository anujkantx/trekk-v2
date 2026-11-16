import os
from flask import Flask, jsonify
from backend.config import Config
from backend.extensions import db, jwt, cors, cache
import backend.models # execute init.py to register models
from backend.routes.auth import auth_bp

def create_app(config_class=Config):
    app = Flask(__name__) # flask app instance 
    app.config.from_object(config_class)

    # Ensure instance, exports, and reports directories exist
    os.makedirs(app.config.get("INSTANCE_DIR"), exist_ok=True)
    os.makedirs(app.config.get("EXPORTS_DIR"), exist_ok=True)
    os.makedirs(app.config.get("REPORTS_DIR"), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    cache.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)

    # Health check route
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "healthy", "service": "Trekking Management API"}), 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="localhost", port=5001, debug=True)
