import random
import string

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.forms import LoginForm, EventForm, RegisterForm
from app.models import User, Event, Reservation

routes = Blueprint('routes', __name__)


def generate_reservation_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


@routes.route('/')
def index():
    events = Event.query.all()
    return render_template('index.html', events=events)


@routes.route('/register/<int:event_id>', methods=['GET', 'POST'])
def register(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        email = request.form['email']
        reservation_code = generate_reservation_code()
        reservation = Reservation(event_id=event.id, email=email, reservation_code=reservation_code)
        db.session.add(reservation)
        db.session.commit()
        flash(f'Registration successful! Your reservation code: {reservation_code}')
        return redirect(url_for('routes.index'))
    return render_template('register.html', event=event)


@routes.route('/manage/<reservation_code>', methods=['GET', 'POST'])
def manage_reservation(reservation_code):
    reservation = Reservation.query.filter_by(reservation_code=reservation_code).first_or_404()
    if request.method == 'POST':
        db.session.delete(reservation)
        db.session.commit()
        flash('Your reservation has been canceled.')
        return redirect(url_for('routes.index'))
    return render_template('manage.html', reservation=reservation)


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
        new_user = User(email=form.email.data, password=hashed_password, is_admin=form.is_admin.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('routes.login'))
    return render_template('user_registration.html', form=form)


@routes.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('routes.index'))

    form = EventForm()
    if form.validate_on_submit():
        new_event = Event(
            title=form.title.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            thumbnail=form.thumbnail.data
        )
        db.session.add(new_event)
        db.session.commit()
        flash('Event created successfully.')
        return redirect(url_for('routes.admin_panel'))

    return render_template('admin.html', form=form)
