import unittest
from .test_utils import (
    get_log_contents, get_parms_contents, get_route_contents,
)
from ..data_processing.data_utils import timestamp_to_int
from ..settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()


class TestRouteCompliance(unittest.TestCase):
    def setUp(self):
        """Set up test case with version-specific paths."""
        self.log = get_log_contents()
        self.parms = get_parms_contents()
        self.route = get_route_contents()

    def test_start_time(self):
        """Test that the start time in the route table (current time of
        first row) corresponds to the start time in the log."""

        # Get the start times from the log
        start_time_param = timestamp_to_int(
            current_timestamp=self.parms['START_TIME'],
        )
        start_time_route = self.route.loc[0, 'Current_Time']

        # Check if first departure is after start time
        self.assertEqual(
            start_time_param, start_time_route,
            "Start time in route does not match start time in parameters."
        )

    def test_row_statistics(self):
        """Test statistics for each individual row in the route table."""
        start_time = timestamp_to_int(
            current_timestamp=self.parms['START_TIME']
        )
        end_time = timestamp_to_int(current_timestamp=self.parms['END_TIME'])

        for idx, row in self.route.iterrows():
            # Test non-negative values
            self.assertGreaterEqual(
                row['Distance_Counted'],
                0,
                f"Distance_Counted is negative at row {idx}"
            )
            self.assertGreaterEqual(
                row['Waiting_Time'],
                0,
                f"Waiting_Time is negative at row {idx}"
            )
            self.assertGreaterEqual(
                row['Score'],
                0,
                f"Score is negative at row {idx}"
            )

            # Convert string timestamps to datetime
            departure = row['Departure_Int']
            arrival = row['Arrival_Int']

            # Test time constraints
            self.assertLess(
                departure,
                arrival,
                f"Departure is not before Arrival at row {idx}"
            )
            self.assertGreaterEqual(
                departure,
                start_time,
                f"Departure is before `start_time` at row {idx}"
            )
            self.assertLessEqual(
                arrival,
                end_time,
                f"Arrival is after `end_time` at row {idx}"
            )

    def test_consecutive_trains(self):
        """Test statistics comparing current train with the next train
        in the sequence."""
        min_transfer = self.parms['MIN_TRANSFER_TIME']
        max_transfer = self.parms['MAX_TRANSFER_TIME']

        # Iterate through all rows except the last one
        for idx in range(len(self.route) - 1):
            current = self.route.iloc[idx]
            next_train = self.route.iloc[idx + 1]

            # Test station connectivity
            self.assertEqual(
                next_train['Station'],
                current['To'],
                f"Next Station doesn't match current To at row {idx}"
            )

            # Convert timestamps
            current_arrival = current['Arrival_Int']
            next_departure = next_train['Departure_Int']

            # Test transfer time constraints
            self.assertLessEqual(
                next_departure,
                current_arrival + max_transfer,
                f"Transfer time exceeds maximum at row {idx}"
            )

            if next_train['ID'] == current['ID']:
                # Same train, might continue immediately
                self.assertGreaterEqual(
                    next_departure,
                    current_arrival,
                    "Next departure is before current "
                    f"arrival for same train at row {idx}"
                )
            else:
                # Different train, should respect minimum transfer time
                self.assertGreaterEqual(
                    next_departure,
                    current_arrival + min_transfer,
                    "Transfer time is less than minimum "
                    f"for different trains at row {idx}"
                )


if __name__ == '__main__':
    unittest.main()
