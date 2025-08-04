import pandas as pd


def read_timetable(timetable_path: str) -> pd.DataFrame:
    """Read the timetable CSV file into a pandas DataFrame. Interpret the 
    'Departure' and 'Arrival' columns as datetime objects. (Format: '14:20')
    
    Args:
    - timetable_path (str): Full path to the timetable CSV file

    Returns:
    - pd.DataFrame: DataFrame containing the timetable data
    
    TODO Vnext: Change to pathlib.Path for better path handling.
    """
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


def save_timetable(
        processed_timetable: pd.DataFrame,
        processed_timetable_path: str
    ) -> None:
    """Save the processed timetable to a CSV file.
    
    Args:
    - processed_timetable (pd.DataFrame): DataFrame containing the processed timetable data
    - processed_timetable_path (str): Full path where the processed timetable will be saved
    
    TODO Vnext: Change to pathlib.Path for better path handling.
    """
    processed_timetable.to_csv(
        processed_timetable_path,
        sep=';',
        index=False,
        float_format='%.1f'  # Format distances and speeds to one decimal place
    )


def add_duration_in_minutes(
        timetable_df: pd.DataFrame,
        start_col: str,
        end_col: str,
        duration_col: str
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

