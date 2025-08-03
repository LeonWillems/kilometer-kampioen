# TODO: Read in mock_timetable.csv, and create a table with
# the set of stations as both the index and columns.
# All values are initially set to None. If a sprinter
# drive from station A to station B, then the value at
# (x, y) is set to 'S'. For an intercity, 'I'. If both
# types have driven, then concatenate the strings.
# In theory, you can drive from A to B multiple times,
# even with the same type. All will be written as a class.

import pandas as pd

TIMETABLE_PATH = './data/mock_timetable_processed.csv'
TYPE_CONVERSION = {'Spr': 'S', 'Int': 'I'}


class RouteIndicator:
    def __init__(self, timetable_path: str | None = None):
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

    def update_indicator(self, timetable_row):
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
        """Get the section driven indicator for a specific route and train type."""
        if train_type not in TYPE_CONVERSION:
            raise ValueError(f"Unknown train type: {train_type}")
        
        indicator_val = TYPE_CONVERSION[train_type]

        if indicator_val in self.indicator_table.at[from_station, to_station]:
            return 1  # Section has been driven with the specified train type
        else:
            return 0  # Section has not been driven with the specified train type

    def copy(self):
        new_indicator = RouteIndicator()
        new_indicator.indicator_table = self.indicator_table.copy()
        return new_indicator

def main(): 
    indicator = RouteIndicator(TIMETABLE_PATH)
    
    test_rides = indicator.timetable.sample(n=12)
    print(test_rides)

    for _, row in test_rides.iterrows():
        indicator.update_indicator(row)

    print(indicator.indicator_table)


if __name__ == "__main__":
    main()

