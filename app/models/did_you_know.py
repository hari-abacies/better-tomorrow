from .base import BaseModel
from app import db

class DidYouKnow(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    quotes = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Boolean, default=False)