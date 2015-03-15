from flask import session
from flask.ext.socketio import emit, join_room, leave_room
from flask.ext.login import current_user
from app import db
from .. import socketio
from ..models import Channel


@socketio.on('joined', namespace='/chat')
def joined(message):
    room = session.get('room')
    user = current_user
    chat_room = Channel.query.filter_by(name=room).first()
    user.join(chat_room)
    db.session.add(user)
    db.session.commit()
    join_room(room)
    emit('status', {'msg': user.username + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    user = current_user
    emit('message', {'msg': user.username + ' : ' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    user = current_user
    chat_room = Channel.query.filter_by(name=room).first()
    user.leave(chat_room)
    db.session.add(user)
    db.session.commit()
    leave_room(room)
    emit('status', {'msg': user.username + ' has left the room.'}, room=room)

