from flask import Flask, render_template, url_for, redirect, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "db.sqlite3")

app.config["SECRET_KEY"] = "secretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) 
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    license_plate = db.Column(db.String(20), unique=True, nullable=False)
    image_url = db.Column(db.String(255))

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False) 
    price = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')

    car = db.relationship('Car')
    user = db.relationship('User')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def is_car_available(car_id, start_date, end_date, exclude_rental_id=None):
    query = Rental.query.filter(
        Rental.car_id == car_id,
        Rental.status == 'accepted',
        Rental.start_date <= end_date,
        Rental.end_date >= start_date
    )
    if exclude_rental_id:
        query = query.filter(Rental.id != exclude_rental_id)

    overlapping = query.first()
    return overlapping is None


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('admin' if user.username == 'admin' else 'index'))
        flash('Invalid credentials.', 'error')
    return render_template('login.html')

def add_admin_user():
    admin_username = "admin"
    admin_password = "admin"
    existing_admin = User.query.filter_by(username=admin_username).first()
    if not existing_admin:
        hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256')
        admin_user = User(username=admin_username, password=hashed_password)
        db.session.add(admin_user)
        db.session.commit()

@app.route('/')
@login_required
def index():
    if current_user.username == 'admin':
        return redirect(url_for('admin'))

    today = date.today()

    active_rentals = Rental.query.filter(
        Rental.status == 'accepted',
        Rental.start_date <= today,
        Rental.end_date >= today
    ).all()

    rented_car_ids = [rental.car_id for rental in active_rentals]

    available_cars = Car.query.filter(~Car.id.in_(rented_car_ids)).all()

    print(f"Bugün müsait araç sayısı: {len(available_cars)}")

    return render_template('index.html', cars=available_cars)

@app.route('/add_to_cart/<int:car_id>')
@login_required
def add_to_cart(car_id):
    car = Car.query.get(car_id)
    if not car:
        flash("Car not found.", "error")
        return redirect(url_for('index'))

    cart = session.get('cart', [])
    if any(item['id'] == car.id for item in cart):
        flash("Car already in cart.", "warning")
    else:
        cart.append({'id': car.id, 'name': car.name, 'price': car.price, 'image_url': car.image_url})
        session['cart'] = cart
        flash(f"{car.name} added to cart.", "success")

    return redirect(url_for('index'))

@app.route('/rent/<int:car_id>', methods=['GET', 'POST'])
@login_required
def rent_car(car_id):
    car = Car.query.get(car_id)
    if not car:
        flash('Car not found.', 'error')
        return redirect(url_for('index'))

    today = date.today().isoformat()

    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'error')
            return redirect(request.url)

        if end_date < start_date:
            flash('End date cannot be before start date.', 'error')
            return redirect(request.url)

        if start_date < date.today():
            flash('Start date cannot be in the past.', 'error')
            return redirect(request.url)

        if not is_car_available(car.id, start_date, end_date):
            flash('Car is not available in the selected date range.', 'error')
            return redirect(request.url)

        rental_days = (end_date - start_date).days + 1
        total_price = rental_days * car.price

        cart = session.get('cart', [])
        cart.append({
            'id': car.id,
            'name': car.name,
            'price': total_price,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'rental_days': rental_days
        })
        session['cart'] = cart
        flash(f'{car.name} rented for {rental_days} days. Total price: {total_price} TL', 'success')
        return redirect(url_for('cart'))

    return render_template('rent_form.html', car=car, today=today)

