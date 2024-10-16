from flask import Flask, request, jsonify, redirect, url_for, session
from admin import admin
import sqlite3
from home import home
from services import services
from employee import employee
from auth import user




app = Flask(__name__)
app.secret_key = 'my_key22'  #secret key for app


#initializing databases
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    phone_number TEXT,
                    email TEXT,
                    password TEXT,
                    status TEXT DEFAULT 'User'
                )''')

    # Create shopping_requests table
    c.execute('''
    CREATE TABLE IF NOT EXISTS shopping_requests (
        user_id INTEGER,
        shopping_id TEXT PRIMARY KEY,
        phone_number TEXT,
        home_address TEXT,
        items TEXT,
        additional_info TEXT,
        status TEXT,
        requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        assigned_to TEXT DEFAULT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Create parcels table
    c.execute('''
        CREATE TABLE IF NOT EXISTS parcels (
            parcel_id TEXT PRIMARY KEY,
            user_id INTEGER,
            recipient_name TEXT,
            recipient_address TEXT,
            recipient_phone TEXT,
            parcel_details TEXT,
            collection_point TEXT,
            additional_instructions TEXT,
            status TEXT,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            assigned_to TEXT DEFAULT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    #create surprise express table
    c.execute('''CREATE TABLE IF NOT EXISTS surprise_express (
        user_id INTEGER,
        surprise_id TEXT PRIMARY KEY,
        recipient_name TEXT,
        recipient_address TEXT,
        recipient_phone TEXT,
        surprise_details TEXT,
        status TEXT,
        requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        assigned_to TEXT DEFAULT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')

    # Create All_requests table
    c.execute('''CREATE TABLE IF NOT EXISTS All_requests (
            request_id TEXT PRIMARY KEY,
            status TEXT,
            assigned_to TEXT DEFAULT NULL
        )'''
    )

    # Create employees table
    c.execute('''CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            phone_number TEXT NOT NULL,
            request_id TEXT DEFAULT 0,
            location TEXT DEFAULT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (request_id) REFERENCES All_requests(request_id)
        )''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()


#register admin blueprint
app.register_blueprint(admin, url_prefix='/admin')


#regiser home blueprint
app.register_blueprint(home, url_prefix='/home')

#register services blueprint
app.register_blueprint(services, url_prefix='/services')

#register employee blueprint
app.register_blueprint(employee, url_prefix='/employee')

#register authentication blueprint
app.register_blueprint(user, url_prefix='/user')


#route for home page
@app.route('/')
def home():
    return redirect(url_for('home.home_page'))













if __name__ == '__main__':
    app.run(port=5050, debug=True)
