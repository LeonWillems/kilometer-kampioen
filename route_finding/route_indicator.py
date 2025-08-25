import pandas as pd
from ..settings import Settings


class RouteIndicator:
    def __init__(self):
        """Initialize the RouteIndicator with a timetable.

        Attributes:
        - stations: Unique stations from the timetable
        - indicator_table: DataFrame to hold the route indicators between stations

        Methods
        - init_indicator_table: Initialize the indicator_table
        - update_indicator: Update the indicator table based on a timetable row
        - get_section_driven_by_type: Check if a section has been driven by a 
          specific train type
        - copy: Create a copy of the RouteIndicator instance
        """
        self.stations = list()
        self.indicator_table = pd.DataFrame()

    def init_indicator_table(self, stations: list[str]):
        """Initialize the indicator table, based on a set of stations.
        
        Args:
        - stations (list): List of unique stations in de timetable.
        """
        self.indicator_table = pd.DataFrame(
            index=stations, 
            columns=stations,
            data=''
        )

    def update_indicator_table(self, timetable_row: pd.Series) -> None:
        """Update the indicator table based on a timetable row.
        Each cell contains a string, with a concatenations of train
        types letters ('S' for Sprinter, 'I' for Intercity).

        Args:
        - timetable_row (pd.Series): A row from the timetable DataFrame containing
            at least the 'Station', 'To', and 'Type' columns
        """
        from_station = timetable_row['Station']
        to_station = timetable_row['To']
        train_type = timetable_row['Type']

        # Convert to 'S' for Sprinter or 'I' for Intercity
        if train_type not in Settings.TYPE_CONVERSION:
            raise ValueError(f"Unknown train type: {train_type}")
        
        short_train_type = Settings.TYPE_CONVERSION[train_type]
        self.indicator_table.at[from_station, to_station] += short_train_type
        self.indicator_table.at[to_station, from_station] += short_train_type

    def get_section_driven_by_type(
            self,
            from_station: str,
            to_station: str,
            train_type: str,
        ) -> int:
        """Get the section driven indicator for a specific route and train type.
        
        Args:
        - from_station (str): Starting station of the route
        - to_station (str): Destination station of the route
        - train_type (str): Type of train ('Spr' for Sprinter, 'Int' for Intercity)
        
        Returns:
        - int: 1 if the section has been driven with the specified train type, else 0
        """
        if train_type not in Settings.TYPE_CONVERSION:
            raise ValueError(f"Unknown train type: {train_type}")
        
        # Convert to 'S' for Sprinter or 'I' for Intercity
        short_train_type = Settings.TYPE_CONVERSION[train_type]

        if short_train_type in self.indicator_table.at[from_station, to_station]:
            return 1  # Section has been driven with the specified train type
        else:
            return 0  # Section has not been driven with the specified train type

    def copy(self):
        """Create a copy of the RouteIndicator instance.

        Returns:
        - RouteIndicator: A new instance of RouteIndicator with a copied indicator table
        """
        new_indicator = RouteIndicator()
        new_indicator.stations = self.stations.copy()
        new_indicator.indicator_table = self.indicator_table.copy()
        return new_indicator


def main(): 
    """Main function to demonstrate the RouteIndicator functionality.
    
    Will get some random rows from the timetable and update the indicator table.
    """
    from data_processing.timetable_utils import read_timetable
    indicator = RouteIndicator()

    # Init version and corresponding timetable
    version = 'v0'
    timetable_df = read_timetable(version=version, processed=True)

    # Get unique stations and some random rides
    stations_list = timetable_df['Station'].unique()
    test_rides = timetable_df.sample(n=12)

    # Initialize the indicator table with the stations
    indicator.init_indicator_table(stations=stations_list)

    # Iteratively update the indicator table with the test rides
    for _, row in test_rides.iterrows():
        indicator.update_indicator_table(row)

    print(indicator.indicator_table)


if __name__ == "__main__":
    main()

