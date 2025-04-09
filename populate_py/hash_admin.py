from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = ('mssql+pyodbc://DESKTOP-RC369C7\\SQLEXPRESS01/WanderMap_DB'
                                         '?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Administrator(db.Model):
    __tablename__ = 'Administrator'
    userName = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.String(255), nullable=False)

def is_hashed(password):
    return password.startswith("$2b$")

def update_all_admin_passwords():
    with app.app_context():
        administrators = Administrator.query.all()

        for admin in administrators:
            if not is_hashed(admin.password):
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(admin.password.encode("utf-8"), salt).decode("utf-8")
                admin.password = hashed_password
                print(f"Password updated for administrator: {admin.userName}")

        db.session.commit()
        print("All administrator passwords have been securely hashed and updated!")

if __name__ == "__main__":
    update_all_admin_passwords()
