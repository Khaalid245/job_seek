import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "application"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File Upload Configuration
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='job_seeker')
    skill = db.Column(db.String(200))
    bio = db.Column(db.Text)
    experience = db.Column(db.String(200))
    location = db.Column(db.String(400))
    profile_image = db.Column(db.String(300), nullable=True)
    cv_file = db.Column(db.String(300), nullable=True)
    jobs = db.relationship('Job', backref='poster', lazy=True)

    def __repr__(self):
        return f"<User {self.username}, {self.email}, {self.role}>"

# Job model
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    company_website = db.Column(db.String(300))
    company_logo = db.Column(db.String(300))
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    skills = db.Column(db.String(300))
    education_level = db.Column(db.String(50))
    salary = db.Column(db.String(50))
    job_type = db.Column(db.String(50), nullable=False)
    expiration_date = db.Column(db.Date)
    application_method = db.Column(db.String(50), nullable=False)
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please login', 'danger')
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password, role=role)

        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful. You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            if user.role == 'company':
                return redirect(url_for('company_dashboard'))
            else:
                return redirect(url_for('jobseeker_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Jobseeker Dashboard
@app.route('/dashboard/jobseeker', methods=['GET', 'POST'])
@login_required
def jobseeker_dashboard():
    if current_user.role != 'job_seeker':
        flash("Access denied", 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        current_user.username = request.form['username']
        current_user.email = request.form['email']
        current_user.skill = request.form['skill']
        current_user.bio = request.form['bio']
        current_user.experience = request.form['experience']
        current_user.location = request.form['location']

        profile_image = request.files['profile_image']
        if profile_image and profile_image.filename != '':
            filename = secure_filename(profile_image.filename)
            profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            current_user.profile_image = filename

        cv_file = request.files['cv_file']
        if cv_file and cv_file.filename != '':
            filename = secure_filename(cv_file.filename)
            cv_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            current_user.cv_file = filename

        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('jobseeker_dashboard'))

    return render_template('dashboard_jobseeker.html', user=current_user)

# Company Dashboard
@app.route('/dashboard/company', methods=['GET', 'POST'])
@login_required
def company_dashboard():
    if current_user.role != 'company':
        flash("Access denied", 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        company_name = request.form['company_name']
        company_website = request.form.get('company_website')
        job_title = request.form['job_title']
        job_description = request.form['job_description']
        location = request.form['location']
        skills = ','.join(request.form.getlist('skills'))
        education_level = request.form.get('education_level')
        salary = request.form.get('salary')
        job_type = request.form['job_type']
        expiration_date_str = request.form.get('expiration_date')
        expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date() if expiration_date_str else None
        application_method = request.form['application_method']

        company_logo = None
        if 'company_logo' in request.files:
            file = request.files['company_logo']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                company_logo = filename

        new_job = Job(
            company_name=company_name,
            company_website=company_website,
            company_logo=company_logo,
            job_title=job_title,
            job_description=job_description,
            location=location,
            skills=skills,
            education_level=education_level,
            salary=salary,
            job_type=job_type,
            expiration_date=expiration_date,
            application_method=application_method,
            posted_by=current_user.id
        )

        db.session.add(new_job)
        db.session.commit()
        flash('Job posted successfully!', 'success')

    jobs = Job.query.filter_by(posted_by=current_user.id).all()
    return render_template('dashboard_company.html', name=current_user.username, jobs=jobs)

# Edit Job Route
@app.route('/dashboard/company/job/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    if current_user.role != 'company':
        flash("Access denied", 'danger')
        return redirect(url_for('home'))

    job = Job.query.get_or_404(job_id)
    if job.poster.id != current_user.id:
        flash("You can only edit your own jobs", 'danger')
        return redirect(url_for('company_dashboard'))

    if request.method == 'POST':
        job.company_name = request.form['company_name']
        job.company_website = request.form.get('company_website')
        job.job_title = request.form['job_title']
        job.job_description = request.form['job_description']
        job.location = request.form['location']
        job.skills = request.form['skills']
        job.education_level = request.form.get('education_level')
        job.salary = request.form.get('salary')
        job.job_type = request.form['job_type']
        expiration_date_str = request.form.get('expiration_date')
        job.expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date() if expiration_date_str else None
        job.application_method = request.form['application_method']

        if 'company_logo' in request.files:
            file = request.files['company_logo']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                job.company_logo = filename

        db.session.commit()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('company_dashboard'))

    return render_template('edit_job.html', job=job)

# Delete Job Route
@app.route('/dashboard/company/job/<int:job_id>/delete', methods=['POST'])
@login_required
def delete_job(job_id):
    if current_user.role != 'company':
        flash("Access denied", 'danger')
        return redirect(url_for('home'))

    job = Job.query.get_or_404(job_id)
    if job.poster.id != current_user.id:
        flash("You can only delete your own jobs", 'danger')
        return redirect(url_for('company_dashboard'))

    db.session.delete(job)
    db.session.commit()
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('company_dashboard'))

# Home route
@app.route('/')
def home():
    users = User.query.filter(User.skill != None).all()
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template('home.html', users=users, jobs=jobs)

# Jobseekers route
@app.route('/jobseekers')
def job_seekers():
    users = User.query.filter(User.skill != None).all()
    return render_template('job_seekers.html', users=users)

# Filter jobs API
@app.route('/api/jobs/filter', methods=['GET'])
@login_required
def filter_jobs():
    query = Job.query.filter_by(posted_by=current_user.id)

    job_type = request.args.get('job_type')
    if job_type:
        query = query.filter_by(job_type=job_type)

    education_level = request.args.get('education_level')
    if education_level:
        query = query.filter_by(education_level=education_level)

    search_term = request.args.get('search')
    if search_term:
        query = query.filter(Job.job_title.contains(search_term) |
                             Job.job_description.contains(search_term) |
                             Job.company_name.contains(search_term))

    jobs = query.all()

    jobs_data = [{
        'id': job.id,
        'company_name': job.company_name,
        'job_title': job.job_title,
        'location': job.location,
        'job_type': job.job_type,
        'salary': job.salary
    } for job in jobs]

    return jsonify(jobs_data)

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Run app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)