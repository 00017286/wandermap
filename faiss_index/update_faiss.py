import sys
import os

# Add parent directory to Python path to allow imports from parent folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import faiss  # Facebook AI Similarity Search library for vector indexing
import numpy as np
from datetime import date
from app import db, app 
from app import Traveller, Waypoint

# Define waypoint categories used for feature vector encoding
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
    """Generate feature vector for traveller using their profile attributes."""
    age = (date.today().year - traveller.dateOfBirth.year) if traveller.dateOfBirth else 0
    return [
        int(traveller.hasKids),
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
    ]

def get_waypoint_vector(waypoint):
    """Generate feature vector for waypoint by checking its type against predefined categories."""
    return [int(any(waypoint.type in category for category in waypoint_categories)) for category in waypoint_categories]

# Load traveller and waypoint data from db
with app.app_context():
    travellers = Traveller.query.all()  # Retrieve all travellers
    waypoints = Waypoint.query.all()    # Retrieve all waypoints

    # Convert traveller and waypoint objects to numerical vectors
    travellers_data = np.array([get_traveller_vector(t) for t in travellers], dtype='float32')
    waypoints_data = np.array([get_waypoint_vector(w) for w in waypoints], dtype='float32')

print(f"Loaded {len(travellers)} travellers and {len(waypoints)} waypoints")

# Create/update FAISS index for traveller vectors (12-dimensional)
travellers_index = faiss.IndexFlatL2(12)  # Use L2 - Euclidean distance
if travellers_data.size > 0:
    travellers_index.add(travellers_data)  # Add data to index
faiss.write_index(travellers_index, "faiss_index/travellers_index.faiss")  # Save index to disk
print("1. FAISS index updated for travellers!")

# Create/update FAISS index for waypoint vectors (also 12-dimensional)
waypoints_index = faiss.IndexFlatL2(12)  # Use L2 - Euclidean distance
if waypoints_data.size > 0:
    waypoints_index.add(waypoints_data)  # Add data to index
faiss.write_index(waypoints_index, "faiss_index/waypoints_index.faiss")  # Save index to disk
print("2. FAISS index updated for waypoints!")
