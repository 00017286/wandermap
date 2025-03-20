from faker import Faker
import random
import pandas as pd
from app import db, Waypoint, app  # Importing Waypoint model and Flask app

fake = Faker()

# User preferences and corresponding point categories
PREFERENCES = {
    "hasKids": ["amusement_park", "water_park", "theme_park"],
    "hasPets": ["pet", "dog_park", "park"],
    "extrovert": [],  # Not defined
    "natureLover": ["forest", "beach", "wood", "water", "nature_reserve"],
    "museumLover": ["art_gallery", "museum", "gallery", "attraction"],
    "sportLover": ["climbing", "surfing", "stadium", "swimming_pool", "sports_centre"],
    "female": ["fashion", "cosmetics", "jewelry"],
    "male": ["car", "electronics"],
    "young": ["nightclub", "pub", "skateboard"],
    "elderly": ["spa"]
}

def get_user_preferences(user):
    """Generates a list of preferred point categories based on user attributes."""
    categories = []

    if user["hasKids"]:
        categories.extend(PREFERENCES["hasKids"])
    if user["hasPets"]:
        categories.extend(PREFERENCES["hasPets"])
    if user["natureLover"]:
        categories.extend(PREFERENCES["natureLover"])
    if user["museumLover"]:
        categories.extend(PREFERENCES["museumLover"])
    if user["sportLover"]:
        categories.extend(PREFERENCES["sportLover"])

    # Gender and age preferences
    if user["gender"] == "Female":
        categories.extend(PREFERENCES["female"])
    elif user["gender"] == "Male":
        categories.extend(PREFERENCES["male"])

    age = 2024 - int(user["dateOfBirth"].split("-")[0])  # Extract birth year and calculate age
    if age < 30:
        categories.extend(PREFERENCES["young"])
    elif age > 50:
        categories.extend(PREFERENCES["elderly"])

    return set(categories)  # Remove duplicates

def get_filtered_waypoints(categories):
    """Fetches waypoints from the database based on user preferences."""
    with app.app_context():
        waypoints = Waypoint.query.filter(Waypoint.type.in_(categories)).all()
        return waypoints if waypoints else []

num_users = 1000  # Number of users

# Generating synthetic users
usernames = set()
users = []
while len(users) < num_users:
    username = fake.user_name()
    if username in usernames:
        continue  # Skip duplicate usernames
    usernames.add(username)

    user = {
        "userName": username,
        "password": fake.password(),
        "email": fake.email(),
        "name": fake.first_name(),
        "surname": fake.last_name(),
        "dateOfBirth": str(fake.date_of_birth(minimum_age=18, maximum_age=80)),
        "gender": random.choice(["Male", "Female", "Other"]),
        "maritalState": random.choice(["Single", "Married", "Divorced"]),
        "hasKids": int(random.choice([True, False])),   # 👈 True -> 1, False -> 0
        "hasPets": int(random.choice([True, False])),
        "extrovert": int(random.choice([True, False])),
        "natureLover": int(random.choice([True, False])),
        "museumLover": int(random.choice([True, False])),
        "sportLover": int(random.choice([True, False])),
    }
    users.append(user)

# Saving users to a CSV file
df_users = pd.DataFrame(users)
df_users.to_csv("synthetic_users.csv", index=False, encoding="utf-8-sig")
print("1000 users generated!")

num_maps = 2000  # Number of maps
starting_map_id = 1  # Initial ID for maps

df_users = pd.read_csv("synthetic_data/synthetic_users.csv")  # Load generated users
usernames = df_users.to_dict("records")

maps = []
map_waypoints = []

for map_id in range(starting_map_id, starting_map_id + num_maps):
    user = random.choice(usernames)  # Select a random user for each map
    map_entry = {
        "id": map_id,
        "description": f"Map {map_id}",
        "userName": user["userName"],
        "rating": round(random.uniform(1, 5), 1)  # Random rating between 1.0 and 5.0
    }
    maps.append(map_entry)

    # Get preferred categories for the user
    preferred_categories = get_user_preferences(user)
    
    # Fetch matching waypoints from the database
    available_waypoints = get_filtered_waypoints(preferred_categories)

    # If waypoints exist, randomly select 2 to 5 waypoints
    if available_waypoints:
        chosen_waypoints = random.sample(available_waypoints, min(len(available_waypoints), random.randint(2, 5)))
        
        for order, waypoint in enumerate(chosen_waypoints):
            map_waypoints.append({
                "mapId": map_id,
                "waypointId": waypoint.id,  # ID from the database
                "waypointOrder": order + 1
            })

# Saving maps and waypoints to CSV files
df_maps = pd.DataFrame(maps)
df_map_waypoints = pd.DataFrame(map_waypoints)

df_maps.to_csv("synthetic_data/synthetic_maps.csv", index=False)
df_map_waypoints.to_csv("synthetic_data/synthetic_map_waypoints.csv", index=False, encoding="utf-8-sig")

print(f"{num_maps} maps generated with waypoints!")
