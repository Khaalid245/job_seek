# 🔐 Flask Login & Signup App (Practice Project)

This is a beginner-friendly Flask web application designed to help me practice the core concepts of building user authentication systems using Flask, Flask-Login, SQLAlchemy, and Bootstrap.

## 🧠 Project Idea

The goal of this project was to:
- Learn the basics of Flask and web development
- Build a single-page application that includes both login and signup forms
- Use sessions and secure password hashing
- Store user data using SQLite and SQLAlchemy
- Flash messages and user-friendly design with Bootstrap

## 📦 Features

- 🔑 User Signup (register with username, email, and password)
- 🔐 User Login (with password validation)
- ✅ Protected Dashboard page (only for logged-in users)
- 🚪 Logout functionality
- 🧠 Flash messages (success, error alerts)
- 🎨 Bootstrap styling
- 📄 All routes handled in one Python file (`app.py`)
- 🗂️ Login and Signup on the **same page**

## 🛠️ Technologies Used

- Python 3
- Flask
- Flask-Login
- Flask-SQLAlchemy
- SQLite (for the database)
- Bootstrap 5
- Jinja2 (Flask template engine)
- Werkzeug (for password hashing)

## 🗂️ File Structure

```
project-folder/
│
├── app.py                 # Main Flask app logic
├── users.db               # SQLite database (auto-generated)
└── templates/
    ├── layout.html        # Base layout with Bootstrap
    └── login_signup.html  # Combined login & signup form
```

## 🚀 How to Run the App

1. Clone this repository or download the code.
2. Install dependencies:
   ```bash
   pip install flask flask_sqlalchemy flask_login
   ```
3. Run the app:
   ```bash
   python app.py
   ```
4. Visit `http://127.0.0.1:5000/login-signup` in your browser.

## 📚 What I Learned

- How to break a Flask app into understandable parts
- How to structure user models and hash passwords securely
- How Flask routes connect with HTML templates via Jinja
- How to show and style flash messages
- How to protect pages using `@login_required`

## ✅ Future Plans

- Add skill submission form inside the user dashboard
- Allow admin to view a list of all registered users
- Send confirmation emails (using Flask-Mail)
- Store profile pictures or resumes

## 🙌 Acknowledgements

This project was built as part of my personal practice to understand Flask and full-stack web development better. Inspired by the goal of building professional apps from the ground up.

---

**Made with ❤️ by Khalid**
