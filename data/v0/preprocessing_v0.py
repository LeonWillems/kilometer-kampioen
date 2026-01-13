import pandas as pd

from ...data_processing.data_utils import read_csv_to_df, save_timetable
from ...settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()


def add_day_of_run(df: pd.DataFrame, cols: list[str]):
    """Adds the day of the v0 run to a list of time columns.
    Assumes that these columns are of the form '12:45' (str),
    then adds the day, resulting in example: '2025-10-02 12:45'

    Args:
    - df (pd.DataFrame): Pandas DataFrame containing timetable data
    - cols (list[str]): List of columns names to be extended,
        example ['Arrival', 'Departure']
    """
    for col in cols:
        df[col] = \
            df[col].apply(lambda x: f"{SETTINGS.DAY_OF_RUN} {x}")

    return df


def preprocess():
    """Function to preprocess the v0 raw data file. For this version,
    we only need to add the day of the v0 run to arrival and departure
    columns. Then, it's ready to be processed further for the analysis.

    Steps: read .csv, add day of run, save to .csv again
    """
    raw_file_name = 'timetable_raw.csv'
    path_fo_raw_file = SETTINGS.DATA_PATH / raw_file_name
    path_to_timetable = SETTINGS.DATA_PATH / SETTINGS.TIMETABLE_FILE

    raw_df = read_csv_to_df(path_to_file=path_fo_raw_file)

    day_of_run_df = add_day_of_run(
        df=raw_df,
        cols=['Departure', 'Arrival'],
    )

    save_timetable(
        timetable_df=day_of_run_df,
        timetable_path=path_to_timetable,
    )
