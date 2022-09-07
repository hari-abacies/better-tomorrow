from app import db
from app.models import BaseModel
import json

class Referrals(BaseModel):
    __tablename__ = "referrals"
    id = db.Column(db.Integer, primary_key=True)
    ref_status = db.Column(db.Boolean, default=False)
    ref_user_id = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)