import pandas as pd


def read_timetable(timetable_path: str) -> pd.DataFrame:
    """Read the timetable CSV file into a pandas DataFrame. Interpret the 
    'Departure' and 'Arrival' columns as datetime objects. (Format: '14:20')"""
    timetable_df = pd.read_csv(
        timetable_path,
        sep=';',
        header=0,
        index_col=False,
    )

    for col in ['Departure', 'Arrival']:
        # Formatting is not needed, as Pandas will accurately
        # infer the format for our use case (tested)
        timetable_df[col] = pd.to_datetime(
            timetable_df[col]
        )

    return timetable_df


def save_timetable(
        processed_timetable: pd.DataFrame,
        processed_timetable_path: str
    ) -> None:
    """Save the processed timetable to a CSV file."""
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

    timetable_df[duration_col] = (
        (timetable_df[end_col] - timetable_df[start_col]) \
        .dt.total_seconds() / 60
    ).astype(int)

    return timetable_df

