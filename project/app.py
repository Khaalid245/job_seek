from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "application"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

# ✅ Home route
@app.route('/home')
def home():
    return render_template('home.html')

# ✅ Dashboard route (protected)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

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
