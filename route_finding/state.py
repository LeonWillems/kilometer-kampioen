from logging import Logger

from .route_indicator import RouteIndicator
from data_processing.data_utils import (
    int_to_timestamp, timestamp_to_int,
)

from settings import Parameters, VersionSettings
SETTINGS = VersionSettings.get_version_settings()


class State:
    """Represents the state of the route finding process.

    Attributes:
    - total_distance (float): The total distance of the route
        (according to the Kilometer Kampioen rules)
    - route (list[pd.Series]): A list of pd.Series objects
        representing the route
    - route_indicator (RouteIndicator): An instance of RouteIndicator
    - current_time (int): The current time in the route finding process,
        usually the time of the last train arrival, in minutes after epoch
    - current_station (str): The station where the route finding is currently,
        usually the arrival station of the last train
    - id_previous_train (str): The ID of the last train used in the
        route finding
    - logger (Logger): Logger instance for logging information

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
        self.logger = None

    def set_initial_state(self, logger: Logger):
        """Sets the initial state with the current time and starting station.

        Args:
        - version (str): Version of the timetable data (example: 'v0')
        - current_time (str): The current time in the route finding process
        - current_station (str): The station where the route finding starts
        - logger (Logger): Logger instance for logging information
        """
        self.current_time = timestamp_to_int(
            current_timestamp=Parameters.START_TIME
        )
        self.current_station = Parameters.START_STATION
        self.route_indicator.init_indicator_table()
        self.logger = logger

        self.logger.info(
            "Starting new route finding run with parameters:\n"
            f"Current station: {self.current_station}\n"
            f"Current time: {int_to_timestamp(self.current_time)}\n"
        )

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
