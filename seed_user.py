"""
seed_user.py
------------
Interactive helper to add a user to the database.

• Prompts for e‑mail, password (with confirmation), and dark‑mode preference
• Hashes the password
• Creates a blank Settings row for the new user

Run inside your virtual‑env *after* the app’s tables exist:

    $ python seed_user.py
"""

from getpass import getpass
from werkzeug.security import generate_password_hash

from models import db, User, Settings
from app import create_app


def ask_credentials() -> tuple[str, str]:
    """Prompt for email + password (with confirmation)."""
    email = input("📨  Email address: ").strip()
    while True:
        pw1 = getpass("🔑  Password: ")
        pw2 = getpass("🔑  Confirm  : ")
        if pw1 and pw1 == pw2:
            break
        print("❌  Passwords don’t match or are empty — try again.\n")
    return email, pw1


def ask_dark_mode() -> bool:
    """Prompt whether to enable dark mode by default."""
    resp = input("🌙  Enable dark mode by default? (y/N): ").strip().lower()
    return resp in ("y", "yes")


def create_user(email: str, raw_password: str, dark_mode: bool = False):
    """Insert user + default settings if email not taken."""
    if User.query.filter_by(email=email).first():
        print(f"⚠️  {email} already exists. Aborting.")
        return

    user = User(
        email=email,
        password=generate_password_hash(raw_password),
        dark_mode=dark_mode
    )
    db.session.add(user)
    db.session.commit()  # need user.id for FK

    settings = Settings(user_id=user.id)
    db.session.add(settings)
    db.session.commit()

    dm_status = "with dark mode ON" if dark_mode else "with dark mode OFF"
    print(f"✅  Created user {email!r} {dm_status}")


def main():
    # Create app and tables if needed
    app = create_app()
    with app.app_context():
        # Ensure tables exist
        db.create_all()

        # Prompt for credentials and dark mode
        email, pw = ask_credentials()
        dark = ask_dark_mode()

        # Create the user
        create_user(email, pw, dark)


if __name__ == "__main__":
    main()
