# routes/dashboard.py

from flask import Blueprint, render_template, session, redirect, url_for
from models import Invoice, Client
from routes.helpers import get_or_create_settings

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def view():
    # require login
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # fetch data
    invoices = Invoice.query.all()
    clients  = Client.query.all()
    settings = get_or_create_settings(session['user_id'])

    # render the updated dashboard.html (which now uses the “New Invoice” CTA etc.)
    return render_template(
        'dashboard.html',
        invoices=invoices,
        clients=clients,
        settings=settings
    )
