import pandas as pd
from copy import deepcopy

from data_processing.data_utils import (
    load_intermediate_stations, load_distances
)
from settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()

# Dictionary with pairwise distances for all neighboring stations
INTERMEDIATE_STATIONS = load_intermediate_stations()

# Dictionary that includes all intermediate stations
# for any intercity run in the dataset
STATION_DISTANCES = load_distances()

# Get all unique station names, ground truth = distances table
ALL_STATIONS = sorted(list(set(STATION_DISTANCES.keys())))


class RouteIndicator:
    def __init__(self):
        """Initialize the RouteIndicator. A pair in the dict {'Ht': {'Ehv': 1}}
        will always have a nonzero integer value (number of times driven).

        Attributes
        - indicator_dict: Dict to hold the route indicators between stations.
            Example: {'Ht': {'Ehv': 1, 'Tb': 2}, ...}

        Methods
        - init_indicator_table: Initialize the indicator_table
        - update_indicator_dict: Update the indicator table based on a
            timetable row
        - copy: Create a copy of the RouteIndicator instance
        """
        self.indicator_dict: dict[str, dict[str, int]] = dict()

    def _add_to_dict(self, from_station: str, to_station: str) -> None:
        """Deal with all cases of adding one to the number of times driven.

        Args:
        - from_station (str): Station code, example 'Ehv'
        - to_station (str): Station code, example 'Ht'
        """
        if from_station not in self.indicator_dict:
            self.indicator_dict[from_station] = {to_station: 1}

        elif to_station not in self.indicator_dict[from_station]:
            self.indicator_dict[from_station][to_station] = 1

        else:
            self.indicator_dict[from_station][to_station] += 1

    def update_indicator_dict(self, timetable_row: pd.Series) -> None:
        """Update the indicator dict based on a timetable row.
        Each cell contains a string, with a concatenations of train
        types letters ('S' for Sprinter, 'I' for Intercity).

        For intercity sections, we also indicate all intermediate stations
        on that section. Example: take the intercity from 'Ht' to 'Ehv', then
        we need to include 'Vg', 'Btl', 'Bet' and 'Ehs' as well.

        Args:
        - timetable_row (pd.Series): A row from the timetable DataFrame
            containing at least the 'Station', 'To', and 'Type' columns
        """
        from_station = timetable_row['Station']
        to_station = timetable_row['To']

        # Include all intermediate stations for an intercity as well
        # Will still work for neighboring stations!
        stations = INTERMEDIATE_STATIONS[from_station][to_station]

        # Go over each consecutive pair in the intermediate stations list
        for from_station, to_station in zip(stations[:-1], stations[1:]):
            self._add_to_dict(from_station, to_station)
            self._add_to_dict(to_station, from_station)

    def get_distance_counted(
        self,
        from_station: str,
        to_station: str,
    ) -> float:
        """Get the number of kilometers that may be counted for this section.
        Depends on intermediate sections that have already been driven.
        See 'information/rules-2026.py' for the exact rules.

        Args:
        - from_station (str): Starting station of the route
        - to_station (str): Destination station of the route

        Returns:
        - float: Number of kilometers that may be counted for this section
        """
        # Keep track of how many kilometers may be counted for this section
        distance_counted = 0

        # Get all intermediate stations. Still works for neighboring stations
        stations = INTERMEDIATE_STATIONS[from_station][to_station]

        # Go over each consecutive pair in the intermediate stations list
        for from_station, to_station in zip(stations[:-1], stations[1:]):
            # Pair only exists when time driven is a positive nonzero integer
            times_driven = self.indicator_dict.get(
                from_station, {}
            ).get(to_station, 0)

            intermediate_distance \
                = STATION_DISTANCES[from_station][to_station]

            # May only count once
            if times_driven == 0:  # Section not driven at all yet
                distance_counted += intermediate_distance

        return distance_counted

    def copy(self):
        """Create a copy of the RouteIndicator instance.

        Returns:
        - RouteIndicator: A new instance of RouteIndicator with a
            copied indicator table
        """
        new_indicator = RouteIndicator()
        new_indicator.indicator_dict = deepcopy(self.indicator_dict)
        return new_indicator


if __name__ == "__main__":
    """Main function to demonstrate the RouteIndicator functionality.

    Will get some random rows from the timetable and update the
    indicator table.
    """
    from data_processing.data_utils import read_timetable
    indicator = RouteIndicator()

    # Init version and corresponding timetable
    version = 'v0'
    timetable_df: pd.DataFrame = read_timetable(
        version=version, processed=True
    )

    # Get unique stations and some random rides
    stations_list = timetable_df['Station'].unique()
    test_rides = timetable_df.sample(n=4)

    # Iteratively update the indicator table with the test rides
    for _, row in test_rides.iterrows():
        indicator.update_indicator_dict(row)

    print(indicator.indicator_dict)
