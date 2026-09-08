import pandas as pd

from data_processing.data_utils import (
    read_csv_to_df, save_timetable, load_stations
)
from settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()

COLUMNS_OF_INTEREST = [
    'Stop:Station code', 'Stop:RDT-ID',
    'Stop:Arrival time', 'Stop:Arrival delay',
    'Stop:Departure time', 'Stop:Departure delay',
    'Service:Type', 'Service:RDT-ID',
]

ACCEPTED_TRAIN_TYPES = [
    'Intercity', 'Snelbus ipv trein', 'Sprinter', 'Sneltrein',
    'Stoptrein', 'Stopbus ipv trein', 'Intercity direct', 'Nachttrein'
]

TRAIN_TYPE_MAPPING = {
    'Intercity': 'Int',
    'Snelbus ipv trein': 'Int',
    'Sprinter': 'Spr',
    'Sneltrein': 'Spr',
    'Stoptrein': 'Spr',
    'Stopbus ipv trein': 'Spr',
    'Intercity direct': 'Int',
    'Nachttrein': 'Int',
}

ACCEPTED_COMPANIES = [
    'NS', 'R-net Qb', 'RRReis A', 'R-net NS', 'Arriva',
    'RRReis K', 'Blauwnet A', 'Blauwnet K', 'R-net Qbuz'
]


def keep_dutch_stations(timetable_df: pd.DataFrame) -> pd.DataFrame:
    """Throws away any international stops, only keep Dutch stations.

    Args:
    - timetable_df (pd.DataFrame): Timetable data

    Returns:
    - pd.DataFrame: Same table, but with international rows removed
    """
    stations = load_stations()
    dutch_stations = stations[stations['country'] == 'NL']
    dutch_codes = dutch_stations['code'].to_list()

    # Return only rows where the station code is Dutch
    return timetable_df[timetable_df['Stop:Station code'].isin(dutch_codes)]


def clean_data(timetable_df: pd.DataFrame) -> pd.DataFrame:
    """Cleans the raw data in four steps:
    1. Filter on relevant day
    2. Keep only accepted train types
    3. Keep only Dutch railway stations
    4. Keep only accepted rail operators
    5. Keep only columns of interest

    Args:
    - timetable_df (pd.DataFrame): Timetable data

    Returns:
    - pd.DataFrame: Same table, but cleaned
    """
    # 1. Only keep the relevant day
    df_filtered_day = timetable_df[
        timetable_df['Service:Date'] == SETTINGS.DAY_OF_RUN
    ]

    # 2. Keep train types that are accepted,
    #    to prevent taking a nighttrain, for example
    df_filtered_train_types = df_filtered_day[
        df_filtered_day['Service:Type'].isin(ACCEPTED_TRAIN_TYPES)
    ]

    # 3. Delete rows with international station codes, only keep NL
    df_only_dutch_stations = keep_dutch_stations(df_filtered_train_types)

    # 4. Keep only rows driven by one of the accepted companies
    df_accepted_companies = df_only_dutch_stations[
        df_only_dutch_stations['Service:Company'].isin(ACCEPTED_COMPANIES)
    ]

    # 5. Drop unnecessary columns
    df_filtered_cols = df_accepted_companies[COLUMNS_OF_INTEREST]

    return df_filtered_cols


def process_datetime(datetime: str, delay: str) -> pd.DatetimeIndex:
    """Process the dataset's datetime for our purposes.
    1. Turn to pd.Datetime object given the right format
    2. If so: apply delay

    Args:
    - datetime (str): Raw datetime string, e.g. '2026-07-22T12:22:00+02:00'
    - delay (str): Raw delay string, examples are '' and '4'

    Returns:
    - pd.Datetime: Pandas datetime object, possible delay accounted for
    """
    pd_datetime = pd.to_datetime(
        datetime,
        format=SETTINGS.DATETIME_FORMAT,
    )

    # Delay could be an empty string, which means no delay
    if delay.isdigit():
        delay_int = int(delay)
        pd_datetime -= pd.Timedelta(minutes=delay_int)

    return pd_datetime


