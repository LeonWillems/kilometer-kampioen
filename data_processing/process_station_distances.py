"""
Got the distances from https://github.com/nanderv/trainkms. They are in the following format:
[
    {
        "fromStation": "ehv",
        "toStation": "ehs",
        "distance": 26  # in hectometers
    },
    ...
]

...and we convert them to a dictionary with the following structure:

{
    "Ehv": {"Ehs": 2.6, ...},
    ...
}
"""

import json

DISTANCES_FILE = "./data/station_distances.json"
DISTANCES_PROCESSED_FILE = "./data/station_distances_processed.json"


with open(DISTANCES_FILE, mode='r') as f:
    # JSON contains a list of structured dictionaries
    data = json.load(f)

station_distances_processed = {}

for station_distance in data:
    from_station = station_distance['fromStation'].title()  # Capitalize first letter
    to_station = station_distance['toStation'].title()  # Capitalize first letter
    distance = station_distance['distance'] / 10  # Convert from hectometers to kilometers

    # Check if key (from_station) already exists, if not, initialize empty dictionary
    # Then, for from_station dict, set key (to_station) with value distance
    # We use dictionaries for quick, easy and intuitive lookups (dict[from][to] yields dist)
    station_distances_processed.setdefault(from_station, {})[to_station] = distance

with open(DISTANCES_PROCESSED_FILE, mode='w') as f:
    json.dump(station_distances_processed, f)
    