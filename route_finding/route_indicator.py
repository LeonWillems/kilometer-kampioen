import pandas as pd
from ..settings import Settings
from ..data_processing.data_utils import load_intermediate_stations, load_distances


class RouteIndicator:
    def __init__(self):
        """Initialize the RouteIndicator with a timetable.

        Attributes:
        - stations: Unique stations from the timetable
        - indicator_table: DataFrame to hold the route indicators between stations
        - intermediate_stations: Dictionary that includes all intermediate stations
            for any intercity run in the dataset
        - station_distances: Dictionary with pairwise distances for all neighboring
            stations

        Methods
        - init_indicator_table: Initialize the indicator_table
        - update_indicator: Update the indicator table based on a timetable row
        - get_section_driven_by_type: Check if a section has been driven by a 
          specific train type
        - copy: Create a copy of the RouteIndicator instance
        """
        self.stations = list()
        self.indicator_table = pd.DataFrame()
        self.intermediate_stations = dict()
        self.station_distances = dict()

    def init_indicator_table(self, stations: list[str], version: str):
        """Initialize the indicator table, based on a set of stations.
        
        Args:
        - stations (list): List of unique stations in de timetable.
        - version (str): Version of the timetable data (example: 'v0')
        """
        self.indicator_table = pd.DataFrame(
            index=stations, 
            columns=stations,
            data=''
        )
        self.intermediate_stations = load_intermediate_stations(version)
        self.station_distances = load_distances()
        
    def update_indicator_table(self, timetable_row: pd.Series) -> None:
        """Update the indicator table based on a timetable row.
        Each cell contains a string, with a concatenations of train
        types letters ('S' for Sprinter, 'I' for Intercity).
        
        For intercity sections, we also indicate all intermediate stations
        on that section. Example: take the intercity from 'Ht' to 'Ehv', then
        we need to include 'Vg', 'Btl', 'Bet' and 'Ehs' as well.

        Args:
        - timetable_row (pd.Series): A row from the timetable DataFrame containing
            at least the 'Station', 'To', and 'Type' columns
        """
        from_station = timetable_row.name
        to_station = timetable_row['To']
        train_type = timetable_row['Type']

        # Convert to 'S' for Sprinter or 'I' for Intercity
        if train_type not in Settings.TYPE_CONVERSION:
            raise ValueError(f"Unknown train type: {train_type}")
        
        short_train_type = Settings.TYPE_CONVERSION[train_type]
        self.indicator_table.at[from_station, to_station] += short_train_type
        self.indicator_table.at[to_station, from_station] += short_train_type
        
        # Include all intermediate stations for an intercity as well
        if short_train_type == 'I':
            stations = self.intermediate_stations[from_station][to_station]
            
            # Go over each consecutive pair in the intermediate stations list
            for from_station, to_station in zip(stations[:-1], stations[1:]):
                self.indicator_table.at[from_station, to_station] += short_train_type
                self.indicator_table.at[to_station, from_station] += short_train_type
                
    def get_distance_counted(
            self,
            from_station: str,
            to_station: str,
            train_type: str,
            distance: float,
        ) -> float:
        """Get the number of kilometers that may be counted for this section.
        Depends on intermediate sections that have already been driven.
        See 'information/rules.py' for the exact rules.
        
        Args:
        - from_station (str): Starting station of the route
        - to_station (str): Destination station of the route
        - train_type (str): Type of train ('Spr' for Sprinter, 'Int' for Intercity)
        - distance (float): Distance between the two stations (in kilometers)
        
        Returns:
        - float: Number of kilometers that may be counted for this section
        """
        if train_type not in Settings.TYPE_CONVERSION:
            raise ValueError(f"Unknown train type: {train_type}")
        
        # Convert to 'S' for Sprinter or 'I' for Intercity
        short_train_type = Settings.TYPE_CONVERSION[train_type]
        
        # Keep track of how many kilometers may be counted for this section
        distance_counted = 0
        
        if short_train_type == 'S':  # No intermediate stations (by design)
            # Get string of train types that have already driven the current
            # section. Example: 'SSI' (two sprinters, one intercity)
            types_driven = self.indicator_table.at[from_station, to_station]
            
            if len(types_driven) < 2:  # May only count twice at most
                distance_counted += distance
        
        else:  # Intercity section with intermediate stations (by design)
            stations = self.intermediate_stations[from_station][to_station]

            # Go over each consecutive pair in the intermediate stations list
            for from_station, to_station in zip(stations[:-1], stations[1:]):
                types_driven = self.indicator_table.at[from_station, to_station]
                intermediate_distance = self.station_distances[from_station][to_station]
            
                # 'I' may only be counted once!
                if len(types_driven) == 1 and 'I' not in types_driven:
                    distance_counted += intermediate_distance
                elif len(types_driven) == 0:  # Section not driven at all yet
                    distance_counted += intermediate_distance

        return distance_counted
        
    def copy(self):
        """Create a copy of the RouteIndicator instance.

        Returns:
        - RouteIndicator: A new instance of RouteIndicator with a copied indicator table
        """
        new_indicator = RouteIndicator()
        new_indicator.stations = self.stations.copy()
        new_indicator.indicator_table = self.indicator_table.copy()
        new_indicator.intermediate_stations = self.intermediate_stations
        new_indicator.station_distances = self.station_distances
        return new_indicator


def main(): 
    """Main function to demonstrate the RouteIndicator functionality.
    
    Will get some random rows from the timetable and update the indicator table.
    """
    from ..data_processing.data_utils import read_timetable
    indicator = RouteIndicator()

    # Init version and corresponding timetable
    version = 'v0'
    timetable_df = read_timetable(version=version, processed=True)

    # Get unique stations and some random rides
    stations_list = timetable_df['Station'].unique()
    test_rides = timetable_df.sample(n=4)

    # Initialize the indicator table with the stations
    indicator.init_indicator_table(stations=stations_list, version=version)

    # Iteratively update the indicator table with the test rides
    for _, row in test_rides.iterrows():
        indicator.update_indicator_table(row)

    print(indicator.indicator_table)


if __name__ == "__main__":
    main()

