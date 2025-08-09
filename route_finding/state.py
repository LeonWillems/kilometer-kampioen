from route_finding.route_indicator import RouteIndicator
from data_processing.timetable_utils import read_timetable
import pandas as pd


class State:
    """Represents the state of the route finding process.
    
    Attributes:
    - total_distance (float): The total distance of the route
        (according to the Kilometer Kampioen rules)
    - route (list[pd.Series]): A list of pd.Series objects representing the route
    - route_indicator (RouteIndicator): An instance of RouteIndicator
    - current_time (datetime): The current time in the route finding process,
        usually the time of the last train arrival
    - current_station (str): The station where the route finding is currently,
        usually the arrival station of the last train
    - id_previous_train (str): The ID of the last train used in the route finding

    Methods:
    - set_initial_state(current_time, current_station): Sets the initial state
        with the current time and starting station
    - copy(): Returns a deep copy of the current state
    """
    def __init__(self):
        self.total_distance = 0
        self.route = []
        self.route_indicator = RouteIndicator()
        self.current_time = None
        self.current_station = None
        self.id_previous_train = None

    def set_initial_state(
            self,
            version: str,
            current_time: pd.Timestamp,
            current_station: pd.Timestamp,
        ):
        """Sets the initial state with the current time and starting station.

        Args:
        - version (str): Version of the timetable data (example: 'v0')
        - current_time (datetime): The current time in the route finding process
        - current_station (str): The station where the route finding starts
        """
        timetable_df = read_timetable(version=version, processed=True)
        stations = timetable_df['Station'].unique()
        
        self.current_time = current_time
        self.current_station = current_station
        self.route_indicator.init_indicator_table(stations)

    def copy(self):
        """Returns a deep copy of the current state.

        Returns:
        - State: A new instance of State with the same attributes
        """
        new_state = State()
        new_state.total_distance = self.total_distance
        new_state.route = self.route.copy()
        new_state.route_indicator = self.route_indicator.copy()
        new_state.current_time = self.current_time
        new_state.current_station = self.current_station
        new_state.id_previous_train = self.id_previous_train 
        return new_state
    
    