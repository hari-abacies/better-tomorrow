from random import choices
from app import db
from app.models import BaseModel
import json

class Answer(BaseModel):
    __tablename__ = "answer"
    id = db.Column(db.Integer, primary_key=True)
    choices = db.Column(db.Text, default=json.dumps([]))
    qus_id = db.Column(db.Integer, db.ForeignKey("question.id", ondelete="CASCADE"), nullable=False)
