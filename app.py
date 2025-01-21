from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    date = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300))

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    medication_name = db.Column(db.String(150), nullable=False)
    schedule = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Checking if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('signup'))

        try:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    pets = Pet.query.filter_by(owner_id=current_user.id).all()

    for pet in pets:
        pet.appointments = Appointment.query.filter_by(pet_id=pet.id).all()
        pet.medications = Medication.query.filter_by(pet_id=pet.id).all()
    
    return render_template('dashboard.html', pets=pets)

@app.route('/add_pet', methods=['GET', 'POST'])
@login_required
def add_pet():
    if request.method == 'POST':
        name = request.form.get('name')
        new_pet = Pet(name=name, owner_id=current_user.id)
        db.session.add(new_pet)
        db.session.commit()
        flash('Pet added successfully!', 'success')
        return redirect(url_for('add_pet'))

    pets = Pet.query.filter_by(owner_id=current_user.id).all()
    return render_template('add_pet.html', pets=pets)

@app.route('/add_appointment/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def add_appointment(pet_id):
    if request.method == 'POST':
        date = request.form.get('date')
        description = request.form.get('description')
        new_appointment = Appointment(pet_id=pet_id, date=date, description=description)
        db.session.add(new_appointment)
        db.session.commit()
        flash('Appointment added successfully!', 'success')
        return redirect(url_for('add_appointment', pet_id=pet_id))  

    appointments = Appointment.query.filter_by(pet_id=pet_id).all()
    return render_template('add_appointment.html', pet_id=pet_id, appointments=appointments)


@app.route('/add_medication/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def add_medication(pet_id):
    if request.method == 'POST':
        medication_name = request.form.get('medication_name')
        schedule = request.form.get('schedule')
        new_medication = Medication(pet_id=pet_id, medication_name=medication_name, schedule=schedule)
        db.session.add(new_medication)
        db.session.commit()
        flash('Medication added successfully!', 'success')  
        return redirect(url_for('add_medication', pet_id=pet_id))  

    medications = Medication.query.filter_by(pet_id=pet_id).all()
    return render_template('add_medication.html', pet_id=pet_id, medications=medications)


@app.route('/contact_vet')
@login_required
def contact_vet():
    return render_template('contact_vet.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
