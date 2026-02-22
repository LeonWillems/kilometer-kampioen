import signal
import pandas as pd
from logging import Logger
from datetime import datetime
from queue import PriorityQueue

from .state import State
from .logger import setup_logger
from data_processing.data_utils import (
    read_timetable, save_timetable,
    add_duration_in_minutes,
    filter_timetable, int_to_timestamp,
    pre_filter_timetable
)

from settings import Parameters, VersionSettings
SETTINGS = VersionSettings.get_version_settings()


class ExploreSet:
    """A route finding algorithm that keeps a priority queue of states, ergo
    routes, from best to worst. Runs best, and adds consequent possible states/
    routes to the queue.

    Args:
    - timestamp (datetime): Current time when running the algorithm

    Attributes:
    - timetable_df (pd.DataFrame): DataFrame containing the timetable data
    - timetables (list[pd.DataFrame]): One timetable df for each 'Station'
    - best_state (State): The best state found during the search
    - best_distance (float): The best distance found during the search
    - iterations (int): Number of recursive dfs calls
    - priority_queue (PriorityQueue): Minheap with the best possible states/
        routes as the lowest values
    - logger (Logger): Used for logging purposes
    """
    def __init__(self, timestamp: datetime):
        self.timestamp = timestamp

        self.timetable_df: pd.DataFrame \
            = pre_filter_timetable(read_timetable(processed=True))

        # Create one timetable for each separate station, reducing the
        # filtering time per call
        stations = self.timetable_df['Station'].unique()

        self.timetables: dict[str, pd.DataFrame] = {
            station: self.timetable_df[self.timetable_df['Station'] == station]
            for station in stations
        }

        self.best_state: State = State()
        self.best_distance: float = 0
        self.iterations: int = 0

        # Will contain pairs: (-State.total_distance, State),
        # as it will be treated as a min-heap
        self.priority_queue = PriorityQueue()

        # Setup interrupt handling
        signal.signal(signal.SIGINT, self._handle_interrupt)

        # Setup logger
        self.logger: Logger = setup_logger(timestamp=self.timestamp)
        self.logger.info(
            "Starting new route finding run with parameters:\n"
            f"Version: {SETTINGS.VERSION} ({SETTINGS.VERSION_NAME})\n"
            f"End time: {Parameters.END_TIME}\n"
            f"Transfer time range: {Parameters.MIN_TRANSFER_TIME}"
            f"-{Parameters.MAX_TRANSFER_TIME} minutes"
        )

    def _handle_interrupt(self, signum, frame):
        """Handle interrupt signal (Ctrl+C) by saving current
        best state, and exiting the current run.
        """
        self.logger.info("Interrupt received")
        self._save_best_route()
        exit(0)

    def _save_best_route(self):
        """Save the current best route as a .csv to the routes folder."""
        hms_driven = int(self.best_distance * 10)  # Convert to hectometers
        file_path = SETTINGS.ROUTES_PATH / f"{self.timestamp}_{hms_driven}.csv"

        # Construct custom df for the best found route
        best_route_df = pd.DataFrame(data=self.best_state.route)

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
        """Applies a scoring function to the transfer options to
        prioritize them.

        Steps:
        1. Calculate waiting time (in minutes) for each transfer option
        2. Calculate the average speed of each option, including waiting time
        3. Sort options by score in descending order
        4. Add 'Section_Driven' for current train type as a column (1 or 0)
        5. Sort on 'Section_Driven' (ascending, 0 is good)
        6. Return the top 2 options

        Args:
        - transfer_options (pd.DataFrame): DataFrame containing
            transfer options
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
                from_station=row['Station'],
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
        transfer_options = transfer_options.sort_values(
            by='Score', ascending=False
        )

        # 5. Return the top 2 options. For now, we find that the code
        # runs for way too long if we don't limit the number of options.
        # This is because we exhaustively search all options.
        return transfer_options.head(2)

    def explore_state(self, current_state: State):
        """Explore the current state. Finds the top 2 best states and adds
        these to the priority queue.

        Args:
        - current_state (State): The current state of the route finding process
        """
        self.iterations += 1

        # TODO: log current state? Compare with v1, might not be necessary

        # 1. Get options from current position (station & time filtered)
        transfer_options = filter_timetable(
            timetable_df=self.timetables[current_state.current_station],
            current_time=current_state.current_time,
            id_previous_train=current_state.id_previous_train,
        )

        # 2. If no options are available, return
        if transfer_options.empty:
            self.logger.debug(
                "No valid transfers found from "
                f"{current_state.current_station}."
            )
            return

        self.logger.debug(f"Found {len(transfer_options)} transfer options.")

        # 3. Call score function to sort based on some priority
        top_transfers = self._apply_score_function(
            transfer_options, current_state
        )

        # 4. Go over options, add to the priority queue
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

            # Build a queue pair based on the score of interest. Current
            # version: min negative total distance (so max total distance)
            queue_pair = (-new_state.total_distance, new_state)
            self.priority_queue.put(queue_pair)

            # c. Update best state if better
            if new_state.total_distance > self.best_distance:
                self.logger.info(
                    "New best route found! Distance: "
                    f"{new_state.total_distance:.1f}km  (+"
                    f"{new_state.total_distance - self.best_distance:.1f}"
                    "km)"
                )
                self.best_distance = new_state.total_distance
                self.best_state = new_state.copy()


def run_explore_set(timestamp: datetime):
    """Main function to run the ExploreSet route finding algorithm.

    Args:
    - timestamp (datetime): Current time when running the algorithm
    """
    explore_set = ExploreSet(timestamp=timestamp)

    initial_state = State()
    initial_state.set_initial_state(logger=explore_set.logger)

    explore_set.explore_state(initial_state)

    while not explore_set.priority_queue.empty():
        best_state = explore_set.priority_queue.get()[1]
        explore_set.explore_state(best_state)

    explore_set._save_best_route()
