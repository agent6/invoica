# routes/__init__.py

"""
The `routes` package contains all Flask Blueprints for Invoica.
Each module under `routes/` registers a Blueprint that’s wired up
in the main `app.py`.
"""

# You can optionally expose helper functions here for convenience:
from .helpers import get_or_create_settings

__all__ = [
    "auth_bp",
    "dashboard_bp",
    "clients_bp",
    "invoices_bp",
    "items_bp",
    "pdf_bp",
    "profile_bp",
    "settings_bp",
    "get_or_create_settings",
]
