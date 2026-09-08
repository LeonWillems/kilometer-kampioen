import sys
import json
import pandas as pd
from time import time
from pathlib import Path
from datetime import datetime
from dataclasses import asdict
from data_processing.data_utils import read_timetable, timestamp_to_int

from settings import Parameters, VersionSettings
SETTINGS = VersionSettings.get_version_settings()


def _read_last_run_df(runs_path: Path) -> pd.DataFrame:
    """In case of continue from save: we need to find the last run. This is the
    CSV file in the last folder for the current version (in runs). Find it,
    and build a pd.DataFrame.

    Args:
    - runs_path (Path): Path with all the runs for some version

    Returns:
    - pd.DataFrame: Last run's route
    """
    # Find all runs for given version, keep the last one
    run_paths = [path for path in runs_path.iterdir() if path.is_dir()]
    run_path = run_paths[-1]

    # Check path for only CSV files, then keep the first (and only) one
    csv_files = [
        path for path in run_path.iterdir() if
        path.is_file() and path.suffix == '.csv'
    ]
    csv_file_path = csv_files[0]

    return read_timetable(processed=True, timetable_path=csv_file_path)


def _get_route_so_far(route_df: pd.DataFrame, stop_id: int) -> pd.DataFrame:
    """Given the complete last run route, only keep those until (and including)
    the row with a given `Stop_ID`.

    Args:
    - route_df (pd.DataFrame): Complete route from last run
    - stop_id (int): `Stop_ID` of the last row to include, continue from there

    Returns:
    - pd.DataFrame: Route, but until (and including) the row for stop_id
    """
    stop_id_row = route_df[route_df['Stop_ID'] == stop_id]
    stop_id_row_index = stop_id_row.index[0]
    route_df_until_stop = route_df[:stop_id_row_index+1]
    return route_df_until_stop


def _run_algo(
    run_path: Path,
    route_df: pd.DataFrame | None = None,
    time_int: int | None = None,
) -> None:
    """Calls the right path finding algorithm based on the version.

    Args:
    - run_path (Path): Path in which to store files for current run
    - route_df (pd.DataFrame, optional): If continue from save, contains route
        done so far, continue from last stop
    """
    match SETTINGS.VERSION:
        case 'v0' | 'v1' if route_df is not None:
            print("Run from save only available from v2 onwards")

        case 'v0' | 'v1' if route_df is None:
            from route_finding.archive.v0v1_greedy_dfs \
                import run_greedy_dfs
            run_greedy_dfs(run_path)

        case 'v2':
            from route_finding.archive.v2_explore_set import run_explore_set
            run_explore_set(run_path, route_df, time_int)

        case 'v3':
            from route_finding.v3_explore_set import run_explore_set
            run_explore_set(run_path, route_df, time_int)


if __name__ == "__main__":
    runs_path: Path = SETTINGS.RUNS_PATH
    stop_id = None
    current_time_int = None

    # The last `Stop_ID` value to use, continue from there (if so)
    # May include some time from which to continue as well (e.g. `12:30`)
    try:
        stop_id = int(sys.argv[1])
        print(f"Continuing last route from stop `{stop_id}`.")

        if len(sys.argv) > 2:
            current_time: str = sys.argv[2]
            current_time_int: int = timestamp_to_int(current_time)
            print(f"Continuing with current time `{current_time}`")

        continue_from_save = True

        last_run_df = _read_last_run_df(runs_path)
        df_until_stop = _get_route_so_far(last_run_df, stop_id)

    except Exception as e:
        print(f"Debug: {e}")
        print("Running new route finder")
        continue_from_save = False

    time_start = time()
    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create path for new run
    current_run_path: Path = runs_path / timestamp
    current_run_path.mkdir(exist_ok=True)

    # Copy the given Parameters (from `settings.py`)
    params_dict = asdict(Parameters())
    params_dict['TIMESTAMP'] = timestamp

    json_file_path = (current_run_path / 'parameters').with_suffix('.json')
    with open(json_file_path, 'w') as f:
        json.dump(params_dict, f)

    # If a Stop_ID has been provided, continue from there
    if continue_from_save and stop_id is not None:
        _run_algo(current_run_path, df_until_stop, current_time_int)

    else:
        _run_algo(current_run_path)

    time_end = time()
    print(f"That shit took {time_end - time_start:.2f} seconds.")
