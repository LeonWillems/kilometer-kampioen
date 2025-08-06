import pandas as pd
from copy import deepcopy
from project.settings import Settings


def read_timetable(version: str, processed: bool) -> pd.DataFrame:
    """Read the timetable CSV file into a pandas DataFrame. Interpret the 
    'Departure' and 'Arrival' columns as datetime objects. (Format: '14:20')
    
    Args:
    - version (str): Version of the timetable data (example: 'v0')
    - processed (bool): True if processed timetable required,
        False if unprocessed

    Returns:
    - pd.DataFrame: DataFrame containing the timetable data
    """
    data_path = Settings.VERSIONED_DATA_PATHS[version]
    if processed:
        timetable_path = data_path / Settings.TIMETABLE_FILE_PROCESSED
    else:
        timetable_path = data_path / Settings.TIMETABLE_FILE

    timetable_df = pd.read_csv(
        timetable_path,
        sep=';',
        header=0,
        index_col=False,
    )

    for col in ['Departure', 'Arrival']:
        # Formatting is not needed, as Pandas will accurately
        # infer the format for our use case (tested)
        # TODO Vnext: sanity check on format for data from NS
        timetable_df[col] = pd.to_datetime(
            timetable_df[col]
        )

    return timetable_df


def save_timetable(timetable_df: pd.DataFrame, version: str) -> None:
    """Save the processed timetable to a CSV file.
    
    Args:
    - timetable_df (pd.DataFrame): DataFrame containing the processed timetable data
    - version (str): Version of the timetable data (example: 'v0')
    """
    data_path = Settings.VERSIONED_DATA_PATHS[version]
    timetable_path = data_path / Settings.TIMETABLE_FILE_PROCESSED

    timetable_df.to_csv(
        timetable_path,
        sep=';',
        index=False,
        float_format='%.1f'  # Format distances and speeds to one decimal place
    )


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
    - duration_col (str): Name of the new column to store the duration in minutes
    
    Returns:
    - pd.DataFrame: DataFrame with the new duration column added
    """
    timetable_df[duration_col] = (
        (timetable_df[end_col] - timetable_df[start_col]) \
        .dt.total_seconds() / 60
    ).astype(int)

    return timetable_df


def filter_and_sort_timetable(
        timetable_df: pd.DataFrame,
        station: str, 
        current_time: pd.Timestamp,
        end_time: pd.Timestamp,
        min_transfer_time: int,
        max_transfer_time: int,
        id_last_train: int,
    ) -> pd.DataFrame:
    """Filter and sort the timetable based on station, time, and transfer conditions.

    Args:
    - timetable_df (pd.DataFrame): Timetable to filter and sort
    - station (str): The station to filter by
    - current_time (pd.Timestamp): The current time to filter departures
    - end_time (pd.Timestamp): The end time to filter arrivals
    - min_transfer_time (int): Minimum transfer time in minutes
    - max_transfer_time (int): Maximum transfer time in minutes
    - id_last_train (int): ID of the last train to consider for transfers

    Returns:
    - pd.DataFrame: filtered and sorted timetable
    """
    df_copy = deepcopy(timetable_df)

    # Filter on departures from our current station
    df_station = df_copy[df_copy['Station'] == station]

    # Calculate time window
    min_time = current_time + pd.Timedelta(minutes=min_transfer_time)
    max_time = current_time + pd.Timedelta(minutes=max_transfer_time)

    # Either we are driving the same train with 0 minutes transer (or
    # slightly more, if trains stops for a while), or we are looking for
    # a new train between min_time and max_time, indicating margins in 
    # which we look. Arrival time must be before we reach the end time.
    df_time = df_station[
        ((df_station['Departure'] >= min_time) \
            | ((df_station['Departure'] >= current_time) \
                & (df_station['ID'] == id_last_train))) \
        & (df_station['Departure'] <= max_time) \
        & (df_station['Arrival'] <= end_time)
    ]

    # Sort by 'Departure'
    df_time_sorted = df_time.sort_values(by='Departure')
    return df_time_sorted

