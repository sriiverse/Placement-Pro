"""
extensions.py — Flask extension instances.

Instantiated here (outside the app factory) so any module can import them
without triggering circular imports. They are bound to the app via
`init_app(app)` inside create_app().
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "60 per hour"],
    storage_uri="memory://",
    strategy="fixed-window",
)
