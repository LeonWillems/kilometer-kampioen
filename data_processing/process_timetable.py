import json
import pandas as pd
from copy import deepcopy
from find_intercity_distance import BFS

DATA_FOLDER = "./data/"
DISTANCES_PROCESSED_FILE = "./data/station_distances_processed.json"


class TimetableProcessor:
    def __init__(
            self,
            timetable_name: str,
            processed_timetable_name: str,
    ) -> None:
        """Class to process/enhance the timetable with distances and average speeds.
        Also, extend the distances dictionary with intercity connections."""
        self.timetable_name = timetable_name
        self.processed_timetable_name = processed_timetable_name

        self.timetable_path = DATA_FOLDER + self.timetable_name
        self.processed_timetable_path = DATA_FOLDER + self.processed_timetable_name

        self.distances = self._load_distances()
        self.timetable_df = self._read_timetable()

    def _load_distances(self):
        """Load the distances dictionary from a JSON file. 
        For structure, see the find_intercity_distance.py file"""
        with open(DISTANCES_PROCESSED_FILE, mode='r') as f:
            return json.load(f)

    def _read_timetable(self):
        """Read the timetable CSV file into a pandas DataFrame. Interpret the 
        'Departure' and 'Arrival' columns as datetime objects. (Format: '14:20')"""
        timetable_df = pd.read_csv(
            self.timetable_path,
            sep=';',
            header=0,
            index_col=False,
        )

        for col in ['Departure', 'Arrival']:
            timetable_df[col] = pd.to_datetime(
                timetable_df[col], format='%H:%M'
            )

        return timetable_df

    def add_duration(self):
        """Calculate time taken between departure and arrival, in minutes."""
        self.timetable_df['Duration'] = (
            (self.timetable_df['Arrival'] - self.timetable_df['Departure']) \
            .dt.total_seconds() / 60
        ).astype(int)

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
        self.timetable_df.to_csv(
            self.processed_timetable_path,
            sep=';',
            index=False,
            float_format='%.1f'  # Format distances and speeds to one decimal place
        )


def main():
    """Main function to process the timetable and save it.
    Run this script to generate the processed timetable file."""

    timetable_processor = TimetableProcessor(
        timetable_name="mock_timetable.csv",
        processed_timetable_name="mock_timetable_processed.csv"
    )

    timetable_processor.process_timetable()
    timetable_processor.save_timetable()


if __name__ == "__main__":
    main()
    
