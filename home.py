from flask import Blueprint, render_template, redirect, url_for, request, flash, session
import sqlite3

home = Blueprint('home', __name__, url_prefix='/home', template_folder='templates')

#route for home page
@home.route('/', methods=['GET'])
@home.route('/home', methods=['GET'])
def home_page():
    return render_template('index.html', logged_in='user_id' in session)


#route for services page
@home.route('/services', methods=['GET'])
def services():
    return render_template('services.html')

#route for about page
@home.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

#route for contact page
@home.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')


