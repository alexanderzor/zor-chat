from flask import session, redirect, url_for, render_template, flash, request, jsonify
from flask.ext.login import login_user, logout_user, login_required, current_user
from . import main
from .forms import SearchForm, JoinForm, EditProfileForm
from app import db
from ..models import Channel, User, Registrations


@main.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    channel = None
    channels = []
    if current_user.is_authenticated():
        channels = current_user.rooms()
    if form.validate_on_submit():
        search_room = form.room.data
        channel = Channel.query.filter_by(name=search_room).first()
        if channel is None:
            flash('This room does not exist')
        return render_template('index.html', form=form, channel=channel, channels=channels)
    return render_template('index.html', form=form, channel=channel, channels=channels)


@main.route('/create', methods=['GET', 'POST'])
def create():
    form = JoinForm()
    channels = current_user.rooms()
    if form.validate_on_submit():
        session['room'] = form.room.data
        session['password'] = form.password.data
        chat_room = Channel.query.filter_by(name=session.get('room')).first()
        if chat_room is not None:
            flash('This room has been already created')
        else:
            chat_room = Channel(name=session.get('room'), password=form.password.data)
            db.session.add(chat_room)
            db.session.commit()
            return redirect(url_for('.chat', channel=session.get('room')))
    return render_template('create.html', form=form, channels=channels)


@main.route('/join', methods=['GET', 'POST'])
def join():
    form = JoinForm()
    channels = current_user.rooms()
    if form.validate_on_submit():
        session['room'] = form.room.data
        session['password'] = form.password.data
        chat_room = Channel.query.filter_by(name=session.get('room')).first()
        if chat_room is None:
            flash('This room does not exist')
            return redirect(url_for('.join'))
        if chat_room is not None and chat_room.verify_password(form.password.data):
            return redirect(url_for('.chat', channel=session.get('room')))
        else:
            flash('Invalid password')
            return redirect(url_for('.join', channels=channels))
    return render_template('join.html', form=form, channels=channels)


@main.route('/chat/<channel>', methods=['GET', 'POST'])
def chat(channel):
    session['room'] = channel
    chat_room = Channel.query.filter_by(name=channel).first()
    users = db.session.query(User).select_from(Registrations).filter_by(
        channel_id=chat_room.id).join(User, Registrations.user_id == User.id)
    channels = current_user.rooms()
    if channel == '':
        return redirect(url_for('.index'))
    return render_template('chat.html', chat_room=chat_room,
                           users=users, channels=channels)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    channels = current_user.rooms()
    if form.validate_on_submit():
        current_user.username = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('main.user', username=current_user.username))
    form.name.data = current_user.username
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form, channels=channels)


@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('500.html'), 500