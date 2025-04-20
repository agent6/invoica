# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ───────────────────────────────────────────────────────────────
# User (authentication + dark‑mode preference)
# ───────────────────────────────────────────────────────────────
class User(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    email      = db.Column(db.String(150), unique=True, nullable=False)
    password   = db.Column(db.String(150), nullable=False)
    dark_mode  = db.Column(db.Boolean, default=False)

    # one‑to‑one relationship to Settings
    settings   = db.relationship(
        "Settings",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"

# ───────────────────────────────────────────────────────────────
# Client (CRM data + invoices)
# ───────────────────────────────────────────────────────────────
class Client(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(300), default="")   # new
    email   = db.Column(db.String(150), default="")   # new
    phone   = db.Column(db.String(50),  default="")   # new
    notes   = db.Column(db.Text,       default="")    # new

    invoices = db.relationship(
        "Invoice",
        backref="client",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Client {self.name}>"

# ───────────────────────────────────────────────────────────────
# Invoice (header + line items)
# ───────────────────────────────────────────────────────────────
class Invoice(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.Integer,
        db.ForeignKey("client.id", ondelete="CASCADE"),
        nullable=False
    )
    amount    = db.Column(db.Float,    nullable=False, default=0.0)
    status    = db.Column(db.String(50), nullable=False)
    due_date  = db.Column(db.String(50), nullable=False)

    # one‑to‑many relationship to LineItem
    items = db.relationship(
        "LineItem",
        backref="invoice",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (f"<Invoice #{self.id:03d} "
                f"client={self.client_id} "
                f"amount={self.amount:.2f} "
                f"status={self.status}>")

# ───────────────────────────────────────────────────────────────
# LineItem (individual service/fee lines)
# ───────────────────────────────────────────────────────────────
class LineItem(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    invoice_id  = db.Column(
        db.Integer,
        db.ForeignKey("invoice.id", ondelete="CASCADE"),
        nullable=False
    )
    description = db.Column(db.String(255), nullable=False)
    amount      = db.Column(db.Float,       nullable=False)

    def __repr__(self):
        return f"<LineItem {self.description!r} ${self.amount:.2f}>"

# ───────────────────────────────────────────────────────────────
# Settings (per‑user invoice defaults)
# ───────────────────────────────────────────────────────────────
class Settings(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )

    company_name    = db.Column(db.String(150), default="")
    company_address = db.Column(db.String(300), default="")
    company_logo    = db.Column(db.String(200), default="")

    invoice_prefix  = db.Column(db.String(20), default="INV-")
    next_number     = db.Column(db.Integer, default=1)

    default_notes   = db.Column(db.Text, default="")
    default_terms   = db.Column(db.Text, default="")

    def __repr__(self):
        return (f"<Settings user={self.user_id} "
                f"prefix={self.invoice_prefix} "
                f"next={self.next_number}>")
