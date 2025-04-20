# routes/settings.py

from flask import Blueprint, render_template, request, session, redirect, url_for
from models import db, Settings
from routes.helpers import get_or_create_settings

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET','POST'])
def view():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    settings = get_or_create_settings(session['user_id'])

    if request.method == 'POST':
        section = request.form.get('section')
        if section == 'business':
            settings.company_name    = request.form.get('company_name', settings.company_name)
            settings.company_address = request.form.get('company_address', settings.company_address)
        elif section == 'invoice':
            settings.invoice_prefix  = request.form.get('invoice_prefix', settings.invoice_prefix)
            settings.next_number     = int(request.form.get('next_number', settings.next_number))
            settings.default_notes   = request.form.get('default_notes', settings.default_notes)
            settings.default_terms   = request.form.get('default_terms', settings.default_terms)

        db.session.commit()
        return redirect(url_for('settings.view'))

    return render_template('settings.html', settings=settings)