@app.route('/remove_from_cart/<int:index>')
@login_required
def remove_from_cart(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        removed = cart.pop(index)
        session['cart'] = cart
        flash(f'Removed {removed["name"]} from cart.', 'success')
    else:
        flash('Item not found in cart.', 'error')
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    cart_items = session.get('cart', [])
    
    total = sum(item['price'] for item in cart_items)
    
    rentals = Rental.query.filter_by(user_id=current_user.id).all()
    
    return render_template('cart.html', cart_items=cart_items, total=total, rentals=rentals)

@app.route('/complete_rental')
@login_required
def complete_rental():
    cart = session.get('cart', [])
    if not cart:
        flash("Cart is empty.", "error")
        return redirect(url_for('cart'))

    for item in cart:
        rental = Rental(
            user_id=current_user.id,
            car_id=item['id'],  
            price=item['price'],
            start_date=datetime.strptime(item['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(item['end_date'], '%Y-%m-%d').date(),
            status='pending'
        )
        db.session.add(rental)
    db.session.commit()

    session['cart'] = []  
    flash("Rental request received, awaiting approval.", "success")
    return redirect(url_for('cart'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin():
    if current_user.username != 'admin':
        flash("Admin login required.", "error")
        return redirect(url_for('login'))

    users = User.query.all()
    rentals = Rental.query.order_by(Rental.status).all()
    cars = Car.query.all()
    return render_template('admin.html', users=users, rentals=rentals, cars=cars)

@app.route('/admin/approve/<int:rental_id>')
@login_required
def approve_rental(rental_id):
    if current_user.username != 'admin':
        flash("Only admins can approve rentals.", "error")
        return redirect(url_for('login'))

    rental = Rental.query.get_or_404(rental_id)

    if not is_car_available(rental.car_id, rental.start_date, rental.end_date, exclude_rental_id=rental.id):
        flash("This car is already rented during that period.", "error")
        return redirect(url_for('admin'))

    rental.status = 'accepted'
    db.session.commit()
    flash("Rental approved successfully.", "success")
    return redirect(url_for('admin'))

@app.route('/admin/reject/<int:rental_id>')
@login_required
def reject_rental(rental_id):
    if current_user.username != 'admin':
        flash("Only admins can reject rentals.", "error")
        return redirect(url_for('login'))

    rental = Rental.query.get_or_404(rental_id)
    db.session.delete(rental)
    db.session.commit()
    flash("Rental request rejected and removed.", "success")
    return redirect(url_for('admin'))

def get_active_rentals(user_id):
    today = date.today()
    rentals = Rental.query.filter(
        Rental.user_id == user_id,
        Rental.status == 'accepted',
        Rental.end_date >= today
    ).all()
    return rentals

@app.route('/admin/edit_car/<int:car_id>', methods=['GET', 'POST'])
@login_required
def edit_car(car_id):
    if current_user.username != 'admin':
        flash("Only admins can edit cars.", "error")
        return redirect(url_for('login'))

    car = Car.query.get_or_404(car_id)

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        image_url = request.form.get('image_url')

        if not name or not price or not image_url:
            flash("All fields are required.", "error")
            return redirect(request.url)

        try:
            price = float(price)
        except ValueError:
            flash("Price must be a number.", "error")
            return redirect(request.url)

        car.name = name
        car.price = price
        car.image_url = image_url
        db.session.commit()
        flash("Car updated successfully.", "success")
        return redirect(url_for('admin'))

    return render_template('edit_car.html', car=car)

@app.route('/admin/delete_car/<int:car_id>', methods=['POST'])
@login_required
def delete_car(car_id):
    if current_user.username != 'admin':
        flash("Only admins can delete cars.", "error")
        return redirect(url_for('login'))

    car = Car.query.get_or_404(car_id)
    db.session.delete(car)
    db.session.commit()
    flash("Car deleted successfully.", "success")
    return redirect(url_for('admin'))

@app.route('/admin/add_car', methods=['GET', 'POST'])
@login_required
def add_car():
    if current_user.username != 'admin':
        flash("Yetkisiz erişim.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name')
        brand = request.form.get('brand')
        model = request.form.get('model')
        year = request.form.get('year')
        price = request.form.get('price')
        license_plate = request.form.get('license_plate')
        image_url = request.form.get('image_url')  # e.g., 'araba.png'

        if not (name and brand and model and year and price and license_plate):
            flash("Tüm alanlar doldurulmalıdır.", "error")
            return redirect(request.url)

        try:
            year = int(year)
            price = float(price)
        except ValueError:
            flash("Yıl tam sayı, fiyat sayısal olmalıdır.", "error")
            return redirect(request.url)

        existing = Car.query.filter_by(license_plate=license_plate).first()
        if existing:
            flash("Bu plakaya sahip bir araç zaten var.", "error")
            return redirect(request.url)

        full_image_url = f"images/{image_url}" if image_url else None

        new_car = Car(
            name=name,
            brand=brand,
            model=model,
            year=year,
            price=price,
            license_plate=license_plate,
            image_url=full_image_url
        )
        db.session.add(new_car)
        db.session.commit()

        flash("Araç başarıyla eklendi.", "success")
        return redirect(url_for('admin'))

    return render_template('add_car.html')


def add_sample_cars():
    sample_cars = [
        {
            "name": "Toyota Corolla",
            "brand": "Toyota",
            "model": "Corolla",
            "year": 2020,
            "price": 45,
            "license_plate": "ABC123",
            "image_url": "images/corolla.png"
        },
        {
            "name": "Ford Focus",
            "brand": "Ford",
            "model": "Focus",
            "year": 2018,
            "price": 50,
            "license_plate": "DEF456",
            "image_url": "images/focus.png"
        },
        {
            "name": "Volkswagen Golf",
            "brand": "Volkswagen",
            "model": "Golf",
            "year": 2019,
            "price": 55,
            "license_plate": "GHI789",
            "image_url": "images/golf.png"
        },
        {
            "name": "Honda Civic",
            "brand": "Honda",
            "model": "Civic",
            "year": 2019,
            "price": 60,
            "license_plate": "JKL012",
            "image_url": "images/civic.png"
        },
        {
            "name": "BMW 3 Series",
            "brand": "BMW",
            "model": "3 Series",
            "year": 2021,
            "price": 80,
            "license_plate": "MNO345",
            "image_url": "images/bmw3.png"
        },
        {
            "name": "Audi A4",
            "brand": "Audi",
            "model": "A4",
            "year": 2020,
            "price": 85,
            "license_plate": "PQR678",
            "image_url": "images/audi_a4.png"
        },
        {
            "name": "Mercedes-Benz C-Class",
            "brand": "Mercedes-Benz",
            "model": "C-Class",
            "year": 2021,
            "price": 90,
            "license_plate": "STU901",
            "image_url": "images/mercedes_c.png"
        },
        {
            "name": "Nissan Sentra",
            "brand": "Nissan",
            "model": "Sentra",
            "year": 2017,
            "price": 40,
            "license_plate": "VWX234",
            "image_url": "images/sentra.png"
        },
        {
            "name": "Hyundai Elantra",
            "brand": "Hyundai",
            "model": "Elantra",
            "year": 2018,
            "price": 50,
            "license_plate": "YZA567",
            "image_url": "images/elantra.png"
        },
        {
            "name": "Kia Forte",
            "brand": "Kia",
            "model": "Forte",
            "year": 2019,
            "price": 55,
            "license_plate": "BCD890",
            "image_url": "images/forte.png"
        }
    ]

    for car_data in sample_cars:
        existing_car = Car.query.filter_by(brand=car_data['brand'], model=car_data['model']).first()
        if not existing_car:
            new_car = Car(**car_data)
            db.session.add(new_car)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if not Car.query.first():
            add_sample_cars()

        if not User.query.filter_by(username='admin').first():
            add_admin_user()

    app.run(debug=True)