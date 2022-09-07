from app import db
from app.models import BaseModel

class Quizzes(BaseModel):
    __tablename__ = "quizzes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    disabled = db.Column(db.Boolean, default=False)
    questions = db.relationship("Question", viewonly=True, backref="answer_in_qus", uselist=True)