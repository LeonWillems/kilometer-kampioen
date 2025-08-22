import json
from copy import deepcopy
from .find_intercity_distance import BFS
from .timetable_utils import read_timetable, save_timetable, add_duration_in_minutes
from ..project.settings import Settings


class TimetableProcessor:
    def __init__(self, version: str) -> None:
        """Class to process/enhance the timetable with distances and average speeds.
        Also, extend the distances dictionary with intercity connections.
        
        Args:
        - version (str): Version of the timetable data (example: 'v0')
        
        Attributes:
        - distances: Dictionary containing distances between stations
        - timetable_df: DataFrame containing the timetable data
        
        Methods:
        - _load_distances: Load distances from a JSON file
        - add_duration: Calculate duration between departure and arrival
        - enhance_distances_dict: Add distances for station pairs not in the distances dictionary
        - add_distances: Add distances to the timetable DataFrame
        - add_average_speed: Calculate average speed based on distance and duration
        - process_timetable: Run all processing steps in order
        - save_timetable: Save the processed timetable to a CSV file
        - filter_and_sort: Filter and sort the timetable based on station, time, and transfer conditions
        """
        self.version = version

        self.distances = self._load_distances()
        self.timetable_df = read_timetable(
            version=self.version,
            processed=False,
        )

    def _load_distances(self):
        """Load the distances dictionary from a JSON file. 
        For the file's structure, see the find_intercity_distance.py file."""
        with open(Settings.PROCESSED_DISTANCES_PATH, mode='r') as f:
            return json.load(f)

    def add_duration(self):
        """Calculate time taken between departure and arrival, in minutes."""
        self.timetable_df = add_duration_in_minutes(
            self.timetable_df,
            start_col='Departure',
            end_col='Arrival',
            duration_col='Duration',
        )

    def enhance_distances_dict(self):
        """Add a distance for each pair of stations from the timetable,
        that is not yet in the distances dictionary. Context: initially
        only neighboring stations, not intercity connections."""

        # Get unique [from_station, to_station] station pairs from the timetable
        unique_pairs = self.timetable_df[['Station', 'To']] \
            .drop_duplicates().values.tolist()

        # Initialize BFS instance with the distances dictionary once
        # Deepcopy is used to avoid modifying the original distances,
        # and to ensure BFS works with the current state of distances
        bfs = BFS(adjacency_list=deepcopy(self.distances))

        for from_station, to_station in unique_pairs:
            if to_station not in self.distances[from_station]:
                # If the distance does not exist, calculate it
                path, distance = bfs.search(start=from_station, goal=to_station)
                
                # If a path was found with some non-zero distance
                if path and distance > 0:
                    # Add the distance to the distances dictionary, both directions
                    self.distances[from_station][to_station] = distance
                    self.distances[to_station][from_station] = distance

    def add_distances(self):
        """Add distances between stations to the timetable, in kilometers."""
        self.timetable_df['Distance'] = self.timetable_df.apply(
            lambda row: self.distances[row['Station']][row['To']],
            axis=1
        )

    def add_average_speed(self):
        """Add average speed to the timetable, in km/h."""
        self.timetable_df['Speed'] = (
            self.timetable_df['Distance'] / (self.timetable_df['Duration'] / 60)
        ).round(1)

    def process_timetable(self):
        """Run all processing steps in order."""
        self.add_duration()
        self.enhance_distances_dict()
        self.add_distances()
        self.add_average_speed()

    def save_timetable(self):
        """Save the processed timetable to a CSV file."""
        save_timetable(
            timetable_df=self.timetable_df,
            version=self.version,
        )


def perform_timetable_preprocessing(version: str):
    """Preprocessing function for version 0 of the timetable data.
    
    Args:
    - version (str): Version of data model, example 'v0'
    """

    timetable_processor = TimetableProcessor(version=version)

    timetable_processor.process_timetable()
    timetable_processor.save_timetable()
    
    print("Timetable processed and saved successfully.")


if __name__ == "__main__":
    current_version = 'v0'
    perform_timetable_preprocessing(current_version)

