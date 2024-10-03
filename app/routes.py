import random
import string

import requests
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.forms import LoginForm, EventForm, RegisterForm, EventEditForm
from app.models import User, Event

routes = Blueprint('routes', __name__)


def generate_reservation_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


@routes.route('/')
def index():
    response = requests.get(url_for('api.get_events', _external=True))
    events = response.json()
    return render_template('index.html', events=events)


@routes.route('/register/<int:event_id>', methods=['POST'])
@login_required
def register(event_id):
    try:
        response = requests.post(
            url_for('api.api_register', _external=True),
            json={'event_id': event_id, 'email': current_user.email}
        )

        if response.status_code == 201:
            data = response.json()
            flash(data['message'])
        else:
            error_message = response.text
            flash(f'Registration error: {error_message}')
    except requests.RequestException:
        flash('Error during registration')

    return redirect(url_for('routes.index'))


@routes.route('/manage-events')
@login_required
def manage_events():
    try:
        response = requests.get(url_for('api.get_reservations', email=current_user.email, _external=True))
        response.raise_for_status()
        reservations = response.json()
    except requests.RequestException:
        return abort(500, description="Error getting reservations")

    return render_template('manage_events.html', reservations=reservations)


@routes.route('/cancel-reservation/<int:reservation_id>', methods=['POST'])
@login_required
def cancel_reservation(reservation_id):
    try:
        response = requests.post(
            url_for('api.api_cancel_reservation', _external=True),
            json={'reservation_id': reservation_id, 'email': current_user.email}
        )

        if response.status_code == 200:
            data = response.json()
            flash(data['message'])
        else:
            error_message = response.text
            flash(f'Error canceling reservation: {error_message}')
    except requests.RequestException:
        flash('Error while trying to cancel reservation. Please try again later.')

    return redirect(url_for('routes.manage_events'))


@routes.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('routes.index'))
        flash('Login failed. Check your email and password.')
    return render_template('login.html', form=form)


@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))


@routes.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(email=form.email.data, password=hashed_password, is_admin=False)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('routes.login'))
    return render_template('user_registration.html', form=form)


@routes.route('/edit-event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventEditForm(obj=event)

    if form.validate_on_submit():
        try:
            response = requests.put(
                url_for('api.api_edit_event', _external=True),
                json={
                    'event_id': event_id,
                    'title': form.title.data,
                    'start_date': form.start_date.data.isoformat(),
                    'end_date': form.end_date.data.isoformat(),
                    'thumbnail': form.thumbnail.data
                }
            )

            if response.status_code == 200:
                flash('Event updated successfully.')
                return redirect(url_for('routes.index'))
            else:
                error_message = response.text
                flash(f'Error updating event: {error_message}')
        except requests.RequestException:
            flash('Error while trying to edit the event. Please try again later.')

    return render_template('edit_event.html', form=form, event=event)


@routes.route('/delete-event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    try:
        response = requests.delete(
            url_for('api.api_delete_event', _external=True),
            json={'event_id': event_id}
        )

        if response.status_code == 200:
            flash('Event deleted successfully.')
        else:
            error_message = response.text
            flash(f'Error deleting event: {error_message}')
    except requests.RequestException:
        flash('Error while trying to delete the event. Please try again later.')

    return redirect(url_for('routes.index'))


@routes.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('routes.index'))

    form = EventForm()
    if form.validate_on_submit():
        try:
            response = requests.post(
                url_for('api.api_create_event', _external=True),
                json={
                    'title': form.title.data,
                    'start_date': form.start_date.data.isoformat(),
                    'end_date': form.end_date.data.isoformat(),
                    'thumbnail': form.thumbnail.data
                }
            )

            if response.status_code == 200:
                flash('Event created successfully.')
                return redirect(url_for('routes.index'))
            else:
                error_message = response.text
                flash(f'Error creating event: {error_message}')
        except requests.RequestException:
            flash('Error while trying to create the event. Please try again later.')

    return render_template('admin.html', form=form)
