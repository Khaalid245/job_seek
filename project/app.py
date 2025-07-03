import os

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "application"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ File Upload Configuration (ADDED)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)

# ✅ Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)

# ✅ User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ✅ User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)

    # New fields
    skill = db.Column(db.String(200))
    bio = db.Column(db.Text)
    experience = db.Column(db.String(200))
    location = db.Column(db.String(400))  # ✅ FIXED typo: Column with capital 'C'

    profile_image = db.Column(db.String(300), nullable=True)  # ✅ Changed to nullable=True
    cv_file = db.Column(db.String(300), nullable=True)        # ✅ Changed to nullable=True

    def __repr__(self):
        return f"<User {self.username}, {self.email}>"  # ✅ Optional (debugging)


# ✅ Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Email already exists. Please login', 'danger')
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful. You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


# ✅ Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


# ✅ Dashboard route (protected)
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        current_user.skill = request.form['skill']
        current_user.bio = request.form['bio']
        current_user.experience = request.form['experience']
        current_user.location = request.form['location']  # ✅ ADDED to capture location

        profile_image = request.files['profile_image']
        if profile_image:
            filename = secure_filename(profile_image.filename)
            profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            current_user.profile_image = filename

        cv_file = request.files['cv_file']
        if cv_file:
            filename = secure_filename(cv_file.filename)
            cv_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            current_user.cv_file = filename

        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('home'))

    return render_template('dashboard.html', name=current_user.username)


# ✅ Home route
@app.route('/home')
def home():
    users = User.query.filter(User.skill != None).all()
    return render_template('home.html', user=users)


# ✅ Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ✅ Run app and create tables
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
