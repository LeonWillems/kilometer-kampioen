import re
import os
import unittest
from pathlib import Path
from datetime import datetime
import pandas as pd
from ..project.settings import Settings
from ..data_processing.timetable_utils import read_timetable


class TestRouteCompliance(unittest.TestCase):
    def setUp(self):
        """Set up test case with version-specific paths."""
        self.version = 'v0'
        self.logs_path = Settings.VERSIONED_LOGS_PATH[self.version]
        self.routes_path = Settings.VERSIONED_ROUTES_PATH[self.version]
        
        self.log_file_path = self._get_file_path(self.logs_path)
        self.route_file_path = self._get_file_path(self.routes_path)
        
        self.log = self._get_log_contents()
        self.route = self._get_route_contents()

    def _get_file_path(self, files_folder: Path):
        """Get name of the last file (most recent run) in a folder."""
        file_names = os.listdir(files_folder)
        self.assertNotEqual(len(file_names), 0)
        
        last_file_name = file_names[-1]
        return files_folder / last_file_name
    
    def _get_log_contents(self):
        """Read in the contents of the latest log file."""
        with open(self.log_file_path, 'r') as f:
            log_contents = f.read()
        return log_contents
    
    def _get_route_contents(self):
        """Read in the contents of the latest route file."""
        route_df = read_timetable(
            version=self.version,
            timetable_path=self.route_file_path,
            extra_timestamp_cols=['Current_Time']
        )
        return route_df

    def _get_start_time_from_log(self):
        """Extract the starting time from the log file."""
        # Find the end time line which indicates when the route finding started
        start_time_match = re.search(r'Current time: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', self.log)
        if not start_time_match:
            self.fail(f"Could not find start time in log file {self.log_file_path}")
            
        return datetime.strptime(start_time_match.group(1), '%Y-%m-%d %H:%M:%S')
    
    def verify_start_time(self):
        """Test that the start time in the route table (current time of first row)
        corresponds to the start time in the log."""
        
        # Get the start times from the log
        start_time_log = self._get_start_time_from_log()
        start_time_route = self.route.loc[0, 'Current_Time']

        # Check if first departure is after start time
        self.assertEqual(start_time_log, start_time_route)
        
        
if __name__ == '__main__':
    unittest.main()

