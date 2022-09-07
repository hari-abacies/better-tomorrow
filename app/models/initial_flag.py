from .base import BaseModel
from app import db

class InitialFlag(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Boolean, default=False)