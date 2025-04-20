# routes/auth.py
from flask import Blueprint, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from .helpers import get_or_create_settings

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET"])
def home():
    # If no users exist yet, send to setup screen
    if User.query.count() == 0:
        return redirect(url_for("auth.setup"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/setup", methods=["GET", "POST"])
def setup():
    # Prevent access if setup already completed
    if User.query.count() > 0:
        return redirect(url_for("auth.login"))

    error = None
    if request.method == "POST":
        email   = request.form.get("email", "").strip()
        pw      = request.form.get("password", "")
        pw_conf = request.form.get("confirm_password", "")

        if not email:
            error = "Email is required."
        elif not pw or pw != pw_conf:
            error = "Passwords must match and not be empty."
        else:
            # create first user
            user = User(
                email=email,
                password=generate_password_hash(pw),
                dark_mode=False
            )
            db.session.add(user)
            db.session.commit()

            # create default settings
            get_or_create_settings(user.id)

            return redirect(url_for("auth.login"))

    return render_template("setup.html", error=error)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # if no users exist, force setup
    if User.query.count() == 0:
        return redirect(url_for("auth.setup"))

    if "user_id" in session:
        return redirect(url_for("dashboard.view"))

    error = None
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            session["user_id"] = user.id
            return redirect(url_for("dashboard.view"))
        error = "Invalid credentials"

    return render_template("login.html", error=error)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    # signup only after initial setup
    if User.query.count() == 0:
        return redirect(url_for("auth.setup"))

    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        pw    = request.form.get("password", "")
        if not email or not pw:
            error = "Email and password are required."
        elif User.query.filter_by(email=email).first():
            error = "That email is already registered."
        else:
            user = User(
                email=email,
                password=generate_password_hash(pw),
                dark_mode=False
            )
            db.session.add(user)
            db.session.commit()
            get_or_create_settings(user.id)
            return redirect(url_for("auth.login"))

    return render_template("signup.html", error=error)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
