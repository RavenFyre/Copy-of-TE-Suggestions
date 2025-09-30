# Overview
# - Contains various Python functions to manage suggestions data stored in JSON (suggestions.json)

# Libraries to import
import json
import os

# File where suggestions and panel info is stored
data_file = "data/suggestions.json"

# Load suggestions.json into a Python dictionary
# If the file does not exist, create a new one with base structure
def load_data():
    if not os.path.exists(data_file):
        # Base structure for new file
        base_structure = {
            "last_id": 0,       # Tracks the last used suggestion ID
            "panel_id": None,   # Stores the current suggestion panel message ID
            "suggestions": []   # List to store all suggestions
            }
        save_data(base_structure)
        # Read the JSON file and return as a Python dictionary
    with open(data_file, "r") as f:
        return json.load(f)

# Save a Python dictionary back into suggestions.json
def save_data(data: dict):
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)

# Increment last_id and return a new unique suggestion ID
def get_next_id():
    data = load_data()
    data["last_id"] += 1
    save_data(data)
    return data["last_id"]

# Get the current suggestion panel message ID (if any)
def get_panel_id():
    data = load_data()
    return data.get("panel_id")

# Update the suggestion panel message ID
def set_panel_id(message_id: int):
    data = load_data()
    data["panel_id"] = message_id
    save_data(data)