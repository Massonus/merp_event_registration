import random
import string
from datetime import datetime

from flask import Blueprint, jsonify, request

from app import db
from app.models import Event, Reservation

api = Blueprint('api', __name__)


def generate_reservation_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


@api.route('/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    events_data = []
    for event in events:
        event_info = {
            'id': event.id,
            'title': event.title,
            'start_date': event.start_date,
            'thumbnail': event.thumbnail
        }
        events_data.append(event_info)
    return jsonify(events_data)


@api.route('/reservations', methods=['GET'])
def get_reservations():
    email = request.args.get('email')

    reservations = Reservation.query.filter_by(email=email).all()

    reservations_data = [
        {
            'id': reservation.id,
            'event_id': reservation.event_id,
            'email': reservation.email,
            'reservation_code': reservation.reservation_code,
            'event_title': reservation.event.title
        } for reservation in reservations
    ]

    return jsonify(reservations_data)


@api.route('/register', methods=['POST'])
def api_register():
    data = request.get_json()
    event_id = data.get('event_id')
    email = data.get('email')

    event = Event.query.get_or_404(event_id)

    reservation_code = generate_reservation_code()

    existing_reservation = Reservation.query.filter_by(event_id=event.id, email=email).first()
    if existing_reservation:
        return jsonify({'error': 'You have already registered for this event.'}), 400

    reservation = Reservation(event_id=event.id, email=email, reservation_code=reservation_code)
    db.session.add(reservation)
    db.session.commit()

    return jsonify({'message': 'Registration successful!', 'reservation_code': reservation_code}), 201


@api.route('/cancel-reservation', methods=['POST'])
def api_cancel_reservation():
    data = request.get_json()
    reservation_id = data.get('reservation_id')
    email = data.get('email')

    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.email != email:
        return jsonify({'error': 'You cannot cancel this reservation.'}), 403

    db.session.delete(reservation)
    db.session.commit()

    return jsonify({'message': 'Reservation canceled successfully.'}), 200


@api.route('/edit-event', methods=['PUT'])
def api_edit_event():
    data = request.get_json()
    event_id = data.get('event_id')
    event = Event.query.get_or_404(event_id)

    event.title = data.get('title')
    event.start_date = datetime.fromisoformat(data.get('start_date'))
    event.end_date = datetime.fromisoformat(data.get('end_date'))
    event.thumbnail = data.get('thumbnail')
    db.session.commit()

    return jsonify({'message': 'Event updated successfully.'}), 200


@api.route('/delete-event', methods=['DELETE'])
def api_delete_event():
    data = request.get_json()
    event_id = data.get('event_id')
    event = Event.query.get_or_404(event_id)

    reservations = Reservation.query.filter_by(event_id=event_id).all()
    for reservation in reservations:
        db.session.delete(reservation)

    db.session.delete(event)
    db.session.commit()

    return jsonify({'message': 'Event deleted successfully.'}), 200


@api.route('/create-event', methods=['POST'])
def api_create_event():
    data = request.get_json()
    new_event = Event(
        title=data.get('title'),
        start_date=datetime.fromisoformat(data.get('start_date')),
        end_date=datetime.fromisoformat(data.get('end_date')),
        thumbnail=data.get('thumbnail')
    )
    db.session.add(new_event)
    db.session.commit()

    return jsonify({'message': 'Event created successfully.'}), 200
