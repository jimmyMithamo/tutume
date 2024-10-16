import sqlite3
from flask import redirect, url_for, session, request

#function to generate id's
def generate_id(request):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if request == 'shopping':
        c.execute('SELECT COUNT(*) FROM shopping_requests')
        count = c.fetchone()[0]
        new_id = f'SHP-{count + 1:02d}'  # Generates IDs like SHP-01, SHP-02, etc.
        
    elif request == 'parcel':
        c.execute('SELECT COUNT(*) FROM parcels')
        count = c.fetchone()[0]
        new_id = f'PRC-{count + 1:02d}'  # Generates IDs like PRC-01, PRC-02, etc.

    elif request == 'gift':
        c.execute('SELECT COUNT(*) FROM surprise_express')
        count = c.fetchone()[0]
        new_id = f'SE_GFT-{count + 1:02d}'

    elif request == 'flowers':
        c.execute('SELECT COUNT(*) FROM surprise_express')
        count = c.fetchone()[0]
        new_id = f'SE_FLW-{count + 1:02d}'

    elif request == 'care_package':
        c.execute('SELECT COUNT(*) FROM surprise_express')
        count = c.fetchone()[0]
        new_id = f'SE_CRP-{count + 1:02d}'
        
    elif request == 'gift_basket':
        c.execute('SELECT COUNT(*) FROM surprise_express')
        count = c.fetchone()[0]
        new_id = f'SE_GFT_BSKT-{count + 1:02d}'
    
    conn.close()
    return new_id


#route for getting free employees
def get_users_with_request_id_0():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Execute the SQL query
    c.execute('''
        SELECT u.username
        FROM employees e
        JOIN users u ON e.user_id = u.id
        WHERE e.request_id = '0';
    ''')
    
    # Fetch all results
    users = c.fetchall()
    
    conn.close()
    
    # Return the list of usernames
    return [user[0] for user in users]


#function to update request status
def update_request_status(request_id, request_type, url):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Fetch current status and assigned employee
    if request_type == 'parcel':
        c.execute('SELECT status, assigned_to FROM parcels WHERE parcel_id = ?', (request_id,))
    elif request_type == 'shopping':
        c.execute('SELECT status, assigned_to FROM shopping_requests WHERE shopping_id = ?', (request_id,))
    else:
        print('wrong request type')
        return

    request_data = c.fetchone()
    if request_data is None:
        conn.close()
        return "Request not found", 404

    current_status, assigned_username = request_data[0], request_data[1]

    # If the request is completed or canceled, do not allow editing
    if current_status in ['Completed', 'Cancelled']:
        print("This request cannot be edited because it is already completed.")
        session['alert'] = "This request cannot be edited because it is already completed."
        conn.close()
        return redirect(url_for(url))

    new_status = request.form.get('status')
    new_assigned_username = request.form.get('assigned_to')
    print(f"New status: {new_status}, New assigned username: {new_assigned_username}")
    print(type(new_status), type(new_assigned_username))

    if new_status == '':
        new_status = current_status
        print("New status not provided. Using the current status.")
        print(current_status)

    if new_assigned_username == '':
        new_assigned_username = assigned_username
        print("New assigned username not provided. Using the current assigned username.")
        print(assigned_username)

    # If the new status is 'Completed', free the current employee's request
    if new_assigned_username:
        # Free the current employee's request
        print(f"Assigned employee: {new_assigned_username}")

        if new_assigned_username:
            if new_status == 'Completed':
                c.execute('UPDATE employees SET request_id = "0" WHERE user_id = (SELECT id FROM users WHERE username = ?)', (new_assigned_username,))
            else:
                # Assign the new employee to the request
                user_id = c.execute('SELECT id FROM users WHERE username = ?', (new_assigned_username,)).fetchone()
                if user_id:
                    c.execute('UPDATE employees SET request_id = ? WHERE user_id = ?', (request_id, user_id[0]))
                else:
                    print("New assigned username not found.")

        
        

    # Update the request status and keep the last assigned employee in the record
    if request_type == 'shopping':
        c.execute('UPDATE shopping_requests SET status = ?, assigned_to = ? WHERE shopping_id = ?', (new_status, new_assigned_username or assigned_username, request_id))
    elif request_type == 'parcel':
        c.execute('UPDATE parcels SET status = ?, assigned_to = ? WHERE parcel_id = ?', (new_status, new_assigned_username or assigned_username, request_id))
    else:
        print('wrong request type')
        conn.close()
        return

    # Update the all requests table with the last assigned employee
    c.execute('UPDATE All_requests SET status = ?, assigned_to = ? WHERE request_id = ?', (new_status, new_assigned_username or assigned_username, request_id))

    conn.commit()
    conn.close()
    return redirect(url_for(url))


#function to update users
def update_user(user_id, status):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Update the user role to employee
    c.execute('UPDATE users SET status = ? WHERE id = ?', (status, user_id))
    conn.commit()
    conn.close()
    
    return "User has been promoted to employee successfully!"