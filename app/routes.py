from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Event, Reservation
import random
import string

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
