from .base import BaseModel
from app import db

class BoardInfo(BaseModel):
    __tablename__ = "boardinfo"
    id = db.Column(db.Integer, primary_key=True)
    board_info = db.Column(db.String(200), unique=True, nullable=False)
    board_type = db.Column(db.Integer, default=0)
    source_id =  db.Column(db.String(200)) #question id