from app import db
from app.models import BaseModel, answer
import json


class Question(BaseModel):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    question = db.Column(db.Text)
    details = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.Text)
    description = db.Column(db.Text)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    answer = db.relationship("Answer", viewonly=True, backref="answer_in_qus", uselist=False)
    interactive_console = db.Column(db.Text)

    