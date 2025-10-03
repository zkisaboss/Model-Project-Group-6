from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# App config
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_rental.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    price_per_day = db.Column(db.Float)
    category = db.Column(db.String(50))
    available = db.Column(db.Boolean, default=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    total_price = db.Column(db.Float)

# Routes

# ---------- AUTH ----------
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    user = User(email=data['email'], password=data['password'], is_admin=data.get('is_admin', False))
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email'], password=data['password']).first()
    if user:
        return jsonify({'message': 'Login successful', 'user_id': user.id, 'is_admin': user.is_admin})
    return jsonify({'error': 'Invalid credentials'}), 401

# ---------- CARS ----------
@app.route('/cars', methods=['GET'])
def get_cars():
    cars = Car.query.all()
    return jsonify([{
        'id': car.id,
        'make': car.make,
        'model': car.model,
        'price_per_day': car.price_per_day,
        'category': car.category,
        'available': car.available
    } for car in cars])

@app.route('/cars', methods=['POST'])
def add_car():
    data = request.json
    car = Car(
        make=data['make'],
        model=data['model'],
        price_per_day=data['price_per_day'],
        category=data['category'],
        available=True
    )
    db.session.add(car)
    db.session.commit()
    return jsonify({'message': 'Car added successfully'})

@app.route('/cars/<int:id>', methods=['DELETE'])
def delete_car(id):
    car = Car.query.get(id)
    if not car:
        return jsonify({'error': 'Car not found'}), 404
    db.session.delete(car)
    db.session.commit()
    return jsonify({'message': 'Car deleted'})

# ---------- BOOKINGS ----------
@app.route('/bookings', methods=['POST'])
def create_booking():
    data = request.json
    booking = Booking(
        user_id=data['user_id'],
        car_id=data['car_id'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        total_price=data['total_price']
    )
    db.session.add(booking)
    db.session.commit()

    print(f"Booking confirmed for user {data['user_id']} – confirmation email sent (mock)")
    return jsonify({'message': 'Booking created successfully'})

@app.route('/admin/bookings', methods=['GET'])
def view_bookings():
    bookings = Booking.query.all()
    return jsonify([{
        'id': b.id,
        'user_id': b.user_id,
        'car_id': b.car_id,
        'start_date': b.start_date,
        'end_date': b.end_date,
        'total_price': b.total_price
    } for b in bookings])

# ---------- INIT DB ----------
@app.before_first_request
def create_tables():
    db.create_all()

# Run app
if __name__ == '__main__':
    app.run(debug=True)
