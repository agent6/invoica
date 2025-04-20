# routes/clients.py

from flask import Blueprint, render_template, session, redirect, url_for, request
from models import db, Client

clients_bp = Blueprint('clients', __name__, url_prefix='/clients')


@clients_bp.route('/', methods=['GET'])
def list():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    clients = Client.query.all()
    return render_template('clients.html', clients=clients)


@clients_bp.route('/new', methods=['GET', 'POST'])
def create():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        client = Client(name=request.form['name'])
        db.session.add(client)
        db.session.commit()
        return redirect(url_for('clients.list'))
    return render_template('new_client.html')


@clients_bp.route('/<int:client_id>', methods=['GET', 'POST'])
def detail(client_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    client = Client.query.get_or_404(client_id)

    if request.method == 'POST':
        # update client CRM fields
        client.name    = request.form.get('name', client.name)
        client.address = request.form.get('address', client.address)
        client.email   = request.form.get('email', client.email)
        client.phone   = request.form.get('phone', client.phone)
        client.notes   = request.form.get('notes', client.notes)
        db.session.commit()
        return redirect(url_for('clients.detail', client_id=client.id))

    return render_template('client_detail.html', client=client)


@clients_bp.route('/<int:client_id>/delete', methods=['POST'])
def delete(client_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('clients.list'))
