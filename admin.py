from flask import Blueprint, render_template, redirect, url_for, request, flash, session
import sqlite3
from utils import update_request_status, get_users_with_request_id_0, generate_id

admin = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates')


# Admin dashboard
@admin.route('/home', methods=['GET'])
@admin.route('/', methods=['GET'])
def dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Fetch and categorize requests
    c.execute('SELECT request_id, status, assigned_to FROM All_requests WHERE status = "Request Received"')
    received_requests = c.fetchall()
    
    c.execute('SELECT request_id, status, assigned_to FROM All_requests WHERE status = "In Transit"')
    in_transit_requests = c.fetchall()
    
    c.execute('SELECT request_id, status, assigned_to FROM All_requests WHERE status = "Completed"')
    completed_requests = c.fetchall()
    
    c.execute('SELECT request_id, status, assigned_to FROM All_requests WHERE status = "Cancelled"')
    cancelled_requests = c.fetchall()

    c.execute('SELECT request_id, status, assigned_to FROM All_requests WHERE status = "Request Approved"')
    approved_requests = c.fetchall()

    c.execute('SELECT request_id, status, assigned_to FROM All_requests WHERE status = "In Progress"')
    in_progress_requests = c.fetchall()

    conn.close()
    
    return render_template('admin_dashboard.html', 
                           received_requests=received_requests, 
                           in_transit_requests=in_transit_requests,
                           completed_requests=completed_requests, 
                           cancelled_requests=cancelled_requests,
                           approved = approved_requests,
                           in_progress = in_progress_requests,)

#route for viewing all employees and users
@admin.route('/employees', methods=['GET'])
def admin_employees():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Fetch employees
    c.execute('SELECT * FROM users where status = "Employee"')  # Adjust as necessary
    employees = c.fetchall()

    # Fetch users (you may have a different query depending on your users table)
    c.execute('SELECT * FROM users where status = "User"')  # Adjust as necessary
    users = c.fetchall()
    print(users)
    conn.close()
    
    return render_template('employees.html', employees=employees, users=users)

#route for promoting usr to employee
@admin.route('/promote/<int:id>', methods=['POST'])
def promote_user(id):
    conn = sqlite3.connect('database.db')

    user = conn.execute('SELECT * FROM users WHERE id = ?', (id,)).fetchone()
    if not user:
        flash('User not found!')
        return redirect(url_for('admin.admin_employees'))
    user_name = user[1]
    user_phoneNumber = user[2]
        
    # Update the user role to employee
    conn.execute('UPDATE users SET status = "Employee" WHERE id = ?', (id,))
    #add user to employee table
    conn.execute('INSERT INTO employees (user_id, phone_number, request_id) VALUES (?, ?, ?)', (id, user_phoneNumber, '0'))
    conn.commit()
    conn.close()
    
    flash('User has been promoted to employee successfully!')
    return redirect(url_for('admin.admin_employees'))

#route for viewing parcels
@admin.route('/parcels', methods=['GET'])
def admin_parcels():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM parcels')
    parcels = c.fetchall()
    employees = get_users_with_request_id_0()
    print(employees)
    conn.close()


    return render_template('admin_parcels.html', parcels=parcels,employees=employees)


#route to update parcel status
@admin.route('/update_status/<string:parcel_id>', methods=['POST'])
def update_status(parcel_id):
    print(f"Parcel ID: {parcel_id}")
    return update_request_status(parcel_id, 'parcel', 'admin.admin_parcels')

#route for viewing shopping requests
@admin.route('/shopping', methods=['GET'])
def admin_shopping():  
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM shopping_requests join users on shopping_requests.user_id = users.id')
    shopping_requests = c.fetchall()
    employees = get_users_with_request_id_0()

    conn.close()
    print(shopping_requests)

    return render_template('admin_shopping.html', shopping_requests=shopping_requests, employees=employees)

#route to update shopping request status
@admin.route('/update_shopping_status/<string:shopping_id>', methods=['POST'])
def update_shopping_status(shopping_id):
    return update_request_status(shopping_id, 'shopping', 'admin.admin_shopping')

#route for viewing all surprise express
@admin.route('/surprise_express')
def admin_surprise_express():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM surprise_express join users on surprise_express.user_id = users.id')
    surprise_express = c.fetchall()
    employees = get_users_with_request_id_0()

    conn.close()
    print(surprise_express)


    return render_template('admin_surprise_express.html', surprise_express=surprise_express, employees=employees)