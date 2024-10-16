from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from auth import login_required
import sqlite3


employee = Blueprint('employee', __name__, url_prefix='/employee', template_folder='templates')


#route for employee dashboard
@employee.route('/dashboard', methods=['GET'])
@login_required
def employee_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Assuming you have an employee table with a column for the employee's name
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    employee = c.fetchone()

    if employee:
        request_id = employee[3]
        employee_name = employee[1]

        # Fetch requests associated with the employee
        c.execute('SELECT * FROM All_requests WHERE assigned_to = ? AND status NOT IN (?, ?, ?, ?, ?)', (employee_name, 'Completed', 'Cancelled', 'Request Approved', 'In Progress', 'In Transit'))
        requests = c.fetchall()
        request_id = requests[0][0] if requests else '0'
        if request_id:
            if 'SHP' in request_id:
                c.execute('SELECT * FROM shopping_requests WHERE shopping_id = ?', (request_id,))
                request_details = c.fetchone()
                request_type = 'shopping'

            else:
                c.execute('SELECT * FROM parcels WHERE parcel_id = ?', (request_id,))
                request_details = c.fetchone()
                request_type = 'parcel'

    else:
        requests = []

    conn.close()
    print(request_details)
    return render_template('employee_dashboard.html', request_details = request_details, request_type = request_type, requests=requests)


#route for employee to view requests
@employee.route('/fetch_employee_requests', methods=['GET', 'POST'])
@login_required
def fetch_employee_requests():
    employee_id = session['user_id']
    print(f"Employee ID: {employee_id}")

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Fetch username
    c.execute('SELECT username FROM users WHERE id = ?', (employee_id,))
    employee_username = c.fetchone()

    if employee_username is None:
        conn.close()
        return "User not found", 404  # Handle user not found
    
    employee_username = employee_username[0]  # Corrected index
    print(f"Employee Username: {employee_username}")

    # Fetch all records from All_requests table assigned to the employee
    c.execute('SELECT * FROM All_requests WHERE assigned_to = ?', (employee_username,))
    requests = c.fetchall()
    
    # Initialize a list to store request details
    detailed_requests = []

    # Fetch request details
    for request in requests:
        request_id = request[0]
        if 'SHP' in request_id:  # Shopping request
            c.execute('SELECT * FROM shopping_requests WHERE shopping_id = ?', (request_id,))
            request_details = c.fetchone()
            request_type = 'shopping'
        else:  # Parcel request
            c.execute('SELECT * FROM parcels WHERE parcel_id = ?', (request_id,))
            request_details = c.fetchone()
            request_type = 'parcel'
        
        # Append detailed request to the list
        if request_details:
            detailed_requests.append({
                'request': request,
                'details': request_details,
                'type': request_type
            })
            print(f"Request Details: {request_details}, Type: {request_type}")

    print(f"Requests fetched: {requests}")
    print(f"Detailed Requests: {detailed_requests}")
    conn.close()
    
    return render_template('employee_requests.html', detailed_requests=detailed_requests)


#route to accept requests
@employee.route('/accept_request', methods=['POST'])
@login_required
def accept_request():
    # Get the request ID from the form
    request_id = request.form.get('request_id')
    if not request_id:
        print("Request ID not provided")
    print(f"Request ID received: {request_id}")
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT status FROM All_requests WHERE request_id = ?', (request_id,))
    status = c.fetchone()
    print(f"Request status: {status}")
    if status and status[0] == 'Request Received':
        if request_id.startswith('SHP'):
            c.execute('UPDATE shopping_requests SET status = "Request Approved" WHERE shopping_id = ?', (request_id,))
        else:
            c.execute('UPDATE parcels SET status = "Request Approved" WHERE parcel_id = ?', (request_id,))
        
        c.execute('UPDATE All_requests SET status = "Request Approved" WHERE request_id = ?', (request_id,))

        conn.commit()
        conn.close()
        print("Request accepted successfully")
    return redirect(url_for('employee.employee_dashboard'))


#route for employee to reject requests
@employee.route('/reject_request', methods=['POST'])
@login_required
def reject_request():
    print("Rejecting request")
    # Get the request ID from the form
    request_id = request.form.get('request_id')
    if not request_id:
        print("Request ID not provided")
    print(f"Request ID received: {request_id}")
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT status FROM All_requests WHERE request_id = ?', (request_id,))
    status = c.fetchone()
    print(f"Request status: {status}")
    if status and status[0] == 'Request Received':
        if request_id.startswith('SHP'):
            c.execute('UPDATE shopping_requests SET status = "Employee cancelled" WHERE shopping_id = ?', (request_id,))
            #change assigned to to none
            c.execute('UPDATE shopping_requests SET assigned_to = NULL WHERE shopping_id = ?', (request_id,))
        else:
            c.execute('UPDATE parcels SET status = "Employee Cancelled" WHERE parcel_id = ?', (request_id,))
            #change assigned to to none
            c.execute('UPDATE parcels SET assigned_to = NULL WHERE parcel_id = ?', (request_id,))
        
        c.execute('UPDATE All_requests SET status = "Employee cancelled" WHERE request_id = ?', (request_id,))
        #set assigned to to none in all requests table
        c.execute('UPDATE All_requests SET assigned_to = NULL WHERE request_id = ?', (request_id,))
        #remove request id from employee table, set it to 0
        c.execute('UPDATE employees SET request_id = "0" WHERE request_id = ?', (request_id,))

        conn.commit()
        conn.close()
        print("Request rejected successfully")
    return redirect(url_for('employee.employee_dashboard'))

#route for employee account
@employee.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    c.execute('SELECT location FROM employees WHERE user_id = ?', (user_id,))
    location = c.fetchone()[0]
    conn.close()
    print(user)
    return render_template('my_profile.html', user=user, location=location)


#route to update employee profile
@employee.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    user_id = session['user_id']
    username = request.form['username']
    email = request.form['email']
    phone = request.form['phone']
    location = request.form['location']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    #get username before update
    c.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    old_username = c.fetchone()[0]
    print(old_username)

    #update user details
    c.execute('UPDATE users SET username = ?, email = ?, phone_number = ? WHERE id = ?', (username, email, phone, user_id))
    c.execute('UPDATE employees SET location = ? WHERE user_id = ?', (location, user_id))

    #update name on requests
    c.execute('UPDATE All_requests SET assigned_to = ? WHERE assigned_to = ?', (username, old_username))

    #update name on shopping requests
    c.execute('UPDATE shopping_requests SET assigned_to = ? WHERE assigned_to = ?', (username, old_username))

    #update name on parcels
    c.execute('UPDATE parcels SET assigned_to = ? WHERE assigned_to = ?', (username, old_username))

    conn.commit()
    conn.close()
    return redirect(url_for('employee.profile'))