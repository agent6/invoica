# routes/invoices.py

from flask import Blueprint, render_template, session, redirect, url_for, request
from models import db, Invoice, Client

invoices_bp = Blueprint('invoices', __name__, url_prefix='/invoices')


@invoices_bp.route('/', methods=['GET'])
def list():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # grab filter & pagination params
    page        = request.args.get('page', 1, type=int)
    client_id   = request.args.get('client_id', type=int)
    status      = request.args.get('status', '').strip()

    # base query
    q = Invoice.query.join(Client)

    # apply filters
    if client_id:
        q = q.filter(Invoice.client_id == client_id)
    if status:
        q = q.filter(Invoice.status == status)

    # order & paginate
    pagination = q.order_by(Invoice.id.desc()) \
                  .paginate(page=page, per_page=10, error_out=False)

    # for the filter dropdowns
    all_clients = Client.query.order_by(Client.name).all()
    statuses    = ['Pending', 'Paid', 'Overdue']

    return render_template(
        'invoices.html',
        invoices        = pagination.items,
        all_clients     = all_clients,
        statuses        = statuses,
        selected_client = client_id,
        selected_status = status,
        pagination      = pagination,
    )


@invoices_bp.route('/new', methods=['GET','POST'])
def create():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    clients = Client.query.all()
    if request.method == 'POST':
        inv = Invoice(
            client_id=int(request.form['client_id']),
            amount=0.0,
            due_date=request.form['due_date'],
            status='Pending'
        )
        db.session.add(inv)
        db.session.commit()
        return redirect(url_for('invoices.detail', invoice_id=inv.id))
    return render_template('new_invoice.html', clients=clients)


@invoices_bp.route('/<int:invoice_id>', methods=['GET','POST'])
def detail(invoice_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    invoice = Invoice.query.get_or_404(invoice_id)
    clients = Client.query.all()
    if request.method == 'POST':
        invoice.client_id = int(request.form['client_id'])
        invoice.due_date   = request.form['due_date']
        invoice.status     = request.form['status']
        db.session.commit()
        return redirect(url_for('invoices.detail', invoice_id=invoice.id))
    return render_template('invoice_detail.html',
                           invoice=invoice,
                           clients=clients)


@invoices_bp.route('/<int:invoice_id>/delete', methods=['POST'])
def delete(invoice_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    inv = Invoice.query.get_or_404(invoice_id)
    db.session.delete(inv)
    db.session.commit()
    return redirect(url_for('invoices.list'))
