from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask import make_response  # create custom HTTP responses
from flask import send_file  # send files as responses
from flask_sqlalchemy import SQLAlchemy  # working with db
from flask_cors import CORS  # handle Cross-Origin Resource Sharing requests
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey  # SQLAlchemy column types
from sqlalchemy.orm import relationship  # defining relationships between models
from flasgger import Swagger

from itertools import permutations  # generate all possible orderings of a sequence
from datetime import datetime, date  # work with date and time
import pymssql  # connecting to Microsoft SQL Server
import json  # handle JSON data
import os  # interact with the operating system
import faiss  # Facebook AI Similarity Search for fast nearest neighbor retrieval
import numpy as np  # numerical operations and array handling
import bcrypt  # password hashing and security
import smtplib  # sending emails
import math
from email.mime.text import MIMEText  # formatting email messages
from fpdf import FPDF  # generating PDF files
import folium  # generating interactive maps

from selenium import webdriver  # automating web browser interactions
from selenium.webdriver.chrome.service import Service  # manage ChromeDriver service
from webdriver_manager.chrome import ChromeDriverManager  # automatic ChromeDriver management

import stripe
# ✅ Устанавливаем ключи Stripe
stripe.api_key = "sk_test_51R4ftwHy59XGfrcneVpHJ3pk6uHm0nky74BPOrAHxhJBUoujIJfXlX8yOb0EYsoBHzbI7e5feb2f1tvNhGm8eBq300D1gGaAPH"
# ✅ Указываем ID подписки
PRICE_ID = "price_1R4jA9Hy59XGfrcn0HX0vZFf"  

app = Flask(__name__)  # Create instance of Flask application
# Swagger initialization
swagger = Swagger(app)

# Enable Cross-Origin Resource Sharing (CORS), allowing requests from any origin
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


# Database connection settings
# app.config['SQLALCHEMY_DATABASE_URI'] = ('mssql+pyodbc://DESKTOP-RC369C7\\SQLEXPRESS01/WanderMap_DB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pymssql://admin:345ertERT!!!@database-1.cavoeg0u27ey.us-east-1.rds.amazonaws.com:1433/WanderMap_DB'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable SQLAlchemy modification tracking for performance improvement

# Initialize database object for interacting with db
db = SQLAlchemy(app)

# Email sending configuration
SMTP_SERVER = "smtp.gmail.com"  # SMTP server address
SMTP_PORT = 587  # SMTP port for sending emails
SMTP_EMAIL = "polinadolgopolova@gmail.com"  # My email address
sender_name = "WanderMap Support"  # Sender's display name
SMTP_PASSWORD = "pgjgsegdokfboexc"  # Application-specific password for SMTP authentication

# Categories for waypoints
waypoint_categories = [
    {"amusement_park", "water_park", "theme_park"},
    {"pet", "dog_park", "park"},
    {"pub", "amusement_park"},
    {"pub", "nightclub", "sports_centre"},
    {"spa", "park", "nature_reserve"},
    {"forest", "beach", "wood", "water", "nature_reserve"},
    {"art_gallery", "museum", "gallery", "attraction"},
    {"climbing", "surfing", "stadium", "swimming_pool", "sports_centre"},
    {"fashion", "cosmetics", "jewelry"},
    {"car", "electronics"},
    {"nightclub", "pub", "skateboard"},
    {"spa"}
]

class Traveller(db.Model):
    __tablename__ = 'Traveller'
    userName = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(255))
    name = db.Column(db.String(255))
    surname = db.Column(db.String(255))
    dateOfBirth = db.Column(db.Date)
    gender = db.Column(db.String(50))
    maritalState = db.Column(db.String(50))
    hasKids = db.Column(db.Boolean, default=False)
    hasPets = db.Column(db.Boolean, default=False)
    extrovert = db.Column(db.Boolean, default=False)
    natureLover = db.Column(db.Boolean, default=False)
    museumLover = db.Column(db.Boolean, default=False)
    sportLover = db.Column(db.Boolean, default=False)
    blocked = db.Column(db.Boolean, default=False)
    subscription = db.Column(db.Boolean, default=False)

    # Relationships with other tables
    reviews = db.relationship('Review', backref='traveller', lazy=True)
    maps = db.relationship('Map', backref='traveller', lazy=True)
    draft_map = db.relationship('DraftMap', backref='traveller', uselist=False)

class Administrator(db.Model):
    __tablename__ = 'Administrator'
    userName = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.String(255), nullable=False)

class Map(db.Model):
    __tablename__ = 'Map'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.Text)
    userName = db.Column(db.String(255), db.ForeignKey('Traveller.userName'))
    rating = db.Column(db.Float)
    reviewsNumber = db.Column(db.Integer)

    # Relationships with other tables
    waypoints = db.relationship('Waypoint', secondary='Map_Waypoint', backref='maps', lazy='subquery')
    reviews = db.relationship('Review', backref='map', lazy=True)

class DraftMap(db.Model):
    __tablename__ = 'DraftMap'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.Text)
    userName = db.Column(db.String(255), db.ForeignKey('Traveller.userName'))

    waypoints = db.relationship('Waypoint', secondary='DraftMap_Waypoint', backref='draft_maps', lazy='subquery')

class Waypoint(db.Model):
    __tablename__ = 'Waypoint'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    type = db.Column(db.String(255))

class MapWaypoint(db.Model):
    __tablename__ = 'Map_Waypoint'
    mapId = db.Column(db.Integer, db.ForeignKey('Map.id'), primary_key=True)
    waypointId = db.Column(db.Integer, db.ForeignKey('Waypoint.id'), primary_key=True)
    waypointOrder = db.Column(db.Integer)
    description = db.Column(db.Text)
    images = db.Column(db.Text)

class DraftMapWaypoint(db.Model):
    __tablename__ = 'DraftMap_Waypoint'
    draftMapId = db.Column(db.Integer, db.ForeignKey('DraftMap.id'), primary_key=True)
    waypointId = db.Column(db.Integer, db.ForeignKey('Waypoint.id'), primary_key=True)
    waypointOrder = db.Column(db.Integer)
    description = db.Column(db.Text)
    images = db.Column(db.Text)

class Review(db.Model):
    __tablename__ = 'Review'
    userName = db.Column(db.String(255), db.ForeignKey('Traveller.userName'), primary_key=True)
    mapId = db.Column(db.Integer, db.ForeignKey('Map.id'), primary_key=True)
    rating = db.Column(db.Float)
    text = db.Column(db.Text)

@app.route('/home')
def home():
    """
    Home Page
    ---
    tags:
      - Pages
    responses:
      200:
        description: Render the home page
    """
    return render_template('home.html')

@app.route('/explore_maps')
def explore_maps():
    """
    Explore Maps Page
    ---
    tags:
      - Pages
    responses:
      200:
        description: Render the explore maps page
    """
    return render_template('explore_maps.html')

@app.route('/how_to_use')
def how_to_use():
    """
    How to Use Page
    ---
    tags:
      - Pages
    responses:
      200:
        description: Render the how-to-use page
    """
    return render_template('how_to_use.html')

@app.route('/about_us')
def about_us():
    """
    About Us Page
    ---
    tags:
      - Pages
    responses:
      200:
        description: Render the about us page
    """
    return render_template('about_us.html')

@app.route('/admin_home')
def admin_home():
    """
    Admin Home Page
    ---
    tags:
      - Pages
    responses:
      200:
        description: Render the admin home page
    """
    return render_template('admin_home.html')

@app.route('/<username>')
def user_home(username):
    """
    User Home Page
    ---
    tags:
      - Pages
    parameters:
      - name: username
        in: path
        required: true
        type: string
        example: "john_doe"
    responses:
      200:
        description: Render the user's home page
    """
    return render_template('user_home.html', username=username)

@app.route('/<username>/my_maps')
def my_maps(username):
    """
    My Maps Page
    ---
    tags:
      - Pages
    parameters:
      - name: username
        in: path
        required: true
        type: string
        example: "john_doe"
    responses:
      200:
        description: Render the my maps page for the user
    """
    return render_template('my_maps.html', username=username)

@app.route('/<username>/my_profile')
def my_profile(username):
    """
    User Profile Page
    ---
    tags:
      - Pages
    parameters:
      - name: username
        in: path
        required: true
        type: string
        example: "john_doe"
    responses:
      200:
        description: Render the user profile page
      404:
        description: User not found
    """
    traveller = Traveller.query.filter_by(userName=username).first()
    if not traveller:
        return "User not found", 404

    return render_template('my_profile.html', traveller=traveller)

@app.route('/<username>/explore_maps')
def user_explore_maps(username):
    """
    Explore Maps for User
    ---
    tags:
      - Pages
    parameters:
      - name: username
        in: path
        required: true
        type: string
        example: "john_doe"
    responses:
      200:
        description: Render the explore maps page for the user
    """
    return render_template('user_explore_maps.html', username=username)

