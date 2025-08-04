
import pandas as pd
from data_processing.process_timetable import TimetableProcessor
from data_processing.data_utils import add_duration_in_minutes
from route_finding.state import State


class GreedyDFS:
    def __init__(
            self,
            end_time: pd.Timestamp,
            min_transfer_time: int,
            max_transfer_time: int
        ):
        self.end_time = end_time
        self.min_transfer_time = min_transfer_time
        self.max_transfer_time = max_transfer_time

        self.timetable_processor = TimetableProcessor(
            timetable_file="mock_timetable_processed.csv",
        )

        self.best_state = State()
        self.best_distance = 0

    def _apply_score_function(
            self,
            transfer_options: pd.DataFrame,
            state: State
        ) -> pd.DataFrame:
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
            transfer_options['Distance'] /
            (transfer_options['Waiting_Time'] + transfer_options['Duration'])
        )

        # 3. Sort by score (descending)
        transfer_options = transfer_options.sort_values(by='Score', ascending=False)

        # TODO: delete after testing
        transfer_options = transfer_options.head(2)

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

        return transfer_options

    def dfs(self, current_state: State):
        # 1. Get options from current position (station & time filtered)
        transfer_options = self.timetable_processor.filter_and_sort(
            station=current_state.current_station,
            current_time=current_state.current_time,
            end_time=self.end_time,
            min_transfer_time=self.min_transfer_time,
            max_transfer_time=self.max_transfer_time,
            id_last_train=current_state.id_last_train
        )

        # 2. If no options are available, return
        if transfer_options.empty:
            return

        # 3. Call score function to sort based on some priority
        transfer_options = self._apply_score_function(transfer_options, current_state)

        # 4. Go over options
        for _, row in transfer_options.iterrows():
            # a. Create new state for this branch
            new_state = current_state.copy()
            
            # b. Update new state with this ride
            new_state.current_time = row['Arrival']
            new_state.current_station = row['To']
            new_state.id_last_train = row['ID']
            new_state.route_indicator.update_indicator(row)

            # Only add distance if the section has not been driven yet by train type
            if row['Section_Driven'] == 0:
                new_state.total_distance += row['Distance']

            columns_to_keep = ['ID', 'Station', 'To', 'Departure', 'Arrival', 'Distance', 'Type']
            new_state.route.append(row[columns_to_keep].tolist())

            # c. Update best state if better
            if new_state.total_distance > self.best_distance:
                self.best_distance = new_state.total_distance
                self.best_state = new_state.copy()
            
            # d. Iterate recursively on newly found transfer
            self.dfs(new_state)
    

def main():
    greedy_dfs = GreedyDFS(
        end_time=pd.Timestamp('15:00'),
        min_transfer_time=3,
        max_transfer_time=15,
    )

    initial_state = State()
    initial_state.set_initial_state(
        current_time = pd.Timestamp('12:00'),
        current_station = 'Ht'
    )

    greedy_dfs.dfs(initial_state)

    print()
    print("Best State Found:")
    print(f"Total Distance: {greedy_dfs.best_state.total_distance}")
    print()
    print(f"Indicator Table:\n{greedy_dfs.best_state.route_indicator.indicator_table}")
    print()
    print("Route:")
    for row in greedy_dfs.best_state.route:
        print(row)


if __name__ == "__main__":
    main()

