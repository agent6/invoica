# routes/line_items.py

from flask import Blueprint, session, redirect, url_for, request
from models import db, Invoice, LineItem

items_bp = Blueprint('items', __name__, url_prefix='/invoices/<int:invoice_id>/items')

@items_bp.route('', methods=['POST'])
def add(invoice_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    invoice = Invoice.query.get_or_404(invoice_id)
    desc    = request.form['description'].strip()
    amt     = float(request.form['amount'])
    if desc and amt >= 0:
        item = LineItem(invoice_id=invoice.id, description=desc, amount=amt)
        db.session.add(item)
        invoice.amount = sum(i.amount for i in invoice.items)
        db.session.commit()
    return redirect(url_for('invoices.detail', invoice_id=invoice.id))

@items_bp.route('/<int:item_id>/delete', methods=['POST'])
def delete(invoice_id, item_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    item = LineItem.query.get_or_404(item_id)
    invoice = item.invoice
    db.session.delete(item)
    db.session.flush()
    invoice.amount = sum(i.amount for i in invoice.items)
    db.session.commit()
    return redirect(url_for('invoices.detail', invoice_id=invoice.id))
