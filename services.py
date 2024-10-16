from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
import sqlite3
from utils import generate_id
from auth import login_required




services = Blueprint('services', __name__, url_prefix='/services', template_folder='templates')


#route to show shopping page
@services.route('/shopping', methods=['POST', 'GET'])
def shopping():
    return render_template('shopping.html')

#route to submit shopping list
@services.route('/submit_shopping_request', methods=['POST'])
@login_required
def submit_shopping_request():
    phone_number = request.form['phone_number']
    home_address = request.form['home_address']
    items = request.form['items[]']  # Update to retrieve the items correctly as an array
    additional_info = request.form.get('additional_info', '')
    user_id = session['user_id']  # Get the logged-in user's ID
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Generate a unique shopping ID
    shopping_id = generate_id('shopping')
    status = 'Request Received'

    # Insert the shopping request into the database
    c.execute('''INSERT INTO shopping_requests (user_id, shopping_id, phone_number, home_address,
              items, additional_info, status) VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (user_id, shopping_id, phone_number, home_address, items, additional_info, status))

    # Insert a record into the All_requests table
    c.execute('INSERT INTO All_requests (request_id, status) VALUES (?, ?)', (shopping_id, status))
    
    conn.commit()
    conn.close()

    # Redirect to the tracking page or back to the shopping page
    return redirect(url_for('services.track_shopping_requests'))


#route to show tracking page
@services.route('/track_shopping_requests', methods=['GET'])
@login_required
def track_shopping_requests():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM shopping_requests WHERE user_id = ?', (user_id,))
    requests = c.fetchall()
    conn.close()
    print(requests)
    
    return render_template('track_requests.html', requests=requests)

#route for parcel service
@services.route('/parcel', methods=['GET'])
def parcel():
    return render_template('parcel.html')

#route to submit parcel
@services.route('/submit_parcel', methods=['POST'])
@login_required
def submit_parcel():
    recipient_name = request.form.get('recipient_name')
    recipient_address = request.form.get('recipient_address')
    recipient_phone = request.form.get('recipient_phone')
    parcel_details = request.form.get('parcel_details')
    collection_point = request.form.get('collection_point')
    additional_instructions = request.form.get('additional_instructions')

    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    parcel_id = generate_id('parcel')
    c.execute('''
        INSERT INTO parcels (parcel_id, user_id, recipient_name, recipient_address, recipient_phone, parcel_details, collection_point, additional_instructions, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (parcel_id, user_id, recipient_name, recipient_address, recipient_phone, parcel_details, collection_point, additional_instructions, 'Received'))
    c.execute('INSERT INTO All_requests (request_id, status) VALUES (?, ?)', (parcel_id, 'Request Received'))
    conn.commit()
    conn.close()
    return redirect(url_for('services.track_parcels'))

#route to track parcels
@services.route('/track_parcels', methods=['GET'])
@login_required
def track_parcels():
    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM parcels WHERE user_id = ?', (user_id,))
    parcels = c.fetchall()
    conn.close()
    return render_template('track_parcels.html', parcels=parcels)

#route to show food delivery page
@services.route('/fooddelivery', methods=['GET'])
def food_delivery():
    return render_template('fooddelivery.html')

#route to show handyman service page
@services.route('/handyman', methods=['GET'])
def handyman():
    return render_template('handyman.html')

#route to show furniture delivery page
@services.route('/furniture', methods=['GET'])
def furniture_delivery():
    return render_template('furniture.html')

#route to show booka-appoinment page
@services.route('/book_appointment', methods=['GET'])
def book_appointment():
    return render_template('book_appointment.html')

#route to handle surprise express
@services.route('/surprise_express')
@login_required
def surprise_express():
    return render_template('surprise_express.html')


#route to submit surprise express
@services.route('/submit_surprise_express//<string:request_type>', methods=['GET', 'POST'])
def submit_surprise_express(request_type):
    recipient_name = request.form.get('recipient_name')
    recipient_address = request.form.get('recipient_address')
    recipient_phone = request.form.get('recipient_phone')
    surprise_details = request.form.get('surprise_details')

    if request_type == 'gift':
        surprise_id = generate_id('gift')
    elif request_type == 'flowers':
        surprise_id = generate_id('flowers')
    elif request_type == 'care_package':
        surprise_id = generate_id('care_package')
    else:
        surprise_id = generate_id('gift_basket')

    user_id = session['user_id']
    conn = sqlite3.connect('database.db')

    #Add the request to the surprise express table
    c = conn.cursor()
    c.execute('''INSERT INTO surprise_express (user_id, surprise_id, recipient_name, recipient_address, recipient_phone, surprise_details, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)''', (user_id, surprise_id, recipient_name, recipient_address, recipient_phone, surprise_details, 'Received'))
    
    #add the request to the all requests table
    c.execute('INSERT INTO All_requests (request_id, status) VALUES (?, ?)', (surprise_id, 'Request Received'))


    conn.commit()
    conn.close()
    return 'Request submitted successfully'

