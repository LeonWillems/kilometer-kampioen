import sys
import pandas as pd
from pathlib import Path
from data_processing.data_utils import read_timetable, timestamp_to_int

from settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()


def find_stop_id(station: str, departure: str):
    try:
        station_cap: str = station.capitalize()
        departure_int: int = timestamp_to_int(departure)
        timetable_df: pd.DataFrame = read_timetable(processed=True)

    except Exception as e:
        print(f"Something went wrong: {e}")

    df_from_station = timetable_df[timetable_df['Station'] == station_cap]
    df_departure = df_from_station[
        df_from_station['Departure_Int'] == departure_int
    ].reset_index()

    if len(df_departure) == 0:
        print("Could not find a matching Stop_ID")

    else:
        print(
            f"Found {len(df_departure)} match(es) for given parameters.\n"
            f"Stop_IDs of matches: `{df_departure['Stop_ID'].to_list()}`"
        )


if __name__ == "__main__":
    runs_path: Path = SETTINGS.RUNS_PATH

    # The last `Stop_ID` value to use, continue from there (if so)
    # May include some time from which to continue as well (e.g. `12:30`)
    try:
        func_to_call: str = sys.argv[1]
        station: str = sys.argv[2]
        departure: str = sys.argv[3]

        match func_to_call:
            case 'find_stop_id':
                find_stop_id(station, departure)

    except Exception as e:
        print(f"Something went wrong: {e}")
