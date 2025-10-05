import unittest
import pandas as pd
from .test_utils import (
    get_log_contents,
    get_parms_contents,
    get_route_contents,
)
from ..settings import Settings


class TestRouteCompliance(unittest.TestCase):
    def setUp(self):
        """Set up test case with version-specific paths."""
        self.version = 'v0'
        
        self.log = get_log_contents(self.version)
        self.parms = get_parms_contents(self.version)
        self.route = get_route_contents(self.version)
    
    def test_start_time(self):
        """Test that the start time in the route table (current time of first row)
        corresponds to the start time in the log."""
        
        # Get the start times from the log
        start_time_param = pd.Timestamp(f"{Settings.DAY_OF_RUN} {self.parms['start_time']}")
        start_time_route = self.route.loc[0, 'Current_Time']

        # Check if first departure is after start time
        self.assertEqual(start_time_param, start_time_route,
            "Start time in route does not match start time in parameters.")

    def test_row_statistics(self):
        """Test statistics for each individual row in the route table."""
        start_time = pd.Timestamp(f"{Settings.DAY_OF_RUN} {self.parms['start_time']}")
        end_time = pd.Timestamp(f"{Settings.DAY_OF_RUN} {self.parms['end_time']}")

        for idx, row in self.route.iterrows():
            # Test non-negative values
            self.assertGreaterEqual(row['Distance_Counted'], 0, 
                f"Distance_Counted is negative at row {idx}")
            self.assertGreaterEqual(row['Waiting_Time'], 0, 
                f"Waiting_Time is negative at row {idx}")
            self.assertGreaterEqual(row['Score'], 0, 
                f"Score is negative at row {idx}")
            
            # Convert string timestamps to datetime
            departure = pd.Timestamp(row['Departure'])
            arrival = pd.Timestamp(row['Arrival'])
            
            # Test time constraints
            self.assertLess(departure, arrival, 
                f"Departure is not before Arrival at row {idx}")
            self.assertGreaterEqual(departure, start_time, 
                f"Departure is before `start_time` at row {idx}")
            self.assertLessEqual(arrival, end_time, 
                f"Arrival is after `end_time` at row {idx}")

    def test_consecutive_trains(self):
        """Test statistics comparing current train with the next train in the sequence."""
        min_transfer = pd.Timedelta(minutes=self.parms['min_transfer_time'])
        max_transfer = pd.Timedelta(minutes=self.parms['max_transfer_time'])

        # Iterate through all rows except the last one
        for idx in range(len(self.route) - 1):
            current = self.route.iloc[idx]
            next_train = self.route.iloc[idx + 1]

            # Test station connectivity
            self.assertEqual(next_train['Station'], current['To'], 
                f"Next Station doesn't match current To at row {idx}")

            # Convert timestamps
            current_arrival = pd.Timestamp(current['Arrival'])
            next_departure = pd.Timestamp(next_train['Departure'])
            
            # Test transfer time constraints
            self.assertLessEqual(next_departure, current_arrival + max_transfer, 
                f"Transfer time exceeds maximum at row {idx}")

            if next_train['ID'] == current['ID']:
                # Same train, might continue immediately
                self.assertGreaterEqual(next_departure, current_arrival, 
                    f"Next departure is before current arrival for same train at row {idx}")
            else:
                # Different train, should respect minimum transfer time
                self.assertGreaterEqual(next_departure, current_arrival + min_transfer, 
                    f"Transfer time is less than minimum for different trains at row {idx}")

if __name__ == '__main__':
    unittest.main()

