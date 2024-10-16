from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps



user = Blueprint('user', __name__, template_folder='templates', url_prefix='/user')



#route for user registration
@user.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username') 
        phone_number = request.form.get('phone_number')
        email = request.form.get('email') 
        password = request.form.get('password') 
        
        # Optional: Validate input
        if not username or not password:
            return render_template('signup.html', error="Username and password are required")  # Render form with error
        
        password_hash = generate_password_hash(password)  # Hash the password
        
        # Database connection and user creation
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, phone_number, email, password) VALUES (?,?,?,?)', (username, phone_number, email, password_hash))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))  # Redirect to login after successful registration
    
    return render_template('signup.html')  # Render signup page for GET requests

#decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

#route for user login
@user.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')  # Using get() to avoid KeyError
        password = request.form.get('password')  # Using get() to avoid KeyError
        print(email, password)

        if not email or not password:
            return "Please provide both email and password", 400  # Bad request response

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        print(user)

        if user and check_password_hash(user[4], password):
            session['user_id'] = user[0]
            if user[5] == 'Admin':
                return redirect(url_for('admin.dashboard'))
            elif user[5] == 'Employee':
                return redirect(url_for('employee.employee_dashboard'))
            else:
                return redirect(url_for('home.home_page'))
        else:
            return "Invalid email or password", 401
        
    return render_template('login.html')

#route for user logout
@user.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)  # Remove the user_id from the session
    return redirect(url_for('home'))  # Redirect to the homepage after logout
