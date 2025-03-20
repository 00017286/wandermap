import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import faiss
import numpy as np
from datetime import date
from app import db, app  # Import database, models, and Flask app from app.py
from app import Traveller, Waypoint

# Define waypoint categories to classify places
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

def get_traveller_vector(traveller):
    """Generate a numerical vector for a traveller based on their attributes."""
    age = (date.today().year - traveller.dateOfBirth.year) if traveller.dateOfBirth else 0
    return [
        int(traveller.hasKids), int(traveller.hasPets), int(traveller.extrovert),
        int(traveller.maritalState == 'Single'), int(traveller.maritalState == 'Married'),
        int(traveller.natureLover), int(traveller.museumLover), int(traveller.sportLover),
        int(traveller.gender == 'Female'), int(traveller.gender == 'Male'),
        int(age < 30), int(age > 50)  # Encode age groups
    ]

def get_waypoint_vector(waypoint):
    """Convert waypoint type into a feature vector using predefined categories."""
    return [int(any(waypoint.type in category for category in waypoint_categories)) for category in waypoint_categories]

# Load traveller and waypoint data from the database
with app.app_context():
    travellers = Traveller.query.all()
    waypoints = Waypoint.query.all()
    
    travellers_data = np.array([get_traveller_vector(t) for t in travellers], dtype='float32')
    waypoints_data = np.array([get_waypoint_vector(w) for w in waypoints], dtype='float32')

print(f"Loaded {len(travellers)} travellers and {len(waypoints)} waypoints")

# Create or update FAISS indexes for travellers
travellers_index = faiss.IndexFlatL2(12)  # L2 distance index for 12-dimensional vectors
if travellers_data.size > 0:
    travellers_index.add(travellers_data)  # Add traveller vectors to FAISS index
faiss.write_index(travellers_index, "faiss_index/travellers_index.faiss")
print("1. FAISS index updated for travellers!")

# Create or update FAISS indexes for waypoints
waypoints_index = faiss.IndexFlatL2(12)  # L2 distance index for 12-dimensional vectors
if waypoints_data.size > 0:
    waypoints_index.add(waypoints_data)  # Add waypoint vectors to FAISS index
faiss.write_index(waypoints_index, "faiss_index/waypoints_index.faiss")
print("2. FAISS index updated for waypoints!")