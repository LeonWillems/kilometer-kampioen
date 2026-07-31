import pandas as pd
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
    - id_previous_train (str): The Section_ID of the last train used in the
        route finding
    - logger (Logger): Logger instance for logging information

    Methods:
    - set_initial_state(current_time, current_station): Sets the initial state
        with the current time and starting station
    - copy(): Returns a deep copy of the current state
    """
    def __init__(self):
        self.total_distance: int = 0
        self.route: list[int] = []
        self.route_indicator: RouteIndicator = RouteIndicator()
        self.current_time: int = 0
        self.current_station: str = ''
        self.id_previous_train: int = 0
        self.logger: Logger = None
        self.score: int = 0
        self.got_stamp: bool = False

    def __lt__(self, other: "State"):
        """< comparison for min-heap purposes, see the explore_set algo.
        Note: in this case, a larger score for self returns True.
        """
        return -self.score < -other.score

    def set_initial_state(self, logger: Logger):
        """Sets the initial state with the current time and starting station.

        Args:
        - logger (Logger): Logger instance for logging information
        """
        self.current_time = timestamp_to_int(
            current_timestamp=Parameters.START_TIME
        )
        self.current_station = Parameters.START_STATION
        self.logger = logger

        self.logger.info(
            "Starting new route finding run with parameters:\n"
            f"Current station: {self.current_station}\n"
            f"Current time: {int_to_timestamp(self.current_time)}\n"
        )

        # If we do not need a stamp, just consider we already have it
        if not SETTINGS.STAMP.NEED_STAMP:
            self.got_stamp = True

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
        new_state.score = self.score
        new_state.got_stamp = self.got_stamp
        return new_state

    def _check_stamp(self, station: str, arrival_int: int):
        """Check at current stop for stamp"""
        if self.got_stamp:
            return True

        # Already handled at initialization, but just in case
        if not SETTINGS.STAMP.NEED_STAMP:
            return True

        # We can only get a stamp at the right station
        if station != SETTINGS.STAMP.STATION:
            return False

        # Check if arrival is within the time window. When leaving the train,
        # account for 5 minutes of getting the stamp in both the window,
        # and the current time (just add 5)
        if (
            timestamp_to_int(SETTINGS.STAMP.START_TIME)
            <= arrival_int
            <= timestamp_to_int(SETTINGS.STAMP.END_TIME) - 5
        ):
            self.current_time += 5
            return True

        # Correct station, but not within time window
        return False

    def update_state(self, row: pd.Series):
        """Updates the state given a new row, ergo a new ride.

        Args:
        - row (pd.Series): Row of a dataset
        """
        self.total_distance += row['Distance_Counted']
        self.route.append(row['Stop_ID'])
        self.route_indicator.update_indicator_table(row)
        self.current_time = row['Arrival_Int']
        self.current_station = row['To']
        self.id_previous_train = row['Section_ID']
        self.score = row['Score']
        self.got_stamp = self._check_stamp(row['To'], row['Arrival_Int'])

    def stamp_missed(self) -> bool:
        """Check if we missed the stamp; ergo we do not have it yet, and it is
        too late to get one.

        Returns:
        - bool: True is missed (then cancel searching), False if not
        """
        if self.got_stamp:
            return False

        if self.current_time > timestamp_to_int(SETTINGS.STAMP.END_TIME):
            return True

        return False
