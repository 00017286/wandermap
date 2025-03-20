import requests
from app import db, Waypoint, app  # Import database, Waypoint model, and Flask application from app.py

# List of categories for querying points of interest
CATEGORIES = {
    "tourism": ["art_gallery", "museum", "gallery", "attraction"], #museums
    "leisure": ["park", "nature_reserve", "amusement_park", "water_park", "theme_park", "stadium", "swimming_pool", "sports_centre", "dog_park"], #nature, kids, sport, pets
    "natural": ["forest", "beach", "wood", "water"], #nature
    "sport": ["climbing", "surfing", "skateboard"], #sport
    "amenity": ["cinema", "restaurant", "nightclub", "pub", "spa"], #age
    "shop": ["pet", "car", "electronics", "fashion", "cosmetics", "jewelry"] #pets, gender
}

def fetch_osm_data(city_name, lat, lon):
    """Sends a request to OpenStreetMap (Overpass API) and retrieves a list of points of interest (POIs)."""

    radius_km = 30  # Search radius in kilometers

    # Construct the Overpass API query dynamically based on the categories
    query_parts = []
    for key, values in CATEGORIES.items():
        for value in values:
            query_parts.append(f'node["{key}"="{value}"](around:{radius_km * 1000}, {lat}, {lon});')

    query = f"""
    [out:json];
    ({' '.join(query_parts)});
    out body;
    """
    
    url = "http://overpass-api.de/api/interpreter"
    response = requests.get(url, params={"data": query})  

    # If the request was successful, return the list of elements; otherwise, return an empty list
    return response.json().get("elements", []) if response.status_code == 200 else []

def save_to_db(places):
    """Saves retrieved POIs to the database."""

    with app.app_context():  # Ensure the function runs within the Flask app context
        for place in places:
            name = place.get("tags", {}).get("name", "Unknown")  # Extract place name; default to "Unknown" if missing
            lat = place.get("lat")  # Latitude
            lon = place.get("lon")  # Longitude

            # Identify the category (type) of the place
            place_tags = place.get("tags", {})
            place_type = None
            for key, values in CATEGORIES.items():
                if key in place_tags and place_tags[key] in values:
                    place_type = place_tags[key]  # Assign the place type (e.g., "museum", "hotel")
                    break
            
            if not place_type:
                continue  # Skip places without a known type
            
            # Check if the place already exists in the database to prevent duplicates
            existing = Waypoint.query.filter_by(latitude=lat, longitude=lon).first()
            if not existing:
                waypoint = Waypoint(name=name, latitude=lat, longitude=lon, type=place_type)
                db.session.add(waypoint)
        
        db.session.commit()
        print("DB populated successfully!")  # Log a success message after committing changes

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure database tables exist before inserting data

    # Coordinates of selected cities
    cities = {
        "Amsterdam": (52.3676, 4.9041),
        "Brussels": (50.8503, 4.3517),
        "Paris": (48.8566, 2.3522),
    }

    for city, (lat, lon) in cities.items():
        places = fetch_osm_data(city, lat, lon)  # Fetch POIs from OpenStreetMap
        save_to_db(places)  # Save the results to the database