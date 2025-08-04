from route_finding.route_indicator import RouteIndicator


class State:
    def __init__(self):
        self.visited_stations = set()
        self.total_distance = 0
        self.route = []  # List of tuples
        self.route_indicator = RouteIndicator()
        self.current_time = None
        self.current_station = None
        self.id_last_train = None

    def set_initial_state(self, current_time, current_station):
        self.current_time = current_time
        self.current_station = current_station

    def copy(self):
        new_state = State()
        new_state.visited_stations = self.visited_stations.copy()
        new_state.total_distance = self.total_distance
        new_state.route = self.route.copy()
        new_state.route_indicator = self.route_indicator.copy()
        new_state.current_time = self.current_time
        new_state.current_station = self.current_station
        new_state.id_last_train = self.id_last_train 
        return new_state
    
    