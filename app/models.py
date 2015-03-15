from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from app import db, login_manager
from datetime import datetime


class Registrations(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), primary_key=True)


class Channel(db.Model):
    __tablename__ = 'channels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128))
    users = db.relationship('Registrations', foreign_keys=[Registrations.channel_id],
                            backref=db.backref('channel', lazy='joined'), lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    channels = db.relationship('Registrations', foreign_keys=[Registrations.user_id],
                               backref=db.backref('user', lazy='joined'), lazy='dynamic')
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    def join(self, channel):
        if not self.channels.filter_by(channel_id=channel.id).first():
            f = Registrations(user_id=self.id, channel_id=channel.id)
            db.session.add(f)

    def leave(self, channel):
        f = self.channels.filter_by(channel_id=channel.id).first()
        if f:
            db.session.delete(f)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def rooms(self):
        rooms = db.session.query(Channel).select_from(Registrations).filter_by(
            user_id=self.id).join(Channel, Registrations.channel_id == Channel.id).all()
        return rooms


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


