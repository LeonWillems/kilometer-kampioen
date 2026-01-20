from copy import deepcopy

from .find_intercity_distance import Dijkstra
from .preprocess_data import perform_preprocesing
from .data_utils import (
    save_intermediate_stations,
    load_distances, read_timetable,
    save_timetable, add_minutes_from_epoch
)

from settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()


class TimetableProcessor:
    def __init__(self):
        """Class to process/enhance the timetable with distances and average
        speeds. Also, extend the distances dictionary with intercity
        connections.

        Args:
        - version (str): Version of the timetable data (example: 'v0')

        Attributes:
        - distances: Dictionary containing distances between stations
        - timetable_df: DataFrame containing the timetable data
        - intermediate_stations: Dictionary to hold any intermediate stations
            found between bigger (intercity) connections

        Methods:
        - add_minute_stamps: Add integer timestamps since epochS
        - add_duration: Calculate duration between departure and arrival
        - enhance_distances_dict: Add distances for station pairs not in the
            distances dictionary
        - add_distances: Add distances to the timetable DataFrame
        - add_average_speed: Calculate average speed based on distance
            and duration
        - process_timetable: Run all processing steps in order
        - save_timetable: Save the processed timetable to a CSV file
        - filter_and_sort: Filter and sort the timetable based on station,
            time, and transfer conditions
        """
        self.distances = load_distances()
        self.timetable_df = read_timetable(processed=False, set_index=False)
        self.intermediate_stations = {}

    def add_minute_stamps(self):
        """Add integer timestamps as well. Minutes from epoch"""
        self.timetable_df = add_minutes_from_epoch(
            self.timetable_df,
            'Departure',
            'Departure_Int'
        )
        self.timetable_df = add_minutes_from_epoch(
            self.timetable_df,
            'Arrival',
            'Arrival_Int'
        )
        # Add durations in minutes for epoch columns
        self.timetable_df['Duration'] = (
            self.timetable_df['Arrival_Int']
            - self.timetable_df['Departure_Int']
        )

    def _update_intermediate_stations(
        self,
        from_station: str,
        to_station: str,
        path: list[str],
    ):
        """ Update the intermediate stations dictionary
        with any stations found between from_station and to_station.

        Args:
        - from_station (str): Starting station of the path
        - to_station (str): Ending station of the path
        - path (list): List of stations representing the path (including
            from_station and to_station)
        """
        if from_station not in self.intermediate_stations:
            self.intermediate_stations[from_station] \
                = {to_station: path}

        elif to_station not in self.intermediate_stations[from_station]:
            self.intermediate_stations[from_station][to_station] = path

        else:
            # A direct path might already exist between neighboring stations,
            # but have skipped alle the intermediate stations
            existing_path = \
                self.intermediate_stations[from_station][to_station]

            if len(path) > len(existing_path):
                self.intermediate_stations[from_station][to_station] = path

    def enhance_distances_dict(self):
        """Add a distance for each pair of stations from the timetable,
        that is not yet in the distances dictionary. Context: initially
        only neighboring stations, not intercity connections."""

        # Get unique [from_station, to_station] station pairs from
        # the timetable
        unique_pairs = self.timetable_df[['Station', 'To']] \
            .drop_duplicates().values.tolist()

        # Initialize a Dijkstra instance with the distances dictionary once
        # Deepcopy is used to avoid modifying the original distances,
        # and to ensure Dijkstra works with the current state of distances
        dijkstra = Dijkstra(adjacency_list=deepcopy(self.distances))

        for from_station, to_station in unique_pairs:
            if to_station not in self.distances[from_station]:
                # If the distance does not exist, calculate it
                dijkstra.construct_paths(from_station)
                path, distance = dijkstra.search(to_station)

                # If a path was found with some non-zero distance
                if path and distance > 0:
                    # Add the distance to the distances dictionary,
                    # both directions
                    self.distances[from_station][to_station] = distance
                    self.distances[to_station][from_station] = distance

            elif to_station in self.distances[from_station]:
                # Neighboring stations, direct distance known
                path = [from_station, to_station]

            # Update intermediate stations with path, both directions
            self._update_intermediate_stations(from_station, to_station, path)
            self._update_intermediate_stations(
                to_station, from_station, path[::-1]
            )

    def add_distances(self):
        """Add distances between stations to the timetable, in kilometers."""
        self.timetable_df['Distance'] = self.timetable_df.apply(
            lambda row: self.distances[row['Station']][row['To']],
            axis=1
        )

    def add_average_speed(self):
        """Add average speed to the timetable, in km/h."""
        self.timetable_df['Speed'] = (
            self.timetable_df['Distance']
            / (self.timetable_df['Duration'] / 60)
        ).round(1)

    def process_timetable(self):
        """Run all processing steps in order."""
        self.add_minute_stamps()
        self.enhance_distances_dict()
        save_intermediate_stations(self.intermediate_stations)

        self.add_distances()
        self.add_average_speed()
        save_timetable(timetable_df=self.timetable_df, from_settings=True)


if __name__ == "__main__":
    """Processing functionality of the raw & timetable data."""
    perform_preprocesing()
    print("Preprocessing done successfully.")

    timetable_processor = TimetableProcessor()
    timetable_processor.process_timetable()

    print("Timetable processed and saved successfully.")
