import pandas as pd

TIMETABLE_PATH = './data/mock_timetable_processed.csv'
TYPE_CONVERSION = {'Spr': 'S', 'Int': 'I'}


class RouteIndicator:
    def __init__(self, timetable_path: str | None = None):
        """Initialize the RouteIndicator with a timetable.

        Args:
        - timetable_path (str | None): Path to the timetable CSV file.
          If None, init empty path

        Attributes:
        - timetable: DataFrame containing the timetable data
        - stations: Unique stations from the timetable
        - indicator_table: DataFrame to hold the route indicators between stations

        Methods
        - update_indicator: Update the indicator table based on a timetable row
        - get_section_driven_by_type: Check if a section has been driven by a 
          specific train type
        - copy: Create a copy of the RouteIndicator instance
        """
        self.timetable = pd.read_csv(
            timetable_path if timetable_path else TIMETABLE_PATH,
            sep=';',
            header=0,
            index_col=False,
        )
        self.stations = self.timetable['Station'].unique()
        self.indicator_table = pd.DataFrame(
            index=self.stations, 
            columns=self.stations,
            data=''
        )

    def update_indicator(self, timetable_row: pd.Series):
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

        if train_type not in TYPE_CONVERSION:
            raise ValueError(f"Unknown train type: {train_type}")
        
        new_value = TYPE_CONVERSION[train_type]
        self.indicator_table.at[from_station, to_station] += new_value
        self.indicator_table.at[to_station, from_station] += new_value

    def get_section_driven_by_type(
            self,
            from_station: str,
            to_station: str,
            train_type: str
        ) -> int:
        """Get the section driven indicator for a specific route and train type.
        
        Args:
        - from_station (str): Starting station of the route
        - to_station (str): Destination station of the route
        - train_type (str): Type of train ('Spr' for Sprinter, 'Int' for Intercity)
        
        Returns:
        - int: 1 if the section has been driven with the specified train type, else 0
        """
        if train_type not in TYPE_CONVERSION:
            raise ValueError(f"Unknown train type: {train_type}")
        
        indicator_val = TYPE_CONVERSION[train_type]

        if indicator_val in self.indicator_table.at[from_station, to_station]:
            return 1  # Section has been driven with the specified train type
        else:
            return 0  # Section has not been driven with the specified train type

    def copy(self):
        """Create a copy of the RouteIndicator instance.

        Returns:
        - RouteIndicator: A new instance of RouteIndicator with a copied indicator table
        """
        new_indicator = RouteIndicator()
        new_indicator.indicator_table = self.indicator_table.copy()
        return new_indicator


def main(): 
    """Main function to demonstrate the RouteIndicator functionality.
    
    Will get some random rows from the timetable and update the indicator table.
    """
    indicator = RouteIndicator(TIMETABLE_PATH)
    
    test_rides = indicator.timetable.sample(n=12)
    print(test_rides)

    for _, row in test_rides.iterrows():
        indicator.update_indicator(row)

    print(indicator.indicator_table)


if __name__ == "__main__":
    main()

