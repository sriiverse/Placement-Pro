import os
import time
import uuid
import logging
from datetime import timedelta

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import Flask, g, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .models import db
from .auth import bcrypt
from .extensions import limiter
from .logger import get_logger, apply_correlation_filter
from .openapi import OPENAPI_SPEC
from .cache import all_cache_stats

# Module-level app logger
logger = get_logger("placementpro.app")
apply_correlation_filter(logger)


def create_app():
    app = Flask(__name__)

    # ─── Sentry Error Tracking ────────────────────────────────────────────────
    # SENTRY_DSN is read from environment. If not set, Sentry is disabled
    # gracefully — no crashes, no noise.
    sentry_dsn = os.environ.get("SENTRY_DSN", "")
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FlaskIntegration()],
            # Capture 10% of transactions for performance monitoring
            traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            # Don't send PII (emails, IPs) to Sentry
            send_default_pii=False,
            # Tag every event with environment and release
            environment=os.environ.get("FLASK_ENV", "development"),
            release=os.environ.get("APP_VERSION", "2.0.0"),
        )
        logger.info("Sentry error tracking enabled", extra={"dsn_prefix": sentry_dsn[:20] + "..."})
    else:
        logger.info("Sentry DSN not set — error tracking disabled (dev mode)")

    # ─── CORS ─────────────────────────────────────────────────────────────────
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ─── Core Config ──────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # ─── Database ─────────────────────────────────────────────────────────────
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ─── JWT Configuration ────────────────────────────────────────────────────
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
        minutes=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', 60))
    )
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(
        days=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES_DAYS', 30))
    )

    # ─── Rate Limiter Config ───────────────────────────────────────────────────
    app.config['RATELIMIT_HEADERS_ENABLED'] = True
    app.config['RATELIMIT_SWALLOW_ERRORS'] = False

    # ─── Initialize Extensions ────────────────────────────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    JWTManager(app)
    limiter.init_app(app)

    # ─── Create Tables ────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    # ─── Register Blueprints ──────────────────────────────────────────────────
    from .routes import api_bp
    from .auth import auth_bp

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # ─── Request Lifecycle Hooks ──────────────────────────────────────────────

    @app.before_request
    def _before_request():
        g.correlation_id = str(uuid.uuid4())
        g.request_start_time = time.perf_counter()

        if request.path not in ("/health", "/ready"):
            logger.debug(
                "Incoming request",
                extra={
                    "http_method": request.method,
                    "path": request.path,
                    "remote_addr": request.remote_addr,
                    "content_type": request.content_type,
                },
            )

    @app.after_request
    def _after_request(response):
        if request.path in ("/health", "/ready"):
            return response

        duration_ms = round(
            (time.perf_counter() - getattr(g, "request_start_time", 0)) * 1000, 2
        )
        status_code = response.status_code
        level = logging.WARNING if status_code >= 400 else logging.INFO

        logger.log(
            level,
            "Request completed",
            extra={
                "http_method": request.method,
                "path": request.path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "remote_addr": request.remote_addr,
            },
        )
        return response

    @app.teardown_request
    def _teardown_request(exc):
        if exc is not None:
            logger.error(
                "Unhandled exception during request",
                exc_info=exc,
                extra={"path": request.path},
            )

    # ─── Rate Limit Exceeded Handler ──────────────────────────────────────────
    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        logger.warning(
            "Rate limit exceeded",
            extra={"path": request.path, "remote_addr": request.remote_addr}
        )
        return jsonify({
            "status": "error",
            "message": "Too many requests. Please slow down and try again later.",
            "retry_after": str(e.description),
        }), 429

    # ─── Health Check (Liveness) ──────────────────────────────────────────────
    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy", "service": "placement-pro-core"}), 200

    # ─── Readiness Check (Deep Health) ────────────────────────────────────────
    @app.route('/ready')
    def readiness_check():
        checks = {}
        overall_ok = True

        # Database ping
        try:
            db.session.execute(db.text("SELECT 1"))
            checks["database"] = {"status": "ok", "backend": "sqlite"}
        except Exception as exc:
            checks["database"] = {"status": "error", "detail": str(exc)}
            overall_ok = False
            logger.error("Readiness check: database unreachable", exc_info=exc)

        # Disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_gb = round(free / (1024 ** 3), 2)
            disk_ok = free_gb > 0.5
            checks["disk"] = {"status": "ok" if disk_ok else "warning", "free_gb": free_gb}
            if not disk_ok:
                overall_ok = False
        except Exception as exc:
            checks["disk"] = {"status": "error", "detail": str(exc)}

        # Optional memory check
        try:
            import psutil
            mem = psutil.virtual_memory()
            checks["memory"] = {
                "status": "ok",
                "used_percent": mem.percent,
                "available_mb": round(mem.available / (1024 ** 2), 1),
            }
        except ImportError:
            checks["memory"] = {"status": "skipped", "reason": "psutil not installed"}

        # Cache status
        checks["cache"] = all_cache_stats()

        status_code = 200 if overall_ok else 503
        return jsonify({
            "status": "ready" if overall_ok else "degraded",
            "service": "placement-pro-core",
            "checks": checks,
        }), status_code

    # ─── OpenAPI / Swagger Docs ───────────────────────────────────────────────
    @app.route('/api/docs/openapi.json')
    def openapi_spec():
        """Serve the raw OpenAPI 3.0 JSON spec."""
        return jsonify(OPENAPI_SPEC)

    @app.route('/api/docs/')
    @app.route('/api/docs')
    def swagger_ui():
        """
        Serve the Swagger UI HTML page.
        Loads the official Swagger UI from CDN — no extra package needed.
        """
        spec_url = "/api/docs/openapi.json"
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>PlacementPro+ API Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
  <style>
    body {{ margin: 0; background: #0a0a0f; }}
    .topbar {{ background: #0a0a0f !important; border-bottom: 1px solid #00f3ff33; }}
    .topbar-wrapper img {{ display: none; }}
    .topbar-wrapper::before {{
      content: "PLACEMENT.OS // API v2.0";
      font-family: monospace;
      color: #00f3ff;
      font-size: 1.1rem;
      letter-spacing: 0.15em;
    }}
    .swagger-ui .info h2 {{ color: #00f3ff; }}
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({{
      url: "{spec_url}",
      dom_id: "#swagger-ui",
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
      layout: "BaseLayout",
      deepLinking: true,
      persistAuthorization: true,
      tryItOutEnabled: true,
    }});
  </script>
</body>
</html>"""
        from flask import Response
        return Response(html, mimetype="text/html")

    logger.info(
        "PlacementPro+ app factory initialized",
        extra={"env": os.environ.get("FLASK_ENV", "development")}
    )
    return app
