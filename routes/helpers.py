# routes/helpers.py

from models import db, Settings

def get_or_create_settings(user_id: int) -> Settings:
    settings = Settings.query.filter_by(user_id=user_id).first()
    if not settings:
        settings = Settings(user_id=user_id)
        db.session.add(settings)
        db.session.commit()
    return settings
