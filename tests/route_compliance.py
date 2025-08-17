import unittest
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
from project.settings import Settings
import re


class TestRouteCompliance(unittest.TestCase):
    def setUp(self):
        """Set up test case with version-specific paths."""
        self.version = 'v0'
        self.routes_path = Settings.VERSIONED_ROUTES_PATH[self.version]
        self.logs_path = Settings.VERSIONED_LOGS_PATH[self.version]
        self.pairs = self._get_route_log_pairs()

    def _get_route_log_pairs(self):
        """Get pairs of corresponding route and log files."""
        route_files = os.listdir(self.routes_path)
        log_files = os.listdir(self.logs_path)
        
        # Group files by their timestamp prefix
        pairs = []
        for route_file in route_files:
            timestamp = route_file.split('_')[0:2]  # Get YYYYMMDD_HHMMSS parts
            matching_log = None
            
            for log_file in log_files:
                if all(part in log_file for part in timestamp):
                    matching_log = log_file
                    break
            
            if matching_log:
                pairs.append((
                    Path(self.routes_path, route_file),
                    Path(self.logs_path, matching_log)
                ))
        
        return pairs

    def _get_start_time_from_log(self, log_path):
        """Extract the starting time from the log file."""
        with open(log_path, 'r') as f:
            log_content = f.read()
            
        # Find the end time line which indicates when the route finding started
        end_time_match = re.search(r'Current time: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', log_content)
        if not end_time_match:
            self.fail(f"Could not find end time in log file {log_path}")
            
        return datetime.strptime(end_time_match.group(1), '%Y-%m-%d %H:%M:%S')

    def test_first_departure_after_start(self):
        """Test that the first departure in each route is after the start time in the log."""
        pairs = self.pairs
        self.assertTrue(pairs, "No matching route-log pairs found")
        
        for route_path, log_path in pairs:
            with self.subTest(route=route_path.name):
                # Get the start time from the log
                start_time = self._get_start_time_from_log(log_path)
                
                # Read the route CSV and get the first departure
                route_df = pd.read_csv(route_path, sep=';')
                first_departure = datetime.strptime(
                    route_df.iloc[0]['Departure'],
                    '%Y-%m-%d %H:%M:%S'
                )
                
                # Check if first departure is after start time
                self.assertLessEqual(
                    start_time,
                    first_departure,
                    f"First departure ({first_departure}) should be after or equal to "
                    f"start time ({start_time}) in {route_path.name}"
                )


if __name__ == '__main__':
    unittest.main()

