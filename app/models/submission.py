from app import db
from app.models import BaseModel
import json

class Submission(BaseModel):
    __tablename__ = "submission"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean, default=False)
    q_and_a = db.Column(db.Text, default=json.dumps([]))
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)