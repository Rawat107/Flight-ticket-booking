from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flight_booking.db'
db = SQLAlchemy(app)

# Define models

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False) 

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(10), unique=True, nullable=False)
    departure_time = db.Column(db.String(20), nullable=False)
    seat_count = db.Column(db.Integer, nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='bookings') 

with app.app_context():
    db.create_all()

    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(username='admin', password='adminpassword', is_admin=True)  
        db.session.add(admin_user)
        db.session.commit()

@app.route('/user/signup', methods=['POST'])
def user_signup():
    data = request.json
    username = data['username']
    password = data['password']
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return "User signed up successfully"

@app.route('/user/login', methods=['POST'])
def user_login():
    data = request.json
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        return "User logged in successfully"
    else:
        return "Invalid username or password"

@app.route('/flights/search', methods=['GET'])
def search_flights():
    departure_time = request.args.get('departure_time')
    flights = Flight.query.filter_by(departure_time=departure_time).all()

    if not flights:
        return jsonify({'message': 'No flights found for the given departure time.'}), 404

    flight_info = [{'flight_number': flight.flight_number, 'seat_count': flight.seat_count} for flight in flights]
    return jsonify({'flights': flight_info}), 200

@app.route('/flights/book', methods=['POST'])
def book_flight():
    data = request.json
    flight_number = data['flight_number']
    username = data['username']
    
    # Check if the flight exists
    flight = Flight.query.filter_by(flight_number=flight_number).first()
    if flight is None:
        return "Flight not found", 404
    
    # Check if there are available seats
    if flight.seat_count > 0:
        # Book the flight
        new_booking = Booking(flight_id=flight.id, user_id=username)
        db.session.add(new_booking)
        flight.seat_count -= 1
        db.session.commit()
        return "Ticket booked successfully"
    else:
        return "No seats available"

@app.route('/user/bookings', methods=['GET'])
def user_bookings():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Missing username parameter.'}), 400

    # Verify if the user exists
    user = User.query.filter_by(username=username).one_or_none()
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    # Retrieve bookings associated with the user
    bookings = Booking.query.filter_by(user_id=user.username).all()
    if not bookings:
        return jsonify({'message': 'No bookings found for this user.'}), 200

    formatted_bookings = []
    for booking in bookings:
        flight = Flight.query.get(booking.flight_id)
        if flight:
            formatted_booking = {
                'flight_number': flight.flight_number,
                'departure_time': flight.departure_time
            }
            formatted_bookings.append(formatted_booking)

    if not formatted_bookings:
        return jsonify({'message': 'No valid bookings found for this user.'}), 200

    return jsonify(formatted_bookings), 200


@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Check if the user is an admin
    user = User.query.filter_by(username=username, password=password, is_admin=True).first()
    if user:
        # Generate a unique admin authentication token
        admin_auth_token = secrets.token_hex(16)
        return jsonify({'message': 'Admin logged in successfully', 'admin_auth_token': admin_auth_token}), 200
    else:
        return jsonify({'error': 'Invalid admin credentials'}), 401

@app.route('/admin/flights/add', methods=['POST'])
def add_flight():
    data = request.json

    admin_auth_token = request.headers.get('Authorization')
    if not admin_auth_token or not admin_auth_token.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized access. Missing or invalid admin authentication token.'}), 401
    admin_auth_token = admin_auth_token.split(' ')[1]

    flight_number = data.get('flight_number')
    departure_time = data.get('departure_time')
    seat_count = data.get('seat_count')

    if not all([flight_number, departure_time, seat_count]):
        return jsonify({'error': 'Missing required data. Please provide flight_number, departure_time, and seat_count.'}), 400

    # Check if the flight number already exists
    existing_flight = Flight.query.filter_by(flight_number=flight_number).first()
    if existing_flight:
        return jsonify({'error': 'Flight with the same number already exists.'}), 409

    # Create a new flight record
    new_flight = Flight(flight_number=flight_number, departure_time=departure_time, seat_count=seat_count)
    db.session.add(new_flight)
    db.session.commit()

    return jsonify({'message': 'Flight added successfully'}), 201
    
@app.route('/admin/flights/remove', methods=['POST'])
def remove_flight():
    data = request.json

    admin_auth_token = request.headers.get('Authorization')
    if not admin_auth_token or not admin_auth_token.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized access. Missing or invalid admin authentication token.'}), 401
    admin_auth_token = admin_auth_token.split(' ')[1]

    flight_number = data.get('flight_number')

    if not flight_number:
        return jsonify({'error': 'Missing required data. Please provide flight_number.'}), 400

    # Find and delete the flight
    flight = Flight.query.filter_by(flight_number=flight_number).first()
    if flight:
        db.session.delete(flight)
        db.session.commit()
        return jsonify({'message': 'Flight removed successfully'}), 200
    else:
        return jsonify({'error': 'Flight not found'}), 404

@app.route('/admin/bookings', methods=['GET'])
def admin_bookings():
    # Verify admin credentials
    admin_auth_token = request.headers.get('Authorization')
    if not admin_auth_token or not admin_auth_token.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized access. Missing or invalid admin authentication token.'}), 401
    admin_auth_token = admin_auth_token.split(' ')[1]

    bookings = Booking.query.all()

    formatted_bookings = []
    for booking in bookings:
        flight = Flight.query.get(booking.flight_id)
        user = User.query.get(booking.user_id)
        if user:
            formatted_booking = {
                'flight_number': flight.flight_number,
                'departure_time': flight.departure_time,
                'user_id': booking.user_id,
                'username': user.username  
            }
            formatted_bookings.append(formatted_booking)
        else:
            # Handle the case where the user does not exist
            formatted_booking = {
                'flight_number': flight.flight_number,
                'departure_time': flight.departure_time,
                'user_id': booking.user_id,
                'username': 'User not found'  
            }
            formatted_bookings.append(formatted_booking)

    return jsonify(formatted_bookings), 200


if __name__ == '__main__':
    app.run(debug=True)
