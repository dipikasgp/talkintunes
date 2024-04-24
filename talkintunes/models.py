from talkintunes import db, login_manager
from flask import current_app
import datetime
from flask_login import UserMixin
from itsdangerous import TimedSerializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    private_key = db.Column(db.Text, nullable=False)
    public_key = db.Column(db.Text, nullable=False)
    sent_messages = db.relationship('Messages', backref='sender', foreign_keys='Messages.sender_id', lazy=True)
    received_messages = db.relationship('Messages', backref='receiver', foreign_keys='Messages.receiver_id', lazy=True)

    def get_reset_tokens(self, expires_sec=1800):
        s = TimedSerializer(current_app.config['SECRET_KEY'], str(expires_sec))
        encoded_data = s.dumps({'user_id': self.id}).decode('utf-8')
        return encoded_data

    @staticmethod
    def verify_reset_token(token):
        s = TimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    content = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    mp3_file_path = db.Column(db.Text, nullable=False,default='melody.mp3')
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)


class UserNoteMapping(db.Model):
    __tablename__ = 'user_note_mapping'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    note = db.Column(db.Text)
