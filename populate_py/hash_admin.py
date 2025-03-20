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

# Define the Administrator model, representing the 'Administrator' table in the database
class Administrator(db.Model):
    __tablename__ = 'Administrator'
    userName = db.Column(db.String(255), primary_key=True)  # Username as the primary key
    password = db.Column(db.String(255), nullable=False)  # Hashed password storage

# Function to check if a password is already hashed
def is_hashed(password):
    return password.startswith("$2b$")  # Bcrypt hashed passwords start with "$2b$"

# Function to hash and update passwords for all administrators
def update_all_admin_passwords():
    with app.app_context():  # Ensure the function runs within the Flask app context
        administrators = Administrator.query.all()  # Retrieve all administrators from the database

        for admin in administrators:
            if not is_hashed(admin.password):  # Only hash passwords if they are not already hashed
                salt = bcrypt.gensalt()  # Generate a random salt for bcrypt hashing
                hashed_password = bcrypt.hashpw(admin.password.encode("utf-8"), salt).decode("utf-8")  # Hash the password
                admin.password = hashed_password  # Update the password field with the hashed version
                print(f"Password updated for administrator: {admin.userName}")

        db.session.commit()  # Commit all changes to the database
        print("All administrator passwords have been securely hashed and updated!")

# Execute the password update function if the script is run directly
if __name__ == "__main__":
    update_all_admin_passwords()
