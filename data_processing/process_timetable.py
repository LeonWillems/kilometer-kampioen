import json
import pandas as pd
from copy import deepcopy
from data_processing.data_utils import read_timetable, save_timetable, add_duration_in_minutes
from data_processing.find_intercity_distance import BFS

DATA_FOLDER = "./data/"
DISTANCES_PROCESSED_FILE = "./data/station_distances_processed.json"


class TimetableProcessor:
    def __init__(
            self,
            timetable_file: str,
    ) -> None:
        """Class to process/enhance the timetable with distances and average speeds.
        Also, extend the distances dictionary with intercity connections."""
        self.timetable_file = timetable_file

        self.timetable_path = DATA_FOLDER + self.timetable_file
        self.processed_timetable_path = self.timetable_path.replace(
            ".csv", "_processed.csv"
        )

        self.distances = self._load_distances()
        self.timetable_df = read_timetable(self.timetable_path)

    def _load_distances(self):
        """Load the distances dictionary from a JSON file. 
        For structure, see the find_intercity_distance.py file"""
        with open(DISTANCES_PROCESSED_FILE, mode='r') as f:
            return json.load(f)

    def add_duration(self):
        """Calculate time taken between departure and arrival, in minutes."""
        self.timetable_df = add_duration_in_minutes(
            self.timetable_df,
            start_col='Departure',
            end_col='Arrival',
            duration_col='Duration'
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
        save_timetable(
            processed_timetable=self.timetable_df,
            processed_timetable_path=self.processed_timetable_path
        )

    def filter_and_sort(
            self,
            station: str, 
            current_time: pd.Timestamp,
            end_time: pd.Timestamp,
            min_transfer_time: int,
            max_transfer_time: int
        ) -> pd.DataFrame:
        df_copy = deepcopy(self.timetable_df)

        # Filter on departures from our current station
        df_station = df_copy[df_copy['Station'] == station]

        # Calculate time window
        min_time = current_time + pd.Timedelta(minutes=min_transfer_time)
        max_time = current_time + pd.Timedelta(minutes=max_transfer_time)

        # Filter on 'Departure' within the window,
        # and 'Arrival' before the end time
        df_time = df_station[
            (df_station['Departure'] >= min_time) &
            (df_station['Departure'] <= max_time) &
            (df_station['Arrival'] <= end_time)
        ]

        # Sort by 'Departure'
        df_time_sorted = df_time.sort_values(by='Departure')
        return df_time_sorted


def main():
    """Main function to process the timetable and save it.
    Run this script to generate the processed timetable file."""

    timetable_processor = TimetableProcessor(
        timetable_file="mock_timetable_processed.csv",
    )

    #timetable_processor.process_timetable()
    #timetable_processor.save_timetable()

    filtered_df = timetable_processor.filter_and_sort(
        station="Btl",
        current_time=pd.Timestamp("14:45"),
        end_time=pd.Timestamp("15:00"),
        min_transfer_time=3,
        max_transfer_time=30,
    )

    print(filtered_df)


if __name__ == "__main__":
    main()

