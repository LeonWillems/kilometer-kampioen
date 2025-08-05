from route_finding.route_indicator import RouteIndicator


class State:
    """Represents the state of the route finding process.
    
    Attributes:
    - visited_stations (set): A set of stations that have been visited
    - total_distance (float): The total distance of the route
      (according to the Kilometer Kampioen rules)
    - route (list): A list of tuples representing the route
    - route_indicator (RouteIndicator): An instance of RouteIndicator
    - current_time (datetime): The current time in the route finding process,
      usually the time of the last train arrival
    - current_station (str): The station where the route finding is currently,
      usually the arrival station of the last train
    - id_last_train (str): The ID of the last train used in the route finding

    Methods:
    - set_initial_state(current_time, current_station): Sets the initial state
      with the current time and starting station
    - copy(): Returns a deep copy of the current state
    """
    def __init__(self):
        self.visited_stations = set()
        self.total_distance = 0
        self.route = []  # List of tuples
        self.route_indicator = RouteIndicator()
        self.current_time = None
        self.current_station = None
        self.id_last_train = None

    def set_initial_state(self, current_time, current_station):
        """Sets the initial state with the current time and starting station.

        Args:
        - current_time (datetime): The current time in the route finding process
        - current_station (str): The station where the route finding starts
        """
        self.current_time = current_time
        self.current_station = current_station

    def copy(self):
        """Returns a deep copy of the current state.

        Returns:
        - State: A new instance of State with the same attributes
        """
        new_state = State()
        new_state.visited_stations = self.visited_stations.copy()
        new_state.total_distance = self.total_distance
        new_state.route = self.route.copy()
        new_state.route_indicator = self.route_indicator.copy()
        new_state.current_time = self.current_time
        new_state.current_station = self.current_station
        new_state.id_last_train = self.id_last_train 
        return new_state
    
    