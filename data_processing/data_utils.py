import json
import pandas as pd
from pathlib import Path
from copy import deepcopy

from settings import Parameters, VersionSettings
SETTINGS = VersionSettings.get_version_settings()


def load_distances() -> dict[str, dict[str, float]]:
    """Load the distances dictionary from a JSON file.
    For the file's structure, see the find_intercity_distance.py file.

    Returns:
    - dict: Of all pairwise distances. Example (subset of full dict);
    {
        "Utm": {
            "Bhv": 6.2
        },
        "Bhv": {
            "Utm": 6.2,
            "Uto": 5.6,
            "Dld": 2.9
        }, ...
    }
    """
    with open(SETTINGS.PROCESSED_DISTANCES_PATH, mode='r') as f:
        return json.load(f)


def save_intermediate_stations(intermediate_stations: dict) -> None:
    """Save the intermediate stations dictionary to a JSON file.

    Args:
    - intermediate_stations (dict): Dictionary of intermediate stations
    {
        "Ht": {
            "Tb": ["Ht", "Tb"],
            "Ehv": ["Ht", "Vg", "Btl", "Bet", "Ehs", "Ehv"]
        }, ...
    }
    """
    file_path = SETTINGS.DATA_PATH
    file_name = SETTINGS.INTERMEDIATE_STATIONS_FILE

    with open(file_path / file_name, mode='w') as f:
        json.dump(intermediate_stations, f, indent=4)


def load_intermediate_stations() -> dict[str, dict[str, list[str]]]:
    """Reads in a dictionary from the given json file that
    includes all intermediate stations for any given intercity run.

    Args:
    - version (str): Version of the current run (example: 'v0')

    Returns:
    - dict: Of all intermediate station between pairwise intercity station
    {
        "Ht": {
            "Tb": ["Ht", "Tb"],
            "Ehv": ["Ht", "Vg", "Btl", "Bet", "Ehs", "Ehv"]
        }, ...
    }
    """
    file_path = SETTINGS.DATA_PATH
    file_name = SETTINGS.INTERMEDIATE_STATIONS_FILE

    with open(file_path / file_name, mode='r') as f:
        return json.load(f)


def read_csv_to_df(path_to_file: Path):
    """Reads a .csv file that assumes a standard structure to a df.

    Args:
    - path_to_file (Path): Complete path to a .csv file

    Returns:
    - pd.DataFrame: Containing (un/pre/_)processed timetable data.
    """
    return pd.read_csv(
        path_to_file,
        sep=',',
        header=0,
        index_col=False,
        keep_default_na=False,  # We do not want 'NA' to be Nan
    )


def save_df_to_csv(df: pd.DataFrame, path_to_file: Path):
    """Saved a df to a .csv file that asssumes a standard structure.

    Args:
    - df (pd.DataFrame): A Pandas DataFrame
    - path_to_file (Path): Complete path to the file location
    """
    df.to_csv(
        path_to_file,
        sep=',',
        index=False,
        index_label='Station',
        float_format='%.1f'  # Format distances and speeds to one decimal place
    )


def load_stations() -> pd.DataFrame:
    """Loads the official stations dataset, containing information
    station codes, full name, country and station type.

    Returns:
    - pd.DataFrame
    """
    all_stations = read_csv_to_df(
        path_to_file=SETTINGS.STATIONS_PATH
    )
    return all_stations


def read_timetable(
    processed: bool = True,
    timetable_path: Path = None,
    set_index: bool = True,
) -> pd.DataFrame:
    """Read the timetable CSV file into a pandas DataFrame. Interpret the
    'Departure' and 'Arrival' columns as datetime objects. (Format: '14:20')

    Args:
    - settings (VersionSettings): Contains settings based on the version
    - processed (bool): True if processed timetable required,
        False if unprocessed
    - timetable_path (Path, optional): Path to timetable file location
    - set_index (bool): Set the 'From' column as index if True

    Returns:
    - pd.DataFrame: DataFrame containing the timetable data
    """
    if timetable_path is None:
        data_path = SETTINGS.DATA_PATH
        if processed:
            timetable_path = data_path / SETTINGS.TIMETABLE_FILE_PROCESSED
        else:
            timetable_path = data_path / SETTINGS.TIMETABLE_FILE

    timetable_df = read_csv_to_df(path_to_file=timetable_path)

    for col in ['Departure', 'Arrival']:
        # Turn time columns to datetime
        timetable_df[col] = pd.to_datetime(
            timetable_df[col],
            format=SETTINGS.DATETIME_FORMAT,
        )

    # Sort on 'Departure' because we will filter on it often
    timetable_df.sort_values(by='Departure', inplace=True)

    if set_index:
        # If index, easier to filter on departure station
        timetable_df.set_index('Station', inplace=True)

    return timetable_df


def save_timetable(
    timetable_df: pd.DataFrame,
    timetable_path: Path | None = None,
    from_settings: bool = False
) -> None:
    """Save an (un)processed timetable to a CSV file.

    Args:
    - timetable_df (pd.DataFrame): DataFrame containing the
        processed timetable data
    - version (str): Version of the timetable data (example: 'v0')
    - timetable_path (Path): Path where to save the timetable
    """
    if from_settings:
        data_path = SETTINGS.DATA_PATH
        timetable_path = data_path / SETTINGS.TIMETABLE_FILE_PROCESSED

    save_df_to_csv(df=timetable_df, path_to_file=timetable_path)


