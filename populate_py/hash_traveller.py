from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import bcrypt

# Create a Flask application instance
app = Flask(__name__)

# Database connection configuration
app.config['SQLALCHEMY_DATABASE_URI'] = ('mssql+pyodbc://DESKTOP-RC369C7\\SQLEXPRESS01/WanderMap_DB'
                                         '?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking to improve performance

# Initialize SQLAlchemy for database interactions
db = SQLAlchemy(app)

# Define the Traveller model, representing the 'Traveller' table in the database
class Traveller(db.Model):
    __tablename__ = 'Traveller'
    userName = db.Column(db.String(255), primary_key=True)  # Username as the primary key
    password = db.Column(db.String(255), nullable=False)  # Stores the password (should be hashed)

# Function to check if a password is already hashed
def is_hashed(password):
    return password.startswith("$2b$")  # Bcrypt hashed passwords start with "$2b$"

# Function to hash and update passwords for all users
def update_all_passwords():
    with app.app_context():  # Ensure the function runs within the Flask app context
        travellers = Traveller.query.all()  # Retrieve all users from the database

        for traveller in travellers:
            salt = bcrypt.gensalt()  # Generate a random salt for bcrypt hashing
            hashed_password = bcrypt.hashpw(traveller.password.encode("utf-8"), salt).decode("utf-8")  
            # Encode password to bytes, hash it, then decode back to string
            traveller.password = hashed_password  # Store the hashed password in the database
            print(f"Password updated for user: {traveller.userName}")

        db.session.commit()  # Commit all changes to the database
        print("All user passwords have been securely hashed and updated!")

# Execute the password update function if the script is run directly
if __name__ == "__main__":
    update_all_passwords()
