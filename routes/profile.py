# routes/profile.py

from flask import Blueprint, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash
from models import db, User

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/', methods=['GET','POST'])
def view():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        user.email     = request.form.get('email', user.email)
        user.dark_mode = 'dark_mode' in request.form

        new_pw  = request.form.get('new_password')
        confirm = request.form.get('confirm_password')
        if new_pw and new_pw == confirm:
            user.password = generate_password_hash(new_pw)

        db.session.commit()
        return redirect(url_for('profile.view'))

    return render_template('profile.html', user=user)