@app.route('/<username>/how_to_use')
def user_how_to_use(username):
    """
    How to Use for User
    ---
    tags:
      - Pages
    parameters:
      - name: username
        in: path
        required: true
        type: string
        example: "john_doe"
    responses:
      200:
        description: Render the how-to-use page for the user
    """
    return render_template('user_how_to_use.html', username=username)

@app.route('/<username>/about_us')
def user_about_us(username):
    """
    About Us for User
    ---
    tags:
      - Pages
    parameters:
      - name: username
        in: path
        required: true
        type: string
        example: "john_doe"
    responses:
      200:
        description: Render the about us page for the user
    """
    return render_template('user_about_us.html', username=username)

# Endpoint to check if an administrator exists
@app.route('/admin-sign-in', methods=['POST'])
def admin_sign_in():
    """
    Admin Sign-In
    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              admin_username:
                type: string
                example: "admin123"
              admin_password:
                type: string
                example: "securepassword"
    responses:
      200:
        description: Successfully authenticated
        content:
          application/json:
            schema:
              type: object
              properties:
                userExists:
                  type: boolean
                  example: true
                admin_username:
                  type: string
                  example: "admin123"
      400:
        description: Missing parameters
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()  # Get request data in JSON format
        userName = data.get('admin_username')
        password = data.get('admin_password')

        if userName and password:
            admin = Administrator.query.filter_by(userName=userName).first()
            
            # Check if the administrator exists and the password matches
            if admin and bcrypt.checkpw(password.encode("utf-8"), admin.password.encode("utf-8")):
                resp = make_response(jsonify({'userExists': True, 'admin_username': userName}))
                resp.set_cookie('username', userName)  # Store the username in a cookie
                return resp
            else:
                return jsonify({'userExists': False})
        else:
            return jsonify({'error': 'Missing parameters'}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to check if a user exists
@app.route('/user-sign-in', methods=['POST'])
def user_sign_in():
    """
    User Sign-In
    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username:
                type: string
                example: "traveller01"
              password:
                type: string
                example: "mypassword"
    responses:
      200:
        description: Successfully authenticated or blocked user
        content:
          application/json:
            schema:
              type: object
              properties:
                userExists:
                  type: boolean
                  example: true
                username:
                  type: string
                  example: "traveller01"
                userBlocked:
                  type: boolean
                  example: false
      400:
        description: Parameters not provided
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        userName = data.get('username')
        password = data.get('password')

        if not userName or not password:
            return jsonify({'error': 'Parameters not provided'}), 400

        traveller = Traveller.query.filter_by(userName=userName).first()
        
        # If user is blocked, return a blocked response
        if traveller.blocked == True:
            return jsonify({'userBlocked': True})
        
        # Check if the user exists and the password is correct
        elif traveller and bcrypt.checkpw(password.encode("utf-8"), traveller.password.encode("utf-8")):
            resp = make_response(jsonify({'userExists': True, 'username': userName}))
            resp.set_cookie('username', userName)  # Store the username in a cookie
            return resp
        else:
            return jsonify({'userExists': False})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint for user logout
@app.route('/logout')
def logout():
    """
    User Logout
    ---
    tags:
      - Authentication
    responses:
      302:
        description: Redirects to home and clears user session
    """
    resp = make_response(redirect(url_for('home')))  # Redirect to the home page
    resp.set_cookie('username', '', expires=0)  # Clear the username cookie
    return resp

