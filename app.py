from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# App config
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_rental.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Secret key for flash messages

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

def add_dummy_cars():
    if Car.query.count() == 0:  # Only add data if no cars exist
        cars = [
            Car(make="Toyota", model="Corolla", price_per_day=40.0, category="Sedan", available=True),
            Car(make="Ford", model="Mustang", price_per_day=80.0, category="Coupe", available=True),
            Car(make="BMW", model="X5", price_per_day=120.0, category="SUV", available=True),
            Car(make="Tesla", model="Model S", price_per_day=150.0, category="Sedan", available=True),
            Car(make="Chevrolet", model="Camaro", price_per_day=70.0, category="Coupe", available=True)
        ]
        db.session.bulk_save_objects(cars)
        db.session.commit()

# Routes
@app.route('/')
def home():
    # Render the home page
    return render_template('index.html')

# ---------- AUTH ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            flash('Email already exists!', 'error')
            return redirect(url_for('register'))

        # Create new user
        user = User(
            email=data['email'], 
            password=data['password'], 
            is_admin='is_admin' in data
        )
        db.session.add(user)
        db.session.commit()
        flash('User registered successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(email=data['email'], password=data['password']).first()

        if user:
            flash('Login successful!', 'success')
            return redirect(url_for('get_cars'))  # Use get_cars here
        else:
            flash('Invalid credentials!', 'error')

    return render_template('login.html')

# ---------- CARS ----------
@app.route('/cars', methods=['GET'])
def get_cars():
    cars = Car.query.all()
    return render_template('cars.html', cars=cars)

@app.route('/cars', methods=['POST'])
def add_car():
    data = request.form
    car = Car(
        make=data['make'],
        model=data['model'],
        price_per_day=data['price_per_day'],
        category=data['category'],
        available=True
    )
    db.session.add(car)
    db.session.commit()
    flash('Car added successfully!', 'success')
    return redirect(url_for('get_cars'))  # Corrected this

@app.route('/cars/<int:id>', methods=['DELETE'])
def delete_car(id):
    car = Car.query.get(id)
    if not car:
        flash('Car not found!', 'error')
        return redirect(url_for('get_cars'))  # Corrected this
    db.session.delete(car)
    db.session.commit()
    flash('Car deleted successfully!', 'success')
    return redirect(url_for('get_cars'))  # Corrected this

# ---------- BOOKINGS ----------
@app.route('/bookings', methods=['GET', 'POST'])
def create_booking():
    if request.method == 'POST':
        data = request.form
        car = Car.query.get(data['car_id'])
        user = User.query.get(data['user_id'])

        # Calculate total price
        start_date = data['start_date']
        end_date = data['end_date']
        total_price = (end_date - start_date) * car.price_per_day  # Simple price calculation

        booking = Booking(
            user_id=user.id,
            car_id=car.id,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price
        )

        db.session.add(booking)
        db.session.commit()
        flash('Booking created successfully!', 'success')
        return redirect(url_for('view_bookings'))  # Corrected this

    cars = Car.query.all()  # Get available cars
    return render_template('booking.html', cars=cars)

@app.route('/admin/bookings', methods=['GET'])
def view_bookings():
    bookings = Booking.query.all()
    return render_template('view_bookings.html', bookings=bookings)

# Run app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure the database tables are created
        add_dummy_cars()  # Add dummy cars if the table is empty
    app.run(debug=True)

