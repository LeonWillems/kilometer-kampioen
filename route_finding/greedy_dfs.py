import signal
import pandas as pd
from datetime import datetime

from .state import State
from .logger import setup_logger
from ..project.settings import Settings
from ..data_processing.timetable_utils import (
    read_timetable,
    save_timetable,
    add_duration_in_minutes, 
    filter_and_sort_timetable,
)

class GreedyDFS:
    """Greedy Depth-First Search for route finding.

    Args:
    - version (str): Version of the timetable data (example: 'v0')
    - end_time (pd.Timestamp): The time by which the route must be completed
    - min_transfer_time (int): Minimum transfer time in minutes
    - max_transfer_time (int): Maximum transfer time in minutes

    Attributes:
    - timetable_df (pd.DataFrame): DataFrame containing the timetable data
    - best_state (State): The best state found during the search
    - best_distance (float): The best distance found during the search
    - results_header (list[str]): Header for the results DataFrame
    - routes_path (Path): Path to save the best routes found
    """
    def __init__(
            self,
            version: str,
            end_time: pd.Timestamp,
            min_transfer_time: int,
            max_transfer_time: int,
        ):
        self.version = version
        self.end_time = end_time
        self.min_transfer_time = min_transfer_time
        self.max_transfer_time = max_transfer_time

        self.timetable_df = read_timetable(version=version, processed=True)
        self.best_state = State()
        self.best_distance = 0
        self.results_header = None
        self.iterations = 0

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

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

        # Construct custom df with extra columns
        best_route_df = pd.DataFrame(
            data=self.best_state.route, 
            columns=self.results_header
        )

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
            f"End station: {self.best_state.current_station}"
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
            end_col='Departure',
            duration_col='Waiting_Time'
        )

        # 2. Calculate score distance/(waiting_time + travel_time)
        transfer_options['Score'] = (
            transfer_options['Distance']
            / (transfer_options['Waiting_Time'] + transfer_options['Duration'])
        )

        # 3. Sort by score (descending)
        transfer_options = transfer_options.sort_values(by='Score', ascending=False)

        # 4. Add 'Section_Driven' for current train type as column
        transfer_options['Section_Driven'] = transfer_options.apply(
            lambda row: state.route_indicator.get_section_driven_by_type(
                from_station=row['Station'],
                to_station=row['To'],
                train_type=row['Type']
            ),
            axis=1
        )

        # 5. Sort on 'Section_Driven' (ascending, 0 is good)
        transfer_options = transfer_options.sort_values(by='Section_Driven', ascending=True)

        # 6. Return the top 2 options. For now, we find that the code
        # runs for way too long if we don't limit the number of options.
        # This is because we exhaustively search all options.
        return transfer_options.head(2)

    def dfs(self, current_state: State):
        """Perform a greedy depth-first search to find the best route.
        TODO V0.2: Add pseudocode and an explanation of the algorithm.

        Args:
        - current_state (State): The current state of the route finding process
        """
        self.iterations += 1

        # Log current state
        self.logger.debug(
            f"Iteration {self.iterations}\n"
            f"Current station: {current_state.current_station}\n"
            f"Time: {current_state.current_time}\n"
            f"Distance: {current_state.total_distance:.1f}km"
        )

        # 1. Get options from current position (station & time filtered)
        transfer_options = filter_and_sort_timetable(
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
        transfer_options = self._apply_score_function(transfer_options, current_state)
        self.logger.debug(
            f"Top transfer option: {transfer_options.iloc[0]['Station']} -> "
            f"{transfer_options.iloc[0]['To']} ({transfer_options.iloc[0]['Type']})"
        )

        # 4. Go over options
        for _, row in transfer_options.iterrows():
            # a. Create new state for this branch
            new_state = current_state.copy()
            
            # b. Update new state with this ride
            new_state.current_time = row['Arrival']
            new_state.current_station = row['To']
            new_state.id_previous_train = row['ID']
            new_state.route_indicator.update_indicator_table(row)

            # Only add distance if the section has not been driven yet by train type
            # TODO Vsome_day: Enforce the actual Kilometer Kampioen rule, current one is shit
            if row['Section_Driven'] == 0:
                new_state.total_distance += row['Distance']

            # TODO Vsome_day: Find a cleaner way to get all columns headers, including added ones
            if self.results_header is None:
                self.results_header = row.index

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
    

def main():
    """Main function to run the GreedyDFS route finding algorithm.
    
    TODO V0.1: Save final route to some file
    """
    version = 'v0'

    greedy_dfs = GreedyDFS(
        version=version,
        end_time=pd.Timestamp('15:00'),
        min_transfer_time=3,
        max_transfer_time=15,
    )

    initial_state = State()
    initial_state.set_initial_state(
        version=version,
        current_time=pd.Timestamp('12:00'),
        current_station='Ht',
        logger=greedy_dfs.logger
    )

    greedy_dfs.dfs(initial_state)
    greedy_dfs._save_best_route()


if __name__ == "__main__":
    main()

