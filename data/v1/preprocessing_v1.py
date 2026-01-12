import pandas as pd

from ...data_processing.data_utils import read_csv_to_df, save_timetable
from ...settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()

COLUMNS_OF_INTEREST = [
    'Stop:Station code', 'Stop:Arrival time', 
    'Stop:Departure time',
    'Service:Type', 'Service:RDT-ID',
]

ACCEPTED_TRAIN_TYPES = [
    'Intercity', 'Snelbus ipv trein', 'Sprinter', 'Sneltrein', 
    'Stoptrein', 'Stopbus ipv trein', 'Intercity direct',
]

TRAIN_TYPE_MAPPING = {
    'Intercity': 'Int',
    'Snelbus ipv trein': 'Int',
    'Sprinter': 'Spr',
    'Sneltrein': 'Spr', 
    'Stoptrein': 'Spr',
    'Stopbus ipv trein': 'Spr',
    'Intercity direct': 'Int',
}

STATION_CODE_MAPPING = {
    'DTCP': 'DTZ'
}

INTERNATIONAL_STATION_CODES = [
    'AHBF', 'ANDD', 'ATW', 'ATWLB', 'AW', 'BERCH', 'BH', 'BIELEF', 'BRESSX',
    'BUENDE', 'DUISB', 'DUSSEL', 'EAHS', 'EBEO', 'EBOK', 'ECMF', 'EDD', 'EDKD',
    'EDO', 'EDULH', 'EENP', 'EEPE', 'EHW', 'EHZW', 'EL', 'ELDH', 'ELET',
    'ELGD', 'ELUE', 'EM', 'EOP', 'EPRA', 'EPRN', 'ESEB', 'ESEM', 'ESN', 'ESRT',
    'EUN', 'FKTH', 'FNZD', 'FRP', 'FVS', 'G', 'GKT', 'GWD', 'HAGEN', 'HAMM',
    'HZ', 'KBOI', 'KBRY', 'KDFFH', 'KDUL', 'KN', 'KSWE', 'KWBA', 'KWO', 'LEER',
    'LKP', 'LKR', 'LUIK', 'MARIA', 'MCGB', 'MID', 'NEUSS', 'OBERH', 'OBERHS',
    'OSNH', 'RHEINE', 'VIERS', 'WESEL', 'WR', 'WUPPH', 'WUPPV'
]
    
def clean_data(timetable_df: pd.DataFrame) -> pd.DataFrame:
    """"""
    # 1. Only keep the relevant day
    df_filtered_day = timetable_df[timetable_df['Service:Date'] == SETTINGS.DAY_OF_RUN]
    
    # 2. Drop unnecessary columns
    df_filtered_cols = df_filtered_day[COLUMNS_OF_INTEREST]
    
    # 3. Keep train types that are accepted (to prevent taking a nighttrain, for example)
    df_filtered_train_types = df_filtered_cols[
        df_filtered_cols['Service:Type'].isin(ACCEPTED_TRAIN_TYPES)
    ]
    
    # 4. Replace station codes to comply with the NS codes list
    df_filtered_train_types['Stop:Station code'] \
        = df_filtered_train_types['Stop:Station code'].replace(STATION_CODE_MAPPING)
    
    # 5. Delete rows with international station codes
    df_codes_deleted = df_filtered_train_types[
        ~df_filtered_train_types['Stop:Station code'].isin(INTERNATIONAL_STATION_CODES)
    ]
    
    return df_codes_deleted

def structure_data(timetable_df: pd.DataFrame) -> pd.DataFrame:
    section_ids = timetable_df['Service:RDT-ID'].unique()
    
    new_df_lines = []
    new_columns = [
        'Station', 'To', 'Departure', 'Arrival', 'Type', 'ID'
    ]
    
    for section_id in section_ids:
        section_rows = timetable_df[timetable_df['Service:RDT-ID'] == section_id]
        section_rows.reset_index(inplace=True)
        
        service_type = section_rows.loc[0, 'Service:Type']
        mapped_train_type = TRAIN_TYPE_MAPPING[service_type]
            
        for i in range(len(section_rows) - 1):
            from_station = section_rows.loc[i, 'Stop:Station code'].capitalize()
            to_station = section_rows.loc[i+1, 'Stop:Station code'].capitalize()
            
            departure_time = section_rows.loc[i, 'Stop:Departure time']
            arrival_time = section_rows.loc[i+1, 'Stop:Arrival time']

            new_df_lines.append([
                from_station, to_station, departure_time, 
                arrival_time, mapped_train_type, section_id,
            ])
            
    structured_df = pd.DataFrame(
        data=new_df_lines, 
        columns=new_columns,
    )
    
    # 4. Turn deperture/arrival columns to pd.Datetime
    #    and remove timezone indication (keep date as is)
    for col in ['Departure', 'Arrival']:
        structured_df[col] = pd.to_datetime(
            structured_df[col],
            format=SETTINGS.DATETIME_FORMAT,
        ).dt.tz_localize(None)
    
    return structured_df

def filter_empty_dates(df: pd.DataFrame) -> pd.DataFrame:
    # Consecutively filter out nans for various columns
    for col in ['Departure', 'Arrival']:
        df = df[~df[col].isna()]
    return df

def preprocess():
    raw_file_name = 'services-2025-10.csv'
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