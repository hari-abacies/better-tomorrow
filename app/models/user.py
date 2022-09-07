import json
from datetime import timedelta
import pytz
import redis
from flask_httpauth import HTTPBasicAuth
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models import authenticated
from .base import BaseModel
from config import Config_is

auth = HTTPBasicAuth()
redis_obj = redis.StrictRedis.from_url(Config_is.REDIS_URL, decode_responses=True)


class User(BaseModel):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)

    # Credential
    email = db.Column(db.String(50), index=True, unique=True)
    name = db.Column(db.String(100))
    point_count = db.Column(db.Integer, default=0)
    badge = db.Column(db.Integer, default=0)
    monday_user_id = db.Column(db.String(100))
    submission = db.relationship("Submission", viewonly=True, backref="user_in_submission", uselist=True)


