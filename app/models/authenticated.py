from app import db
from app.models import BaseModel

class Authenticated(BaseModel):
    __tablename__ = "authenticated"
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.Text)
