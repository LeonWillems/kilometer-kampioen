import re
import unittest
from datetime import datetime
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
        self.assertEqual(start_time_param, start_time_route)
        
        
if __name__ == '__main__':
    unittest.main()