def structure_data(timetable_df: pd.DataFrame) -> pd.DataFrame:
    """Restructure the data. Before: each line represents a stop at a station,
    with train data, station, arrival & departue et cetera. After: each line
    represents a section from one station to another (between two stops).

    An example; columns and data shortened for brevity. Before:
    RDT-ID  Type    Code    Arrive  Depart
    8634	Int     RTD		        12:02
    8634	Int     DT      12:14	12:14

    After:
    Station To      Depart  Arrive  Type    ID
    RTD     DT      12:02   14:14   Int     8634

    Args:
    - timetable_df (pd.DataFrame): Timetable data, one stop per row

    Returns:
    - pd.DataFrame: Same table, but one connection per row
    """
    section_ids: pd.DataFrame = timetable_df['Service:RDT-ID'].unique()

    new_df_lines = []
    new_columns = [
        'Station', 'To', 'Departure', 'Arrival',
        'Type', 'Section_ID', 'Stop_ID'
    ]

    # Go over each section ID, representing one whole section from first to
    # last station for one specific train. The ID is unique for train & section
    for section_id in section_ids:
        section_rows = timetable_df[
            timetable_df['Service:RDT-ID'] == section_id
        ]
        section_rows.reset_index(inplace=True)

        service_type = section_rows.loc[0, 'Service:Type']
        mapped_train_type = TRAIN_TYPE_MAPPING[service_type]

        # Turn each consecutive pair into a row for the new dataset
        for i in range(len(section_rows) - 1):
            from_station = \
                section_rows.loc[i, 'Stop:Station code'].capitalize()
            to_station = \
                section_rows.loc[i+1, 'Stop:Station code'].capitalize()

            # Apply processor to datetimes, including possible delays
            departure_time = process_datetime(
                section_rows.loc[i, 'Stop:Departure time'],
                section_rows.loc[i, 'Stop:Departure delay'],
            )
            arrival_time = process_datetime(
                section_rows.loc[i+1, 'Stop:Arrival time'],
                section_rows.loc[i+1, 'Stop:Arrival delay'],
            )
            stop_id = section_rows.loc[i+1, 'Stop:RDT-ID']

            # Each connection will appear as one line in the new dataset
            new_df_lines.append([
                from_station, to_station, departure_time, arrival_time,
                mapped_train_type, section_id, stop_id,
            ])

    structured_df = pd.DataFrame(
        data=new_df_lines,
        columns=new_columns,
    )

    # Remove timezone indication (keep date as is) from datetime cols
    for col in ['Departure', 'Arrival']:
        structured_df[col] = structured_df[col].dt.tz_localize(None)

    return structured_df


def filter_empty_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Filter out any rows that do not have a departure or arrival value"""
    for col in ['Departure', 'Arrival']:
        df = df[~df[col].isna()]
    return df


def preprocess():
    """Function to preprocess the raw dataset.

    After downloading, and before running anything, do not forget to delete the
    following rows (if running for day 2025-10-04). Somehow Dordrecht appeared
    out of nowhere in a few rows, heavily influencing some speeds.

    16911556, DDR (index 221558)
    16911368, DDR (index 219962)
    16909085, DDR (index 200595)
    """
    raw_file_name = 'services-2026-07.csv'
    path_to_raw_file = SETTINGS.DATA_PATH / raw_file_name
    path_to_timetable = SETTINGS.DATA_PATH / SETTINGS.TIMETABLE_FILE

    raw_df = read_csv_to_df(path_to_raw_file)
    cleaned_df = clean_data(raw_df)
    structured_df = structure_data(cleaned_df)
    filtered_df = filter_empty_dates(structured_df)

    save_timetable(
        timetable_df=filtered_df,
        timetable_path=path_to_timetable,
    )