def timestamp_to_int(
    current_timestamp: pd.Timestamp | str,
    from_epoch: bool = True,
    start_timestamp: pd.Timestamp | str | None = None,
) -> int:
    """Takes the difference of two timestamps and return it
    in minutes. With seconds as intermediate step.

    Args:
    - current_timestamp (pd.Timestamp | str): Datetime to subtract from,
        can be either a full Timestmap including day, or a time
        indication ('15:10'). If latter, transform to full timestamp
    - from_epoch (bool): Whether to count the epoch timestamp as
        start_timestamp, defaults to True. If False, start_timestamp is needed
    - start_timestamp (pd.Timestamp | str | None): Datatime to subtract,
        same as for end_time. Not necessary when from_epoch is True

    Returns:
    - int: Time difference in minutes
    """
    if isinstance(current_timestamp, str):
        current_timestamp = pd.Timestamp(
            f"{SETTINGS.DAY_OF_RUN} {current_timestamp}"
        )

    if from_epoch:
        start_timestamp = SETTINGS.EPOCH_TIMESTAMP
    elif isinstance(start_timestamp, str):
        start_timestamp = pd.Timestamp(
            f"{SETTINGS.DAY_OF_RUN} {start_timestamp}"
        )

    total_seconds = (current_timestamp - start_timestamp).total_seconds()
    total_minutes = int(total_seconds // 60)
    return total_minutes


def add_minutes_from_epoch(
    timetable_df: pd.DataFrame,
    datetime_col: str,
    new_col_name: str,
) -> pd.DataFrame:
    """Turns a datetime (e.g. '2025-08-02 14:23') into number of
    minutes since epoch (see settings.py; '1970-01-01 00:00').

    Args:
    - timetable_df (pd.DataFrame): DataFrame containing the timetable data
    - datetime_col (str): Name of the column containing the start time
    - new_col_name (str): Name of the newly calculated minutes column

    Returns:
    - pd.DataFrame: DataFrame with the new minutes-since column added
    """
    timetable_df[new_col_name] = timetable_df[datetime_col].apply(
        lambda datetime: timestamp_to_int(current_timestamp=datetime)
    )
    return timetable_df


def add_duration_in_minutes(
    timetable_df: pd.DataFrame,
    start_col: str,
    end_col: str,
    duration_col: str,
) -> pd.DataFrame:
    """Calculate the time difference in minutes between two datetime columns.

    Args:
    - timetable_df (pd.DataFrame): DataFrame containing the timetable data
    - start_col (str): Name of the column containing the start time
    - end_col (str): Name of the column containing the end time
    - duration_col (str): Name of the new column to store the
        duration in minutes

    Returns:
    - pd.DataFrame: DataFrame with the new duration column added
    """
    timetable_df[duration_col] = (
        timetable_df[end_col] - timetable_df[start_col]
    )
    return timetable_df


def int_to_timestamp(current_time: int) -> pd.Timestamp:
    """Convert an integer timestamp to a full pd.Timestamp.

    Args:
    - current_time (int): Timestamp integer from epoch, example 29235752

    Returns:
    - pd.Timestamp: Full timestamp, example pd.Timestamp('2025-08-02 14:32:00')
    """
    return SETTINGS.EPOCH_TIMESTAMP + pd.Timedelta(minutes=current_time)


def filter_timetable(
    timetable_df: pd.DataFrame,
    station: str,
    current_time: int,
    id_previous_train: int,
) -> pd.DataFrame:
    """Filter and sort the timetable based on station, time,
    and transfer conditions.

    Args:
    - timetable_df (pd.DataFrame): Timetable to filter and sort
    - station (str): The station to filter by
    - current_time (int): The current time to filter departures
    - end_time (int): The end time to filter arrivals
    - min_transfer_time (int): Minimum transfer time in minutes
    - max_transfer_time (int): Maximum transfer time in minutes
    - id_previous_train (int): ID of the last train to consider for transfers

    Returns:
    - pd.DataFrame: filtered and sorted timetable
    """
    # Calculate time window
    min_time = current_time + Parameters.MIN_TRANSFER_TIME
    max_time = current_time + Parameters.MAX_TRANSFER_TIME
    end_time_int = timestamp_to_int(Parameters.END_TIME, from_epoch=True)

    # First, filter on departures from our current station.
    # Then, either we are driving the same train with 0 minutes transer (or
    # slightly more, if trains stops for a while), or we are looking for
    # a new train between min_time and max_time, indicating margins in
    # which we look. Arrival time must be before we reach the end time.
    df_filtered = timetable_df[
        (timetable_df.index == station)
        & ((timetable_df['Departure_Int'] >= min_time)
            | ((timetable_df['Departure_Int'] >= current_time)
                & (timetable_df['ID'] == id_previous_train)))
        & (timetable_df['Departure_Int'] <= max_time)
        & (timetable_df['Arrival_Int'] <= end_time_int)
    ]

    df_copy = deepcopy(df_filtered)
    return df_copy
