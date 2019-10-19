from datetime import datetime
from flask_login import UserMixin
# from werkzeug.security import generate_password_hash, check_password_hash
import logging
from sqlalchemy import and_
from sqlalchemy.orm import load_only, backref
from . import db


class User(db.Model, UserMixin):

    __tablename__ = 'users'

    user_id = db.Column(db.String(50), index=True, primary_key=True)
    logs = db.relationship("Log", order_by="Log.created_at.desc()",
                            primaryjoin="User.user_id == Log.user_id", uselist=True, backref=backref("user", lazy="joined"), lazy="joined")
    # password_hash = db.Column(db.String(20), nullable=True)
    # description = db.Column(db.String(200), nullable=True)
    # profile_image_url = db.Column(db.String(200), nullable=True)
    # twitter_id = db.Column(db.String(15), index=True, unique=True)
    # twitter_access_token = db.Column(db.String(60), nullable=True)
    # twitter_access_token_secret = db.Column(db.String(60), nullable=True)
    # is_recieved_mail_notice = db.Column(db.Integer, nullable=False, default=0)
    # notification_message_stack = db.relationship(
    #     "Notification", primaryjoin="User.id == Notification.user_id", uselist=True)
    # matches = db.relationship(
    #     "Relation", primaryjoin="and_(User.id == Relation.user_id, Relation.is_matched == 1)", uselist=True, lazy="select")
    # my_messages = db.relationship("Message", order_by="Message.created_at.desc()",
    #                               primaryjoin="User.id == Message.user_id", uselist=True, backref=backref("user", lazy="select"), lazy="select")
    # messages = db.relationship("Message", order_by="Message.created_at.desc()",
    #                            primaryjoin="User.id == Message.destination_id", uselist=True, backref=backref("destination", lazy="select"), lazy="select")
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return 'User(id={0}, user_id={1})'.format(
            self.id, self.user_id
        )


class Log(db.Model, UserMixin):

    __tablename__ = 'logs'

    id = db.Column(
        db.Integer,
        primary_key=True)
    user_id = db.Column(db.String(50))
    tag = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return 'User(id={0}, user_id={1}, tag={2}, created_at={3})'.format(
            self.id, self.user_id, self.tag, self.created_at
        )
