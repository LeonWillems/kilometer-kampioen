

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
        """Initialize the RouteIndicator with a timetable.

        Attributes
        - indicator_dict: Dict to hold the route indicators between stations.
            Example: {'Ht': {'Ehv': 'I', 'Tb': 'I}, ...}

        Methods
        - init_indicator_table: Initialize the indicator_table
        - update_indicator: Update the indicator table based on a timetable row
        - get_section_driven_by_type: Check if a section has been driven by a
          specific train type
        - copy: Create a copy of the RouteIndicator instance
        """
        self.indicator_dict: dict[str, dict[str, str]] = dict()

    def _add_to_dict(
        self,
        from_station: str,
        to_station: str,
        train_type: str
    ) -> None:
        """Deal with all cases of appending the train_type string to the
        possible already existing train types.

        Args:
        - from_station (str): Station code, example 'Ehv'
        - to_station (str): Station code, example 'Ht'
        - train_type (str): Type of train, 'S' or 'I'
        """
        if from_station not in self.indicator_dict:
            self.indicator_dict[from_station] = {to_station: train_type}

        elif to_station not in self.indicator_dict[from_station]:
            self.indicator_dict[from_station][to_station] = train_type

        else:
            self.indicator_dict[from_station][to_station] += train_type

    def update_indicator_table(self, timetable_row: pd.Series) -> None:
        """Update the indicator table based on a timetable row.
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
        long_train_type = timetable_row['Type']

        # Convert to 'S' for Sprinter or 'I' for Intercity
        if long_train_type not in SETTINGS.TYPE_CONVERSION:
            raise ValueError(f"Unknown train type: {long_train_type}")

        train_type = SETTINGS.TYPE_CONVERSION[long_train_type]
        self._add_to_dict(from_station, to_station, train_type)
        self._add_to_dict(to_station, from_station, train_type)

        # Include all intermediate stations for an intercity as well
        if train_type == 'I':
            stations = INTERMEDIATE_STATIONS[from_station][to_station]

            # Go over each consecutive pair in the intermediate stations list
            for from_station, to_station in zip(stations[:-1], stations[1:]):
                self._add_to_dict(from_station, to_station, train_type)
                self._add_to_dict(to_station, from_station, train_type)

    def get_distance_counted(
        self,
        from_station: str,
        to_station: str,
        train_type: str,
        distance: float,
    ) -> float:
        """Get the number of kilometers that may be counted for this section.
        Depends on intermediate sections that have already been driven.
        See 'information/rules-2024.py' for the exact rules.

        Args:
        - from_station (str): Starting station of the route
        - to_station (str): Destination station of the route
        - train_type (str): Type of train
            ('Spr' for Sprinter, 'Int' for Intercity)
        - distance (float): Distance between the two stations (in kilometers)

        Returns:
        - float: Number of kilometers that may be counted for this section
        """
        if train_type not in SETTINGS.TYPE_CONVERSION:
            raise ValueError(f"Unknown train type: {train_type}")

        # Convert to 'S' for Sprinter or 'I' for Intercity
        short_train_type = SETTINGS.TYPE_CONVERSION[train_type]

        # Keep track of how many kilometers may be counted for this section
        distance_counted = 0

        if short_train_type == 'S':  # No intermediate stations (by design)
            # Get string of train types that have already driven the current
            # section. Example: 'SSI' (two sprinters, one intercity)
            types_driven = self.indicator_dict.get(
                from_station, {}
            ).get(to_station, '')

            if len(types_driven) < 2:  # May only count twice at most
                distance_counted += distance

        else:  # Intercity section with intermediate stations (by design)
            stations = INTERMEDIATE_STATIONS[from_station][to_station]

            # Go over each consecutive pair in the intermediate stations list
            for from_station, to_station in zip(stations[:-1], stations[1:]):
                types_driven = self.indicator_dict.get(
                    from_station, {}
                ).get(to_station, '')
                intermediate_distance \
                    = STATION_DISTANCES[from_station][to_station]

                # 'I' may only be counted once!
                if len(types_driven) == 1 and 'I' not in types_driven:
                    distance_counted += intermediate_distance
                elif len(types_driven) == 0:  # Section not driven at all yet
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
        indicator.update_indicator_table(row)

    print(indicator.indicator_dict)
