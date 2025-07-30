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

There also exists a big matrix of distances (from/to each station). However,
for the current purposes we only need distances between neighboring stations.
The current data structure is more compact, and allows for quick lookups.
Also, the big matrix (regarding tariffs) does not match one-to-one with the
distances used by Kilometer Kampioen, so we cannot use it directly.
"""

import json

DISTANCES_FILE = "./data/station_distances.json"
DISTANCES_PROCESSED_FILE = "./data/station_distances_processed.json"


class StationDistanceProcessor:
    def __init__(self):
        """Class to process station distances."""
        self.distances = self._load_distances()
        self.processed_distances = self._process_distances()

    def _load_distances(self) -> list:
        # JSON contains a list of structured dictionaries
        with open(DISTANCES_FILE, mode='r') as f:
            return json.load(f)

    def _process_distances(self):
        """Convert the list of distances to a dictionary for quick lookups."""
        station_distances_processed = {}

        for station_distance in self.distances:
            from_station = station_distance['fromStation'].title()  # Capitalize first letter
            to_station = station_distance['toStation'].title()  # Capitalize first letter
            distance = station_distance['distance'] / 10  # Convert from hectometers to kilometers

            # Check if key (from_station) already exists, if not, initialize empty dictionary
            # Then, for from_station dict, set key (to_station) with value distance
            # We use dictionaries for quick, easy and intuitive lookups (dict[from][to] yields dist)
            station_distances_processed.setdefault(from_station, {})[to_station] = distance

        return station_distances_processed

    def save_processed_distances(self):
        # Save to JSON file again, but now in the processed format
        with open(DISTANCES_PROCESSED_FILE, mode='w') as f:
            json.dump(self.processed_distances, f)


def main():
    """Main function to process and save the station distances.
    Run this script to generate the processed distances file."""

    distances_processor = StationDistanceProcessor()
    distances_processor.save_processed_distances()
    print("Station distances processed and saved successfully.")


if __name__ == "__main__":
    main()