# Endpoint for user registration
@app.route('/user-sign-up', methods=['POST'])
def user_sign_up():
    """
    User Sign-Up
    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username:
                type: string
                example: "new_user"
              password:
                type: string
                example: "securepassword"
    responses:
      200:
        description: User successfully registered
      400:
        description: Missing username or password
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        userName = data.get('username')
        password = data.get('password')

        if not userName:
            return jsonify({'noUsername': True})
        if not password:
            return jsonify({'noPassword': True})

        # Check if the user already exists
        if Traveller.query.filter_by(userName=userName).first():
            return jsonify({'userExists': True, 'username': userName})

        # Hash the password before storing it
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

        # Create a new user and store it in the database
        new_traveller = Traveller(userName=userName, password=hashed_password.decode("utf-8"))
        db.session.add(new_traveller)
        db.session.commit()

        resp = make_response(jsonify({'userExists': False, 'username': userName}))
        resp.set_cookie('username', userName)  # Store the username in a cookie
        return resp

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint for password recovery
@app.route('/recover-email', methods=['POST'])
def recover_email():
    """
    Password Recovery
    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username:
                type: string
                example: "user123"
    responses:
      200:
        description: Recovery email sent successfully
      400:
        description: Username is required
      404:
        description: User not found or no email associated
      500:
        description: Internal server error
    """
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({"userExists": False, "message": "Username is required"}), 400

    traveller = Traveller.query.filter_by(userName=username).first()

    if not traveller:
        return jsonify({"userExists": False, "message": "No user with such username."}), 404
    if not traveller.email:
        # Return error if user doesn't have email in their profile
        return jsonify({"hasEmail": False, "message": "No email in user's profile."})

    # Send recovery email
    if send_recover_email(traveller.email):
        return jsonify({"sentEmail": True, "message": "Recovering email sent."})
    else:
        return jsonify({"sentEmail": False, "message": "Failed to send email."})

# Function to send recovery email
def send_recover_email(to_email):
    subject = "Restoring WanderMap password"
    body = (
        f"Dear traveller,\n\n"
        f"Please, send your old and new account password in the answering email. "
        f"We will get in touch with you as soon as possible.\n\n"
        f"If you did not request this change or believe it was made in error, "
        f"please contact our support team immediately by replying to this email.\n\n"
        f"Best regards,\n"
        f"WanderMap Team"
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = f"{sender_name} <{SMTP_EMAIL}>"
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable encryption for secure communication
            server.login(SMTP_EMAIL, SMTP_PASSWORD)  # Authenticate with SMTP server
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())  # Send email
            print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")  # Log error if email sending fails
        return False

# Endpoint to update user profile
@app.route('/update-profile', methods=['POST'])
def update_profile():
    """
    Update User Profile
    ---
    tags:
      - Profile Management
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              userName:
                type: string
                example: "traveller01"
              email:
                type: string
                example: "user@example.com"
              name:
                type: string
                example: "John"
              surname:
                type: string
                example: "Doe"
              dateOfBirth:
                type: string
                format: date
                example: "1990-01-01"
              gender:
                type: string
                example: "Male"
              maritalState:
                type: string
                example: "Single"
              hasKids:
                type: boolean
                example: false
              hasPets:
                type: boolean
                example: true
              extrovert:
                type: boolean
                example: true
              natureLover:
                type: boolean
                example: false
              museumLover:
                type: boolean
                example: true
              sportLover:
                type: boolean
                example: false
    responses:
      200:
        description: Profile updated successfully
      404:
        description: User not found
      500:
        description: Internal server error
    """
    data = request.get_json()  # Extract JSON data from the request

    traveller = Traveller.query.filter_by(userName=data['userName']).first()
    if not traveller:
        return jsonify({"message": "User not found"}), 404

    old_email = traveller.email  # Store old email before updating

    # Update traveller's profile fields with new values (if provided)
    traveller.email = data.get('email', traveller.email)
    traveller.name = data.get('name', traveller.name)
    traveller.surname = data.get('surname', traveller.surname)
    traveller.dateOfBirth = data.get('dateOfBirth', traveller.dateOfBirth)
    traveller.gender = data.get('gender', traveller.gender)
    traveller.maritalState = data.get('maritalState', traveller.maritalState)
    traveller.hasKids = data.get('hasKids', traveller.hasKids)
    traveller.hasPets = data.get('hasPets', traveller.hasPets)
    traveller.extrovert = data.get('extrovert', traveller.extrovert)
    traveller.natureLover = data.get('natureLover', traveller.natureLover)
    traveller.museumLover = data.get('museumLover', traveller.museumLover)
    traveller.sportLover = data.get('sportLover', traveller.sportLover)

    db.session.commit()  # Save changes to db

    # Send notification email if email address has changed
    if old_email != data.get('email'):
        send_email(old_email, data.get('email'))

    # Update index of all travellers for similarity search
    update_travelers_index()

    return jsonify({"message": "Profile updated successfully"})

# Function to send email notification about email update
def send_email(to_email, new_email):
    subject = "Your Email has been Updated"
    body = (
        f"Dear traveller,\n\n"
        f"We would like to inform you that the email address associated with your WanderMap account "
        f"has been successfully updated to: {new_email}.\n\n"
        f"If you did not request this change or believe it was made in error, please contact our support team immediately "
        f"by replying to this email.\n\n"
        f"Best regards,\n"
        f"WanderMap Team"
    )
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = f"{sender_name} <{SMTP_EMAIL}>"
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable encryption
            server.login(SMTP_EMAIL, SMTP_PASSWORD)  # Authenticate with SMTP server
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())  # Send email
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")  # Log any errors if email sending fails

# Function to update FAISS index for all travellers
def update_travelers_index():
    travellers = Traveller.query.all()  # Fetch all travellers from db
    
    # Convert traveller data into numerical vectors for indexing
    travellers_data = np.array([get_traveller_vector(t) for t in travellers], dtype='float32')
    
    travellers_index = faiss.IndexFlatL2(12)  # Create FAISS index with vector dimension of 12
    
    if travellers_data.size > 0:
        travellers_index.add(travellers_data)  # Add traveller data to FAISS index
    
    # Save updated FAISS index to file
    faiss.write_index(travellers_index, "faiss_index/travellers_index.faiss")
    print("FAISS index updated for all travellers!")

# Endpoint to get or create a draft map
@app.route('/draftmap', methods=['POST'])
def get_or_create_draftmap():
    """
    Retrieve an existing draft map for a user or create a new one if none exists.
    ---
    tags:
      - Draft Maps
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username:
                type: string
                description: Username of the user
    responses:
      200:
        description: Draft map retrieved successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                username:
                  type: string
                waypoints:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
                      latitude:
                        type: number
                      longitude:
                        type: number
      400:
        description: Missing username
    """
    data = request.get_json()

    username = data.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    # Check if a draft map already exists
    draft_map = DraftMap.query.filter_by(userName=username).first()

    if draft_map:
        waypoints = [
            {
                'id': mw.id,
                'name': mw.name,
                'latitude': mw.latitude,
                'longitude': mw.longitude
            } for mw in draft_map.waypoints
        ]
        return jsonify({
            'id': draft_map.id,
            'username': draft_map.userName,
            'waypoints': waypoints
        })

    # Create a new draft map
    new_draft_map = DraftMap(userName=username)
    db.session.add(new_draft_map)
    db.session.commit()

    return jsonify({
        'id': new_draft_map.id,
        'username': new_draft_map.userName,
        'waypoints': []
    })

# Endpoint to add a waypoint to a draft map
@app.route('/add-waypoint', methods=['POST'])
def add_waypoint():
    """
    Adds a new waypoint to an existing draft map.
    ---
    tags:
      - Waypoints
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username:
                type: string
              name:
                type: string
              latitude:
                type: number
              longitude:
                type: number
    responses:
      200:
        description: Waypoint successfully added or already exists
        content:
          application/json:
            schema:
              type: object
              properties:
                newWaypoint:
                  type: boolean
                message:
                  type: string
      400:
        description: Missing required fields
      404:
        description: Draft map not found
    """
    data = request.get_json()
    username = data.get('username')
    name = data.get('name')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not all([username, name, latitude, longitude]):
        return jsonify({'error': 'All fields are required'}), 400

    # Check if the draft map exists
    draft_map = DraftMap.query.filter_by(userName=username).first()
    if not draft_map:
        return jsonify({'error': 'DraftMap not found'}), 404

    # Check if the waypoint already exists
    waypoint = Waypoint.query.filter_by(latitude=latitude, longitude=longitude).first()

    if waypoint:
        # If waypoint exists, check if it is already linked to draft map
        draft_map_waypoint = DraftMapWaypoint.query.filter_by(
            draftMapId=draft_map.id, waypointId=waypoint.id
        ).first()
        if draft_map_waypoint:
            return jsonify({'newWaypoint': False, 'message': 'Waypoint already added'})

        # Determine the order for the waypoint
        max_order = (
            db.session.query(db.func.max(DraftMapWaypoint.waypointOrder))
            .filter(DraftMapWaypoint.draftMapId == draft_map.id)
            .scalar()
        )
        new_order = (max_order or 0) + 1

         # Create link between draft map and waypoint
        new_draft_map_waypoint = DraftMapWaypoint(
            draftMapId=draft_map.id,
            waypointId=waypoint.id,
            waypointOrder=new_order
        )
        db.session.add(new_draft_map_waypoint)
        db.session.commit()
        return jsonify({'newWaypoint': False})

    # Create new waypoint
    new_waypoint = Waypoint(name=name, latitude=latitude, longitude=longitude)
    db.session.add(new_waypoint)
    db.session.commit()

    # Determine order for new waypoint
    max_order = (
        db.session.query(db.func.max(DraftMapWaypoint.waypointOrder))
        .filter(DraftMapWaypoint.draftMapId == draft_map.id)
        .scalar()
    )
    new_order = (max_order or 0) + 1

    # Link new waypoint to draft map
    new_draft_map_waypoint = DraftMapWaypoint(
        draftMapId=draft_map.id,
        waypointId=new_waypoint.id,
        waypointOrder=new_order
    )
    db.session.add(new_draft_map_waypoint)
    db.session.commit()

    # Update index for all waypoints
    update_waypoints_index()

    return jsonify({'newWaypoint': True})

# Function to update index for all waypoints
def update_waypoints_index():
    waypoints = Waypoint.query.all()

    # Convert each waypoint into numerical vector representation
    waypoints_data = np.array([get_waypoint_vector(w, waypoint_categories) for w in waypoints], dtype='float32')

    # Create FAISS index with L2 (Euclidean distance) metric
    # Number 12 represents expected dimension of each waypoint vector
    waypoints_index = faiss.IndexFlatL2(12)

    # Add waypoint vectors to index only if there're any data points
    if waypoints_data.size > 0:
        waypoints_index.add(waypoints_data)

    # Save updated FAISS index to file
    faiss.write_index(waypoints_index, "faiss_index/waypoints_index.faiss")

    print("FAISS index updated for all waypoints!")

# Endpoint to delete waypoints from draft map
@app.route('/delete-waypoints', methods=['POST'])
def delete_draft_map():
    """
    Deletes all waypoints from the user's draft map.
    ---
    tags:
      - Waypoints
    parameters:
      - name: username
        in: body
        type: string
        required: true
        description: Username of the traveller.
    responses:
      200:
        description: Successfully deleted the draft map.
      400:
        description: Username is missing.
      404:
        description: User or draft map not found.
      500:
        description: Internal server error.
    """
    try:
        data = request.get_json()
        username = data.get('username')  # Retrieve username from request data

        if not username:
            return jsonify({'error': 'Username is required'}), 400  # Return error if username is missing

        # Find the user (Traveller) by username
        traveller = Traveller.query.filter_by(userName=username).first()
        if not traveller:
            return jsonify({'error': 'User not found'}), 404  # Return error if user does not exist

        # Get the user's draft map
        draft_map = traveller.draft_map
        if not draft_map:
            return jsonify({'error': 'Draft map not found'}), 404  # Return error if no draft map exists

        # Remove all associated waypoints before deleting the draft map
        draft_map.waypoints.clear()

        # Delete the draft map itself
        db.session.delete(draft_map)
        db.session.commit()  # Commit the changes to the database

        return jsonify({'success': True})  # Return success response

    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Handle unexpected errors

# Convert traveller attributes into numerical vector representation.
# Each attribute is transformed into integer value for use in ML models or similarity calculations.
def get_traveller_vector(traveller):
    age = (date.today().year - traveller.dateOfBirth.year) if traveller.dateOfBirth else 0  # Calculate age
    
    return np.array([
        int(traveller.hasKids),  # 1 if traveller has kids, otherwise 0
        int(traveller.hasPets),
        int(traveller.extrovert),
        int(traveller.maritalState == 'Single'),
        int(traveller.maritalState == 'Married'),
        int(traveller.natureLover),
        int(traveller.museumLover),
        int(traveller.sportLover),
        int(traveller.gender == 'Female'),
        int(traveller.gender == 'Male'),
        int(age < 30),
        int(age > 50)
    ], dtype='float')

# Convert waypoint type into numerical vector based on predefined categories.
# Each category receives binary value indicating whether waypoint type belongs to this category.
def get_waypoint_vector(waypoint, categories):
    if waypoint.type:  # Ensure waypoint type is not None
        return np.array([
            int(any(wp_type in category for wp_type in waypoint.type.split(','))) 
            for category in categories
        ], dtype='float')
    else:
        return np.zeros(len(categories), dtype='float')  # Return zero vector if waypoint type is missing

# Recursively convert numpy objects into standard Python data types.
def convert_numpy(obj):
    if isinstance(obj, np.float32) or isinstance(obj, np.float64):
        return float(obj)  # Convert numpy float to standard Python float
    elif isinstance(obj, np.int32) or isinstance(obj, np.int64):
        return int(obj)  # Convert numpy int to standard Python int
    elif isinstance(obj, dict):
        return {key: convert_numpy(value) for key, value in obj.items()}  # Process dictionaries recursively
    elif isinstance(obj, list):
        return [convert_numpy(value) for value in obj]  # Process lists recursively
    return obj  # Return object as-is if no conversion needed

# Endpoint for retrieving travel recommendations based on user profile and draft map
@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    """
    Retrieves travel recommendations based on user profile and draft map.
    ---
    tags:
      - Waypoints
    parameters:
      - name: username
        in: query
        type: string
        required: true
        description: Username of the traveller.
    responses:
      200:
        description: List of recommended waypoints.
      400:
        description: Username is missing.
      500:
        description: Internal server error.
    """
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    # Check if draft map exists for user
    draft_map = DraftMap.query.filter_by(userName=username).first()
    if not draft_map:
        return jsonify({'hasWaypoints': False}), 200  # No draft map found

    db.session.expire_all()  # Refresh database session to ensure up-to-date data
    draft_map_waypoints = DraftMapWaypoint.query.filter_by(draftMapId=draft_map.id).all()
    if not draft_map_waypoints:
        return jsonify({'hasWaypoints': False}), 200  # Draft map exists but has no waypoints

    # Extract waypoint IDs from draft map
    draft_waypoint_ids = {dmw.waypointId for dmw in draft_map_waypoints}
    draft_waypoints = [Waypoint.query.get(wp_id) for wp_id in draft_waypoint_ids]

    # Load FAISS indexes for travellers and waypoints similarity search
    travellers_index = faiss.read_index("faiss_index/travellers_index.faiss")
    waypoints_index = faiss.read_index("faiss_index/waypoints_index.faiss")

    # Retrieve traveller's profile from database
    traveller = Traveller.query.filter_by(userName=username).first()

    # Initialize traveller and waypoint vectors as None
    traveller_vector, draftmap_waypoints_vector = None, None

    # Compute draft map waypoints vector if waypoints exist
    if draft_waypoints:
        draftmap_waypoints_vector = np.mean(
            [get_waypoint_vector(wp, waypoint_categories) for wp in draft_waypoints], axis=0
        ).reshape(1, -1)  # Convert to 2D array for FAISS compatibility

    if traveller and any([
        traveller.dateOfBirth, traveller.gender, traveller.maritalState, traveller.hasKids,
        traveller.hasPets, traveller.extrovert, traveller.natureLover, traveller.museumLover, traveller.sportLover
    ]):
        # Compute traveller vector only if relevant attributes exist
        traveller_vector = get_traveller_vector(traveller).reshape(1, -1)

    if traveller_vector.shape[1] != waypoints_index.d:
        return jsonify({'error': 'Feature size mismatch'}), 500  # Ensure correct vector dimensions

    print(draftmap_waypoints_vector)  # Debugging: print draft map vector
    print(traveller_vector)  # Debugging: print traveller vector

    # Search for closest waypoints
    results = []

    if traveller_vector is None:
        return jsonify({'error': 'Traveller vector is None'}), 500  # Traveller vector missing

    if traveller_vector is not None:
        # Search for similar travellers
        _, traveller_indices = travellers_index.search(traveller_vector, 30)
        traveller_indices = [int(idx) for idx in traveller_indices[0]]  # Convert FAISS results to list of indices

        # Retrieve waypoints visited by similar travellers
        traveller_waypoint_ids = {
            Traveller.query.get(idx).waypointId
            for idx in traveller_indices if idx != -1 and Traveller.query.get(idx) is not None
        }

        # Поиск по похожим пользователям
        _, waypoint_indices_t = waypoints_index.search(traveller_vector, 30)
        results += [(idx, 0.5) for idx in waypoint_indices_t[0] if idx != -1]  # Вес 0.5

    if draftmap_waypoints_vector is not None:
        # Поиск похожих точек по черновым
        _, waypoint_indices_d = waypoints_index.search(draftmap_waypoints_vector, 30)
        results += [(idx, 0.5) for idx in waypoint_indices_d[0] if idx != -1]  # Вес 0.5

    # Объединение и сортировка результатов
    waypoint_scores = {}
    for idx, weight in results:
        if idx in waypoint_scores:
            waypoint_scores[idx] += weight
        else:
            waypoint_scores[idx] = weight

    print(waypoint_scores)
    # Сортируем все точки по убыванию веса и берем все результаты
    sorted_waypoints = sorted(waypoint_scores.items(), key=lambda x: -x[1])

    # Формируем рекомендации
    recommended = []
    for wp_index, score in sorted_waypoints:
        waypoint = Waypoint.query.get(int(wp_index))
        # Проверяем, если точка не находится в черновой карте, добавляем ее
        if waypoint and waypoint.id not in draft_waypoint_ids:
            
            # Найти ближайшую точку из черновой карты
            nearest_draft_wp = min(
                draft_waypoints, 
                key=lambda dwp: haversine_distance(dwp, waypoint),
                default=None
            )
            draft_wp_name = nearest_draft_wp.name if nearest_draft_wp else None
            wp_distance = haversine_distance(nearest_draft_wp, waypoint) if nearest_draft_wp else None

            recommended.append({
                'id': waypoint.id,
                'name': waypoint.name,
                'latitude': waypoint.latitude,
                'longitude': waypoint.longitude,
                'score': round(score, 2),
                'distance': round(wp_distance, 2) if wp_distance is not None else None,
                'draftWaypointName': draft_wp_name
            })

    # Ограничиваем список до 5 точек
    recommended = recommended[:5]

    return jsonify({'hasWaypoints': True, 'recommendedWaypoints': recommended})

# Endpoint for adding user-selected waypoints to their draft map
@app.route('/add-chosen-waypoints', methods=['POST'])
def add_chosen_waypoints():
    """
    Adds user-selected waypoints to their draft map.
    ---
    tags:
      - Waypoints
    parameters:
      - name: username
        in: body
        type: string
        required: true
        description: Username of the traveller.
      - name: waypoints
        in: body
        type: array
        items:
          type: integer
        required: true
        description: List of waypoint IDs to add.
    responses:
      200:
        description: Waypoints successfully added.
      404:
        description: Draft map not found or no valid waypoints found.
      500:
        description: Internal server error.
    """
    # Retrieve data from request payload
    data = request.get_json()
    username = data.get('username')
    selected_waypoints = data.get('waypoints', [])

    # Find the user's draft map by username
    draft_map = DraftMap.query.filter_by(userName=username).first()
    if not draft_map:
        return jsonify({'error': 'Draft map not found for the user'}), 404  # Return error if draft map does not exist

    # Retrieve waypoints by their IDs
    waypoints = Waypoint.query.filter(Waypoint.id.in_(selected_waypoints)).all()
    if not waypoints:
        return jsonify({'error': 'No valid waypoints found'}), 404  # Return error if no valid waypoints were found

    # Add waypoints to the draft map, avoiding duplicates
    for wp in waypoints:
        existing = DraftMapWaypoint.query.filter_by(draftMapId=draft_map.id, waypointId=wp.id).first()
        if not existing:
            new_draft_map_wp = DraftMapWaypoint(draftMapId=draft_map.id, waypointId=wp.id)
            db.session.add(new_draft_map_wp)

    db.session.commit()  # Commit changes to database

    return jsonify({'message': 'Waypoints successfully added to your map.'}), 200

# Convert waypoint object to dictionary format for response
def waypoint_to_dict(wp, recommended_order=None):
    return {
        'id': wp.id,
        'name': wp.name,
        'latitude': wp.latitude,
        'longitude': wp.longitude,
        'waypointRecommendedOrder': recommended_order  # Optional recommended order for waypoints
    }

# Calculate great-circle distance between two waypoints using latitude and longitude
def haversine_distance(wp1, wp2):
    R = 6371  # Earth's radius in kilometers
    lat1, lon1 = math.radians(wp1.latitude), math.radians(wp1.longitude)
    lat2, lon2 = math.radians(wp2.latitude), math.radians(wp2.longitude)
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Apply the Haversine formula for distance calculation
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Return distance in kilometers

# Find shortest route between all waypoints using brute-force approach (not optimal for large datasets)
def find_shortest_route(waypoints):
    all_permutations = permutations(waypoints)
    
    shortest_route = None
    shortest_distance = float('inf')  # Initialize with very large value
    
    for route in all_permutations:
        total_distance = 0
        for i in range(len(route) - 1):
            total_distance += haversine_distance(route[i], route[i + 1])  # Sum distances for each route
        
        # Update shortest route if the current one is shorter
        if total_distance < shortest_distance:
            shortest_distance = total_distance
            shortest_route = route
    
    return shortest_route  # Return the optimal route found

@app.route('/waypoints', methods=['GET'])
def get_waypoints():
    """
    Retrieves the list of waypoints for a user's draft map.
    ---
    tags:
      - Waypoints
    summary: Get waypoints
    description: Fetches the waypoints associated with a user's draft map, ordered by the shortest route.
    parameters:
      - name: username
        in: query
        required: true
        schema:
          type: string
    responses:
      200:
        description: List of waypoints with optimized order
        schema:
          type: object
          properties:
            waypoints:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  order:
                    type: integer
                  description:
                    type: string
                  images:
                    type: array
                    items:
                      type: string
      404:
        description: No draft map found
    """
    username = request.args.get('username')

    # Retrieve draft map for the user
    draft_map = DraftMap.query.filter_by(userName=username).first()
    if not draft_map:
        return jsonify({'waypoints': []}), 200  # If no map exists, return an empty array
    
    # Fetch all waypoints associated with the draft map
    draft_map_waypoints = DraftMapWaypoint.query.filter_by(draftMapId=draft_map.id).all()
    if not draft_map_waypoints:
        return jsonify({'waypoints': []}), 200  # No waypoints? Return an empty list
    
    # Extract waypoints by ID
    waypoints = [Waypoint.query.get(dwp.waypointId) for dwp in draft_map_waypoints]
    
    if len(waypoints) < 2:
        return jsonify({'waypoints': []}), 200  # If less than two waypoints, return an empty array
    
    # Finding the shortest route is crucial for optimization
    shortest_route = find_shortest_route(waypoints)
    
    # Assign order to waypoints based on optimized route
    waypoints_with_order = []
    for idx, wp in enumerate(shortest_route):
        wp_dict = waypoint_to_dict(wp, recommended_order=idx + 1)  # Order starts from 1
        waypoints_with_order.append(wp_dict)
    
    return jsonify({'waypoints': waypoints_with_order}), 200  # Returning structured waypoint list

@app.route('/set-waypoints-order', methods=['POST'])
def set_waypoints_order():
    """
    Updates the order of waypoints in the user's draft map.
    ---
    tags:
      - Waypoints
    summary: Set waypoints order
    description: Allows users to manually set the order of waypoints in their draft map.
    parameters:
      - name: username
        in: body
        required: true
        schema:
          type: string
      - name: waypoints
        in: body
        required: true
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              setWaypointOrder:
                type: integer
    responses:
      200:
        description: Waypoints order updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: Draft map not found
    """
    data = request.get_json()
    username = data.get('username')
    waypoints = data.get('waypoints')

    # Retrieve the user's draft map (assuming it exists)
    draft_map = DraftMap.query.filter_by(userName=username).first()

    if not draft_map:
        return jsonify({'hasWaypoints': False}), 200  # Map not found? Indicate no waypoints exist

    # Update waypoint order, assuming input is correct
    for waypoint_data in waypoints:
        draft_map_waypoint = DraftMapWaypoint.query.filter_by(
            draftMapId=draft_map.id, waypointId=waypoint_data["id"]
        ).first()
        if draft_map_waypoint:
            draft_map_waypoint.waypointOrder = waypoint_data["setWaypointOrder"]

    db.session.commit()  # Persist changes

    return jsonify({"message": "Waypoints order updated successfully"}), 200  # Confirm update

@app.route("/get-draft-map", methods=["GET"])
def get_draft_map():
    """
    Retrieves the details of a user's draft map, including its waypoints.
    ---
    tags:
      - Draft Maps
    summary: Get draft map
    description: Fetches the draft map of a user along with all associated waypoints.
    parameters:
      - name: username
        in: query
        required: true
        schema:
          type: string
    responses:
      200:
        description: Draft map details
        schema:
          type: object
          properties:
            description:
              type: string
            waypoints:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  order:
                    type: integer
                  description:
                    type: string
                  images:
                    type: array
                    items:
                      type: string
      404:
        description: No draft map found
    """
    username = request.args.get('username')
    draft_map = DraftMap.query.filter(DraftMap.userName == username).first()
    if not draft_map:
        return jsonify({"message": "No draft map found"}), 404  # A missing map triggers a 404

    # Gather all waypoints associated with this draft map
    waypoints = DraftMapWaypoint.query.filter_by(draftMapId=draft_map.id).all()
    return jsonify({
        "description": draft_map.description,
        "waypoints": [
            {
                "id": wp.waypointId,
                "name": Waypoint.query.get(wp.waypointId).name if Waypoint.query.get(wp.waypointId) else wp.waypointId,
                "order": wp.waypointOrder,
                "description": wp.description,  # Each waypoint has a description
                "images": wp.images.split(",") if wp.images else []  # Store images as a list
            } for wp in waypoints
        ]
    })

@app.route("/save-draft-waypoint", methods=["POST"])
def save_waypoint():
    """
    Updates a waypoint's description in a draft map.
    ---
    tags:
      - Draft Waypoints
    summary: Update draft waypoint
    description: Updates the description of a waypoint in a user's draft map.
    parameters:
      - name: username
        in: body
        required: true
        schema:
          type: string
      - name: waypointId
        in: body
        required: true
        schema:
          type: integer
      - name: mapDescription
        in: body
        required: false
        schema:
          type: string
      - name: waypointDescription
        in: body
        required: false
        schema:
          type: string
    responses:
      200:
        description: Waypoint updated successfully
      404:
        description: Draft map or waypoint not found
    """
    data = request.json
    username = data.get("username")
    waypoint_id = data.get("waypointId")
    map_description = data.get("mapDescription")
    waypoint_description = data.get("waypointDescription")

    draft_map = DraftMap.query.filter_by(userName=username).first()
    if not draft_map:
        return jsonify({"message": "Draft map not found"}), 404  # Error if the draft map is missing

    waypoint = DraftMapWaypoint.query.filter_by(waypointId=waypoint_id).first()
    if not waypoint:
        return jsonify({"message": "Waypoint not found"}), 404  # Error if the waypoint is missing

    # Updating descriptions (map and waypoint)
    draft_map.description = map_description
    waypoint.description = waypoint_description

    db.session.commit()  # Save changes
    return jsonify({"message": "Waypoint updated successfully"})  # Confirm update

@app.route("/upload-draft-waypoint-image", methods=["POST"])
def upload_waypoint_image():
    """
    Uploads images to a draft waypoint.
    ---
    tags:
      - Draft Waypoints
    summary: Upload waypoint images
    description: Uploads one or more images to a draft waypoint.
    parameters:
      - name: username
        in: formData
        required: true
        schema:
          type: string
      - name: waypointId
        in: formData
        required: true
        schema:
          type: integer
      - name: images
        in: formData
        required: true
        type: file
    responses:
      200:
        description: Images uploaded successfully
      404:
        description: Waypoint not found
    """
    username = request.form.get("username")
    waypoint_id = request.form.get("waypointId")
    
    waypoint = DraftMapWaypoint.query.filter_by(waypointId=waypoint_id).first()
    if not waypoint:
        return jsonify({"error": "Waypoint not found"}), 404  # Waypoint must exist

    images = waypoint.images.split(",") if waypoint.images else []

    # Looping through uploaded images
    for image in request.files.getlist("images"):
        filename = image.filename  # Extract filename
        image.save(os.path.join("static/images/waypoints", filename))  # Save to disk
        images.append(filename)  # Append to list

    waypoint.images = ",".join(images)  # Store images as a comma-separated string
    db.session.commit()  # Persist changes

    return jsonify({"success": True, "images": images})  # Return the updated image list

# Endpoint for removing an image from a draft waypoint
@app.route("/remove-draft-waypoint-image", methods=["POST"])
def remove_waypoint_image():
    """
    Removes an image from a draft waypoint.
    ---
    tags:
      - Draft Waypoints
    summary: Remove waypoint image
    description: Removes a specified image from a draft waypoint.
    parameters:
      - name: username
        in: body
        required: true
        schema:
          type: string
      - name: waypointId
        in: body
        required: true
        schema:
          type: integer
      - name: imageName
        in: body
        required: true
        schema:
          type: string
    responses:
      200:
        description: Image removed successfully
      404:
        description: Waypoint or image not found
    """
    data = request.json
    username = data.get("username")
    waypoint_id = data.get("waypointId")
    image_name = data.get("imageName")

    waypoint = DraftMapWaypoint.query.filter_by(waypointId=waypoint_id).first()
    if not waypoint:
        return jsonify({"error": "Waypoint not found"}), 404

    # Convert images field from a string to a list
    images = waypoint.images.split(",") if waypoint.images else []
    
    if image_name not in images:
        return jsonify({"error": "Image not found in waypoint"}), 404

    # Remove only the specified image from the waypoint
    images.remove(image_name)
    waypoint.images = ",".join(images)
    db.session.commit()

    # Check if the image is used in any other waypoints (both DraftMapWaypoint and MapWaypoint)
    other_draft_waypoints = DraftMapWaypoint.query.filter(DraftMapWaypoint.images.like(f"%{image_name}%")).all()
    other_map_waypoints = MapWaypoint.query.filter(MapWaypoint.images.like(f"%{image_name}%")).all()

    # Delete the file only if no other waypoints reference it
    if not other_draft_waypoints and not other_map_waypoints:
        img_path = os.path.join("static/images/waypoints", image_name)
        if os.path.isfile(img_path):
            os.remove(img_path)

    return jsonify({"success": True, "images": images})

# Endpoint for saving a user's draft map as a permanent map
@app.route('/map', methods=['POST'])
def save_map():
    """
    Saves a draft map as a permanent map.
    ---
    tags:
      - Manage Maps
    summary: Save draft as map
    description: Converts a user's draft map into a permanent map with all associated waypoints.
    parameters:
      - name: username
        in: body
        required: true
        schema:
          type: string
    responses:
      200:
        description: Map saved successfully
      404:
        description: No draft map or waypoints found
    """
    data = request.json  
    username = data.get('username')

    # Check if the user has a draft map
    draft_map = DraftMap.query.filter_by(userName=username).first()
    if not draft_map:
        return jsonify({'hasWaypoints': False}), 200

    # Check if the draft map has any waypoints
    waypoints = DraftMapWaypoint.query.filter_by(draftMapId=draft_map.id).all()
    if not waypoints:
        return jsonify({'hasWaypoints': False}), 200

    # Get the highest existing map ID and increment it for the new map
    max_map_id = db.session.query(db.func.max(Map.id)).scalar() or 0
    new_map_id = max_map_id + 1

    # Create a new map entry in the database
    new_map = Map(
        id=new_map_id,
        description=draft_map.description,
        userName=draft_map.userName,
    )
    db.session.add(new_map)

    # Copy waypoints from the draft map to the new map
    for waypoint in waypoints:
        map_waypoint = MapWaypoint(
            mapId=new_map_id,
            waypointId=waypoint.waypointId,
            waypointOrder=waypoint.waypointOrder,
            description=waypoint.description,
            images=waypoint.images
        )
        db.session.add(map_waypoint)

    # Delete the draft map and its waypoints after saving the new map
    db.session.delete(draft_map)
    for waypoint in waypoints:
        db.session.delete(waypoint)

    db.session.commit()

    return jsonify({'hasWaypoints': True}), 200

# Endpoint for retrieving all maps of a specific user
@app.route('/maps', methods=['GET'])
def get_maps():
    """
    Retrieves all maps associated with a specific user.
    ---
    tags:
      - Manage Maps
    summary: Get user-specific maps
    description: Returns all maps that belong to a given user, along with their waypoints and associated images.
    parameters:
      - name: username
        in: query
        required: true
        schema:
          type: string
    responses:
      200:
        description: List of maps with details
        schema:
          type: object
          properties:
            maps:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  description:
                    type: string
                  rating:
                    type: number
                  waypoints:
                    type: array
                    items:
                      type: object
                      properties:
                        images:
                          type: array
                          items:
                            type: string
            subscription:
              type: boolean
              description: User's subscription status
      400:
        description: Missing username parameter
    """
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Missing username"}), 400

    # Query the database for the user's maps
    maps = Map.query.filter_by(userName=username).all()

    # Get the user's subscription status
    traveller = Traveller.query.filter_by(userName=username).first()
    subscription = traveller.subscription if traveller else False  # Если юзер не найден, считаем, что подписки нет

    map_list = []
    for map in maps:
        # Retrieve waypoints associated with the map
        waypoints = MapWaypoint.query.filter_by(mapId=map.id).all()
        
        waypoints_data = []
        for waypoint in waypoints:
            # Convert the stored comma-separated image string into a list
            images = waypoint.images.split(",") if waypoint.images else []
            waypoints_data.append({'images': images})

        map_list.append({
            'id': map.id,
            'description': map.description,
            'rating': map.rating,
            'waypoints': waypoints_data
        })

    return jsonify({'maps': map_list, 'subscription': subscription})

# Endpoint for retrieving all maps (not just those of a specific user)
@app.route('/all-maps', methods=['GET'])
def get_all_maps():
    """
    Retrieves all maps available in the database.
    ---
    tags:
      - Manage Maps
    summary: Get all maps
    description: Returns all maps in the database, including waypoints and their associated images.
    parameters:
      - name: username
        in: query
        required: true
        schema:
          type: string
    responses:
      200:
        description: List of all maps with details
        schema:
          type: object
          properties:
            maps:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  description:
                    type: string
                  rating:
                    type: number
                  reviewsNumber:
                    type: integer
                  waypoints:
                    type: array
                    items:
                      type: object
                      properties:
                        images:
                          type: array
                          items:
                            type: string
      400:
        description: Missing username parameter
    """
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Missing username"}), 400
    
    traveller = Traveller.query.filter_by(userName=username).first()
    subscription = traveller.subscription if traveller else False  # Подписка юзера

    # Получаем все карты
    maps = Map.query.all()

    # Если подписки нет, ограничиваем количество карт до 3
    if not subscription:
        maps = maps[:3]

    map_list = []
    for map in maps:
        waypoints = MapWaypoint.query.filter_by(mapId=map.id).all()
        
        waypoints_data = [
            {'images': wp.images.split(",") if wp.images else []}
            for wp in waypoints
        ]

        map_list.append({
            'id': map.id,
            'description': map.description,
            'rating': map.rating,
            'reviewsNumber': map.reviewsNumber,
            'waypoints': waypoints_data
        })

    return jsonify({
        'maps': map_list,
        'subscription': subscription
    })

# Endpoint for retrieving map details and waypoints
@app.route("/get-map", methods=["GET"])
def get_map():
    """
    Retrieves details of a specific map, including waypoints.
    ---
    tags:
      - Manage Maps
    summary: Get details of a specific map
    description: Returns details of a map, including its description, waypoints, and user-specific rating if available.
    parameters:
      - name: mapId
        in: query
        required: true
        schema:
          type: integer
      - name: username
        in: query
        required: false
        schema:
          type: string
    responses:
    200:
        description: Map details including waypoints and user rating
        content:
        application/json:
            schema:
            type: object
            properties:
                description:
                type: string
                waypoints:
                type: array
                items:
                    type: object
                    properties:
                    id:
                        type: integer
                    name:
                        type: string
                    order:
                        type: integer
                    description:
                        type: string
                    latitude:
                        type: number
                        format: float
                    longitude:
                        type: number
                        format: float
                    images:
                        type: array
                        items:
                        type: string
                rating:
                type: number
                nullable: true
                subscription:
                type: boolean
    404:
        description: Map not found
    """
    map_id = request.args.get('mapId')
    map_id = int(map_id)  # Ensure map_id is an integer

    username = request.args.get('username')  # Get username from request

    # Get the user's subscription status
    traveller = Traveller.query.filter_by(userName=username).first()
    subscription = traveller.subscription if traveller else False  # Если юзер не найден, считаем, что подписки нет

    # Retrieve the user's rating for this map if it exists
    review = Review.query.filter_by(mapId=map_id, userName=username).first()
    rating = review.rating if review else None

    user_map = Map.query.filter_by(id=map_id).first()
    if not user_map:
        return jsonify({"message": "Map not found"}), 404

    # Fetch all waypoints associated with the map
    waypoints = MapWaypoint.query.filter_by(mapId=user_map.id).all()
    return jsonify({
        "description": user_map.description,
        "waypoints": [
            {
                "id": wp.waypointId,
                # Fetch waypoint details; ensure they exist before accessing attributes
                "name": Waypoint.query.get(wp.waypointId).name if Waypoint.query.get(wp.waypointId) else wp.waypointId,
                "order": wp.waypointOrder,
                "description": wp.description,
                "latitude": Waypoint.query.get(wp.waypointId).latitude if Waypoint.query.get(wp.waypointId) else None,
                "longitude": Waypoint.query.get(wp.waypointId).longitude if Waypoint.query.get(wp.waypointId) else None,
                # Convert images string into a list
                "images": wp.images.split(",") if wp.images else []
            } for wp in waypoints
        ],
        "rating": rating,
        "subscription": subscription
    })

# Endpoint for retrieving a specific waypoint
@app.route("/get-waypoint", methods=["GET"])
def get_waypoint():
    """
    Retrieves details of a specific waypoint in a map.
    ---
    tags:
      - Waypoints
    summary: Get details of a specific waypoint
    description: Returns details of a waypoint, including its name, description, and images.
    parameters:
      - name: waypointId
        in: query
        required: true
        schema:
          type: integer
      - name: mapId
        in: query
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Waypoint details
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            description:
              type: string
            images:
              type: array
              items:
                type: string
      400:
        description: Waypoint ID and Map ID are required
      404:
        description: Waypoint not found in the specified map
    """
    waypoint_id = request.args.get('waypointId')
    map_id = request.args.get('mapId')  # Needed to fetch map-specific details

    if not waypoint_id or not map_id:
        return jsonify({"message": "Waypoint ID and Map ID are required"}), 400

    # Ensure the waypoint exists for the given map
    map_waypoint = MapWaypoint.query.filter_by(waypointId=waypoint_id, mapId=map_id).first()
    if not map_waypoint:
        return jsonify({"message": "Waypoint not found in this map"}), 404

    # Retrieve additional waypoint details
    waypoint = Waypoint.query.get(waypoint_id)

    return jsonify({
        "id": waypoint.id,
        "name": waypoint.name,
        "description": map_waypoint.description,  # Use map-specific description
        "images": map_waypoint.images.split(",") if map_waypoint.images else []
    })

# Endpoint for rating a map
@app.route("/rate-map", methods=["POST"])
def rate_map():
    """
    Allows users to rate a map.
    ---
    tags:
      - Reviews and Ratings
    summary: Rate a map
    description: Allows users to submit or update their rating for a specific map.
    parameters:
      - name: username
        in: body
        required: true
        schema:
          type: string
      - name: mapId
        in: body
        required: true
        schema:
          type: integer
      - name: rating
        in: body
        required: true
        schema:
          type: number
    responses:
      200:
        description: Rating saved
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: Invalid request or rating format
      404:
        description: Map not found
      500:
        description: Couldn't save rating
    """
    data = request.json
    username = data.get("username")
    map_id = data.get("mapId")

    rating = data.get("rating")
    try:
        rating = float(rating)  # Ensure rating is a number
    except ValueError:
        return jsonify({"error": "Rating must be a number"}), 400

    if not all([username, map_id, rating]):
        return jsonify({"error": "Invalid request"}), 400

    # Ensure the map exists
    map_entry = Map.query.get(map_id)
    if not map_entry:
        return jsonify({"error": "Map not found"}), 404
    
    # Ensure fields are initialized
    map_entry.reviewsNumber = map_entry.reviewsNumber or 0
    map_entry.rating = map_entry.rating or 0.0

    review = Review.query.filter_by(userName=username, mapId=map_id).first()

    if review and review.rating is not None:
        # Recalculate rating considering previous user rating
        if map_entry.reviewsNumber and map_entry.rating:
            map_entry.rating = ((map_entry.rating * map_entry.reviewsNumber - review.rating + rating) 
                                / map_entry.reviewsNumber)
        review.rating = rating
    else:
        if review and review.rating is None:
            review.rating = 0.0  # Default value to avoid None issues

        # If the user hasn't rated before, update global rating and review count
        map_entry.rating = ((map_entry.rating or 0) * (map_entry.reviewsNumber or 0) + rating) / (map_entry.reviewsNumber + 1)
        map_entry.reviewsNumber = (map_entry.reviewsNumber or 0) + 1
        
        if review:
            review.rating = rating
        else:
            review = Review(userName=username, mapId=map_id, rating=rating)
            db.session.add(review)

    try:
        db.session.commit()
        return jsonify({"message": "Rating saved"}), 200
    except:
        db.session.rollback()
        return jsonify({"error": "Couldn't save rating"}), 500

# Endpoint for retrieving reviews of a map
@app.route("/get-review", methods=["GET"])
def get_review():
    """
    Retrieves reviews for a map.
    ---
    tags:
      - Reviews and Ratings
    summary: Get map reviews
    description: Fetches reviews left by users for a specific map.
    parameters:
      - name: mapId
        in: query
        required: true
        schema:
          type: integer
      - name: username
        in: query
        required: false
        schema:
          type: string
    responses:
      200:
        description: Reviews retrieved
        schema:
          type: object
          properties:
            review:
              type: string
              nullable: true
            reviews:
              type: array
              items:
                type: object
                properties:
                  username:
                    type: string
                  description:
                    type: string
    """
    map_id = request.args.get("mapId")
    username = request.args.get("username")

    # Fetch the review left by the requesting user (if exists)
    user_review = Review.query.filter_by(userName=username, mapId=map_id).first()

    # Retrieve all reviews excluding the user's own review
    other_reviews = Review.query.filter(Review.mapId == map_id, Review.userName != username).all()

    # Convert reviews to a list format
    reviews_list = [{"username": r.userName, "description": r.text} for r in other_reviews]

    return jsonify({
        "review": user_review.text if user_review else None,
        "reviews": reviews_list  # List of other users' reviews
    })

# Endpoint for submitting a review
@app.route("/review", methods=["POST"])
def save_review():
    """
    Submits or updates a review for a map.
    ---
    tags:
      - Reviews and Ratings
    summary: Submit a review
    description: Allows users to write or update their review for a specific map.
    parameters:
      - name: username
        in: body
        required: true
        schema:
          type: string
      - name: mapId
        in: body
        required: true
        schema:
          type: integer
      - name: review
        in: body
        required: true
        schema:
          type: string
    responses:
      200:
        description: Review saved
        schema:
          type: object
          properties:
            status:
              type: string
    """
    data = request.json
    map_id = data.get("mapId")
    username = data.get("username")
    review_text = data.get("review")

    # Check if user already has a review for this map
    review = Review.query.filter_by(userName=username, mapId=map_id).first()

    if review:
        review.text = review_text  # Update existing review
    else:
        review = Review(userName=username, mapId=map_id, text=review_text)
        db.session.add(review)  # Add new review

    db.session.commit()
    return jsonify({"status": "success"})

# Endpoint for updating the description of a map and its waypoint
@app.route("/save-waypoint", methods=["POST"]) 
def save_map_waypoint():
    """
    Updates the description of a map and its waypoint.
    ---
    tags:
      - Waypoints
    summary: Update map and waypoint description
    description: Updates the descriptions of a map and one of its waypoints.
    parameters:
      - name: mapId
        in: body
        required: true
        schema:
          type: integer
      - name: waypointId
        in: body
        required: true
        schema:
          type: integer
      - name: mapDescription
        in: body
        required: false
        schema:
          type: string
      - name: waypointDescription
        in: body
        required: false
        schema:
          type: string
    responses:
      200:
        description: Waypoint updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: Map or waypoint not found
    """
    data = request.json
    map_id = data.get("mapId")
    waypoint_id = data.get("waypointId")
    map_description = data.get("mapDescription")
    waypoint_description = data.get("waypointDescription")

    user_map = Map.query.filter_by(id=map_id).first()
    if not user_map:
        return jsonify({"message": "Map not found"}), 404

    # Check if the waypoint exists for the given map
    waypoint = MapWaypoint.query.filter_by(mapId=map_id, waypointId=waypoint_id).first()
    if not waypoint:
        return jsonify({"message": "Waypoint not found"}), 404

    user_map.description = map_description
    waypoint.description = waypoint_description

    db.session.commit()
    return jsonify({"message": "Waypoint updated successfully"})

@app.route("/upload-waypoint-image", methods=["POST"])
def upload_map_waypoint_image():
    """
    Uploads images for a specific waypoint on the map.
    ---
    tags:
      - Waypoints
    summary: Upload images for a waypoint
    description: Uploads images and associates them with a specific waypoint on the map.
    parameters:
      - name: mapId
        in: formData
        required: true
        type: integer
      - name: waypointId
        in: formData
        required: true
        type: integer
      - name: images
        in: formData
        required: true
        type: file
        collectionFormat: multi
    responses:
      200:
        description: Successfully uploaded images.
      404:
        description: Waypoint not found.
    """
    map_id = request.form.get("mapId")
    waypoint_id = request.form.get("waypointId")

    # Ensure the waypoint exists before proceeding
    waypoint = MapWaypoint.query.filter_by(mapId=map_id, waypointId=waypoint_id).first()
    if not waypoint:
        return jsonify({"error": "Waypoint not found"}), 404

    images = waypoint.images.split(",") if waypoint.images else []

    for image in request.files.getlist("images"):
        filename = image.filename
        # Save the image in the designated folder
        image.save(os.path.join("static/images/waypoints", filename))
        images.append(filename)

    waypoint.images = ",".join(images)
    db.session.commit()

    return jsonify({"success": True, "images": images})

@app.route("/remove-waypoint-image", methods=["POST"])
def remove_map_waypoint_image():
    """
    Removes an image from a waypoint.
    ---
    tags:
      - Waypoints
    summary: Remove an image from a waypoint
    description: Deletes an image associated with a waypoint, and removes it from storage if unused elsewhere.
    parameters:
      - name: mapId
        in: body
        required: true
        schema:
          type: integer
      - name: waypointId
        in: body
        required: true
        schema:
          type: integer
      - name: imageName
        in: body
        required: true
        schema:
          type: string
    responses:
      200:
        description: Successfully removed image.
      404:
        description: Waypoint or image not found.
    """
    data = request.json
    map_id = data.get("mapId")
    waypoint_id = data.get("waypointId")
    image_name = data.get("imageName")

    # Check if the waypoint exists
    waypoint = MapWaypoint.query.filter_by(mapId=map_id, waypointId=waypoint_id).first()
    if not waypoint:
        return jsonify({"error": "Waypoint not found"}), 404

    images = waypoint.images.split(",") if waypoint.images else []

    # Ensure the specified image exists in the waypoint
    if image_name not in images:
        return jsonify({"error": "Image not found in waypoint"}), 404

    # Remove the image only from this waypoint
    images.remove(image_name)
    waypoint.images = ",".join(images)
    db.session.commit()

    # Check if the image is used in other waypoints or drafts
    other_map_waypoints = MapWaypoint.query.filter(MapWaypoint.images.like(f"%{image_name}%")).all()
    other_draft_waypoints = DraftMapWaypoint.query.filter(DraftMapWaypoint.images.like(f"%{image_name}%")).all()

    # If the image is not used anywhere else, delete the file from storage
    if not other_map_waypoints and not other_draft_waypoints:
        img_path = os.path.join("static/images/waypoints", image_name)
        if os.path.isfile(img_path):
            os.remove(img_path)

    return jsonify({"success": True, "images": images})

# Retrieve a list of users and their maps
@app.route('/manage-maps', methods=['GET'])
def get_travelers_and_maps():
    """
    Retrieves a list of users and their associated maps.
    ---
    tags:
      - Manage Maps
    summary: Get users and their maps
    description: Fetches all users along with the maps they own and their blocked status.
    responses:
      200:
        description: List of users with their maps.
    """
    travellers = Traveller.query.all()  # Fetch all users
    traveller_list = []
    
    for traveller in travellers:
        maps = Map.query.filter_by(userName=traveller.userName).all()  # Fetch maps for the user
        map_list = []
        for map in maps:
            map_list.append({
                'id': map.id,
                'description': map.description
            })
        traveller_list.append({
            'userName': traveller.userName,
            'name': traveller.name,
            'surname': traveller.surname,
            'maps': map_list,
            'blocked': traveller.blocked
        })

    return jsonify(traveller_list)

# Block a user
@app.route('/block-user', methods=['PATCH'])
def block_user():
    """
    Blocks a user by setting their 'blocked' flag to True.
    ---
    tags:
      - Admin panel
    summary: Block a user
    description: Changes the blocked status of a user to True.
    parameters:
      - name: username
        in: body
        required: true
        schema:
          type: string
    responses:
      200:
        description: User successfully blocked or not found.
        schema:
          type: object
          properties:
            message:
              type: string
            noRecord:
              type: boolean
    """
    username = request.json.get('username')
    traveller = Traveller.query.filter_by(userName=username).first()
    if traveller:
        traveller.blocked = True
        db.session.commit()
        return jsonify({'message': f'User {username} has been blocked.'}), 200
    return jsonify({'noRecord': True}), 200

# Endpoint for unblocking a user
@app.route('/unblock-user', methods=['PATCH'])
def unblock_user():
    """
    Changes the blocked status of a user to False.
    ---
    tags:
      - Admin panel
    summary: Unblock a user
    description: Changes the blocked status of a user to False.
    parameters:
      - name: username
        in: body
        required: true
        schema:
          type: string
    responses:
      200:
        description: User unblocked or no record found
        schema:
          type: object
          properties:
            message:
              type: string
            noRecord:
              type: boolean
    """
    username = request.json.get('username')
    traveller = Traveller.query.filter_by(userName=username).first()
    if traveller:
        traveller.blocked = False
        db.session.commit()
        return jsonify({'message': f'User {username} has been unblocked.'}), 200
    return jsonify({'noRecord': True}), 200

# Endpoint for deleting a map and its associated waypoints
@app.route('/delete-map', methods=['POST'])
def delete_map():
    """
    Deletes a specified map and all its associated waypoints.
    ---
    tags:
      - Admin panel
    parameters:
      - name: mapId
        in: body
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Map deleted or no record found
        schema:
          type: object
          properties:
            message:
              type: string
            noRecord:
              type: boolean
    """
    map_id = request.json.get('mapId')
    map_to_delete = Map.query.filter_by(id=map_id).first()
    if map_to_delete:
        # Remove all waypoints associated with the map before deleting it
        MapWaypoint.query.filter_by(mapId=map_id).delete()
        db.session.delete(map_to_delete)
        db.session.commit()
        return jsonify({'message': 'Map has been deleted.'}), 200
    return jsonify({'noRecord': True}), 200

# Generates an image of the map based on given waypoints
def generate_map_image(waypoints, map_id):    
    m = folium.Map(location=[20, 0], zoom_start=2)

    bounds = []  # List of coordinates for automatic map scaling

    for wp in waypoints:
        waypoint = Waypoint.query.get(wp.waypointId)
        if waypoint:
            folium.Marker([waypoint.latitude, waypoint.longitude], popup=waypoint.name).add_to(m)
            bounds.append([waypoint.latitude, waypoint.longitude])  # Collecting coordinates for auto-scaling

    if bounds:
        m.fit_bounds(bounds)  # Adjust zoom to fit all markers

    # Save map as HTML file
    map_path = f"temp/map_{map_id}.html"
    img_path = f"temp/map_{map_id}.png"
    m.save(map_path)

    # Use a headless browser to capture a screenshot of the map
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(f"file://{os.path.abspath(map_path)}")
    driver.save_screenshot(img_path)
    driver.quit()

    return img_path

# Endpoint for generating and downloading a map as a PDF file
@app.route("/download-map-pdf", methods=["GET"])
def download_map_pdf():
    """
    Generates a PDF file with map details, including waypoints and images.
    ---
    tags:
      - Manage Maps
    parameters:
      - name: mapId
        in: query
        required: true
        schema:
          type: integer
    responses:
      200:
        description: PDF file generated successfully
        content:
          application/pdf:
            schema:
              type: string
              format: binary
      400:
        description: Missing map ID
        schema:
          type: object
          properties:
            error:
              type: string
      404:
        description: Map not found
        schema:
          type: object
          properties:
            error:
              type: string
    """
    map_id = request.args.get("mapId")
    if not map_id:
        return jsonify({"error": "Map ID is required"}), 400

    user_map = Map.query.filter_by(id=map_id).first()
    if not user_map:
        return jsonify({"error": "Map not found"}), 404

    waypoints = MapWaypoint.query.filter_by(mapId=map_id).order_by(MapWaypoint.waypointOrder).all()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    font_path = os.path.abspath("static/fonts/DejaVuSans.ttf")
    pdf.add_font('DejaVu', '', font_path, uni=True)
    pdf.add_font('DejaVu', 'B', font_path.replace(".ttf", "-Bold.ttf"), uni=True)
    pdf.set_font("DejaVu", "", 12)

    # Function to add a new page with a styled background
    def add_page_with_background():
        pdf.add_page()
        pdf.set_fill_color(107, 142, 35)  # Olive green background
        pdf.rect(0, 0, 210, 297, "F")  # Fill entire page
        pdf.set_draw_color(255, 255, 255)
        pdf.rect(5, 5, 200, 287)  # White border around content
    
    add_page_with_background()
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DejaVu", "B", 18)
    pdf.cell(200, 10, f'Map "{user_map.description}"', ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("DejaVu", "", 14)
    pdf.cell(200, 10, f"Author: {user_map.userName}", ln=True, align="C")
    pdf.ln(7)
    
    # Generate and insert the map image into the PDF
    map_image_path = generate_map_image(waypoints, map_id)
    pdf.image(map_image_path, x=10, w=190)
    
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(200, 10, "Route Points:", ln=True)
    pdf.ln(5)
    
    # Add details for each waypoint in the route
    for index, wp in enumerate(waypoints, start=1):
        waypoint = Waypoint.query.get(wp.waypointId)
        if waypoint:
            pdf.set_font("DejaVu", "B", 12)
            pdf.cell(200, 8, f"{index}. {waypoint.name}", ln=True)
            pdf.set_font("DejaVu", "", 11)
            pdf.cell(200, 6, f"Coordinates: {waypoint.latitude}, {waypoint.longitude}", ln=True)
            
            if wp.description:
                pdf.multi_cell(190, 6, f"Description: {wp.description}")
                pdf.ln(3)
            
            # Attach waypoint images if available
            if wp.images:
                image_files = wp.images.split(',')
                for image in image_files:
                    image_path = os.path.join("static/images/waypoints", image.strip())
                    if os.path.exists(image_path):
                        pdf.image(image_path, x=10, w=100)
                        pdf.ln(3)
            
            pdf.ln(5)
    
    # Footer text
    pdf.set_text_color(127, 127, 127)
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(200, 10, "Created using WanderMap - Personalized Travel Maps", ln=True, align="C")
    
    file_path = f"temp/map_{map_id}.pdf"
    os.makedirs("temp", exist_ok=True)
    pdf.output(file_path, 'F')
    
    return send_file(file_path, as_attachment=True)

@app.route("/check-subscription", methods=["GET"])
def check_subscription():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Missing username parameter"}), 400

    traveller = Traveller.query.filter_by(userName=username).first()
    return jsonify({"subscription": traveller.subscription if traveller else False})

if __name__ == "__main__":
    with app.app_context():  # Creates application context
        db.create_all()  # Initializes database tables if they do not exist
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
