import signal
import pandas as pd
from datetime import datetime

from .state import State
from .logger import setup_logger
from ..settings import Settings
from ..data_processing.data_utils import (
    read_timetable, save_timetable, add_duration_in_minutes, 
    filter_timetable, timestamp_to_int, int_to_timestamp
)

class GreedyDFS:
    """Greedy Depth-First Search for route finding.

    Args:
    - version (str): Version of the timetable data (example: 'v0')
    - end_time (str): The time by which the route must be completed
      - attr end_time (pd.Timestmap): Complete datatime
    - min_transfer_time (int): Minimum transfer time in minutes
    - max_transfer_time (int): Maximum transfer time in minutes

    Attributes:
    - timetable_df (pd.DataFrame): DataFrame containing the timetable data
    - best_state (State): The best state found during the search
    - best_distance (float): The best distance found during the search
    - routes_path (Path): Path to save the best routes found
    """
    def __init__(
            self,
            version: str,
            end_time: str,
            min_transfer_time: int,
            max_transfer_time: int,
            timestamp: datetime,
        ):
        self.version = version
        self.end_time = timestamp_to_int(current_timestamp=end_time)
        self.min_transfer_time = min_transfer_time
        self.max_transfer_time = max_transfer_time
        self.timestamp = timestamp

        self.timetable_df = read_timetable(version=version, processed=True)
        self.best_state = State()
        self.best_distance = 0
        self.iterations = 0

        # Path to save best routes found
        self.routes_path = \
            Settings.VERSIONED_ROUTES_PATH[self.version]

        # Setup interrupt handling
        signal.signal(signal.SIGINT, self._handle_interrupt)

        # Setup logger
        self.logger = setup_logger(version=self.version, timestamp=self.timestamp)
        self.logger.info(
            "Starting new route finding run with parameters:\n"
            f"Version: {version} ({Settings.VERSION_NAMES['v0']})\n"
            f"End time: {end_time}\n"
            f"Transfer time range: {min_transfer_time}-{max_transfer_time} minutes"
        )

    def _handle_interrupt(self, signum, frame):
        """Handle interrupt signal (Ctrl+C) by saving current best state."""
        self.logger.info("Interrupt received")
        self._save_best_route()
        exit(0)

    def _save_best_route(self):
        """Save the current best route as a .csv to the routes folder."""
        hms_driven = int(self.best_distance * 10)  # Convert to hectometers
        file_path = self.routes_path / f"{self.timestamp}_{hms_driven}.csv"

        # Construct custom df for the best found route
        best_route_df = pd.DataFrame(data=self.best_state.route)
        
        # Add the 'from station' index label as an extra column (leftmost)
        from_stations = [section.name for section in self.best_state.route]
        best_route_df.insert(0, 'Station', from_stations)

        # Save to designated folder (/routes/version/...)
        save_timetable(
            timetable_df=best_route_df,
            timetable_path=file_path
        )

        # Log statistics
        self.logger.info(
            f"Saved best route to: {file_path}\n"
            f"Number of transfers: {len(best_route_df)}\n"
            f"Final distance: {self.best_distance:.1f}km\n"
            f"Total iterations: {self.iterations}\n"
            f"End station: {self.best_state.current_station}\n"
            f"End time: {int_to_timestamp(self.best_state.current_time)}"
        )
        
    def _apply_score_function(
            self,
            transfer_options: pd.DataFrame,
            state: State,
        ) -> pd.DataFrame:
        """Applies a scoring function to the transfer options to prioritize them.

        Steps:
        1. Calculate waiting time (in minutes) for each transfer option
        2. Calculate the average speed of each option, including waiting time
        3. Sort options by score in descending order
        4. Add 'Section_Driven' for current train type as a column (1 or 0)
        5. Sort on 'Section_Driven' (ascending, 0 is good)
        6. Return the top 2 options

        Args:
        - transfer_options (pd.DataFrame): DataFrame containing transfer options
        - state (State): Current state of the route finding process

        Returns:
        - pd.DataFrame: Sorted transfer options based on the score
        """
        # 1. Calculate waiting time
        transfer_options['Current_Time'] = state.current_time
        
        transfer_options = add_duration_in_minutes(
            transfer_options,
            start_col='Current_Time',
            end_col='Departure_Int',
            duration_col='Waiting_Time',
        )
        
        # 2. Add 'Distance_Counted' as a number of how many kilometers may be
        #    counted for the current sections. See 'information/rules.py'
        transfer_options['Distance_Counted'] = transfer_options.apply(
            lambda row: state.route_indicator.get_distance_counted(
                from_station=row.name,
                to_station=row['To'],
                train_type=row['Type'],
                distance=row['Distance'],
            ),
            axis=1
        )

        # 3. Calculate score distance_counted/(waiting_time + travel_time)
        transfer_options['Score'] = (
            transfer_options['Distance_Counted']
            / (transfer_options['Waiting_Time'] + transfer_options['Duration'])
        )

        # 4. Sort by score (descending), higher is better
        transfer_options = transfer_options.sort_values(by='Score', ascending=False)

        # 5. Return the top 2 options. For now, we find that the code
        # runs for way too long if we don't limit the number of options.
        # This is because we exhaustively search all options.
        return transfer_options.head(2)

    def dfs(self, current_state: State):
        """Perform a greedy depth-first search to find the best route.

        Args:
        - current_state (State): The current state of the route finding process
        """
        self.iterations += 1

        # Log current state
        self.logger.debug(
            f"Iteration {self.iterations}\n"
            f"Current station: {current_state.current_station}\n"
            f"Time: {int_to_timestamp(current_state.current_time)}\n"
            f"Distance: {current_state.total_distance:.1f}km"
        )

        # 1. Get options from current position (station & time filtered)
        transfer_options = filter_timetable(
            timetable_df=self.timetable_df,
            station=current_state.current_station,
            current_time=current_state.current_time,
            end_time=self.end_time,
            min_transfer_time=self.min_transfer_time,
            max_transfer_time=self.max_transfer_time,
            id_previous_train=current_state.id_previous_train,
        )

        # 2. If no options are available, return
        if transfer_options.empty:
            self.logger.debug(f"No valid transfers found from {current_state.current_station}.")
            return
        
        self.logger.debug(f"Found {len(transfer_options)} transfer options.")

        # 3. Call score function to sort based on some priority
        top_transfers = self._apply_score_function(transfer_options, current_state)
        self.logger.debug(
            f"Top transfer option: {top_transfers.iloc[0].name} -> "
            f"{top_transfers.iloc[0]['To']} ({top_transfers.iloc[0]['Type']})"
        )

        # 4. Go over options
        for _, row in top_transfers.iterrows():
            # a. Create new state for this branch
            new_state = current_state.copy()
            
            # b. Update new state with this ride
            new_state.current_time = row['Arrival_Int']
            new_state.current_station = row['To']
            new_state.id_previous_train = row['ID']
            new_state.route_indicator.update_indicator_table(row)
            new_state.total_distance += row['Distance_Counted']
            new_state.route.append(row)

            # c. Update best state if better
            if new_state.total_distance > self.best_distance:
                self.logger.info(
                    f"New best route found! Distance: {new_state.total_distance:.1f}km"
                    f" (+{new_state.total_distance - self.best_distance:.1f}km)"
                )
                self.best_distance = new_state.total_distance
                self.best_state = new_state.copy()
            
            # d. Iterate recursively on newly found transfer
            self.dfs(new_state)
    

def run_greedy_dfs(prms: dict):
    """Main function to run the GreedyDFS route finding algorithm.
    
    Args:
    - prms (dict): Parameter settings to run algo, example;
        {'version': 'v0', 'start_station': 'Ht',
         'start_time': '12:00', 'end_time': '15:00',
         'min_transfer_time': 3, 'max_transfer_time': 15,
         'timestamp': datetime}
    """
    greedy_dfs = GreedyDFS(
        version=prms['version'],
        end_time=prms['end_time'],
        min_transfer_time=prms['min_transfer_time'],
        max_transfer_time=prms['max_transfer_time'],
        timestamp=prms['timestamp'],
    )

    initial_state = State()
    initial_state.set_initial_state(
        version=prms['version'],
        current_time=prms['start_time'],
        current_station=prms['start_station'],
        logger=greedy_dfs.logger,
    )

    greedy_dfs.dfs(initial_state)
    greedy_dfs._save_best_route()

