from pathlib import Path
from pandas import Timestamp
from dataclasses import dataclass, asdict, field


# These are just the proposed standard values. Feel free to play around
# with any of the values. For value constraints, see the READMM.
VERSION_SETTINGS = {
    'versions': ['v0', 'v1'],
    'start_station': {
        'v0': 'Ehv',
        'v1': 'Ehv',
    },
    'start_time': {
        'v0': '12:00',
        'v1': '08:00',
    },
    'end_time': {
        'v0': '15:00',
        'v1': '20:00',
    },
    'min_transfer_time':  3,  # So far, this has not been changed
    'max_transfer_time': 15,  # So far, this has not been changed
    'name': {
        'v0': 'greedy_dfs',
        'v1': 'whole_day_data',
    },
    'day_of_run': {
        'v0': '2025-08-02',  # Day where the train times come from
        'v1': '2025-10-04',
    },
    'datetime_format': {
        'v0': 'ISO8601',  # YYYY-MM-DDThh:mm:ss (or similar!)
        'v1': 'ISO8601',  # 'RFC3339'
    },
}


@dataclass
class Parameters:
    VERSION: str = 'v1'  # 'v0' / 'v1'
    START_STATION: str = VERSION_SETTINGS['start_station'][VERSION]
    START_TIME: str = VERSION_SETTINGS['start_time'][VERSION]
    END_TIME: str = VERSION_SETTINGS['end_time'][VERSION]
    MIN_TRANSFER_TIME: int = VERSION_SETTINGS['min_transfer_time']
    MAX_TRANSFER_TIME: int = VERSION_SETTINGS['max_transfer_time']


@dataclass
class BaseSettings:
    # Moment from which we count minutes
    EPOCH_TIMESTAMP: Timestamp = Timestamp("1970-01-01 00:00")

    # Train type setting
    TYPE_CONVERSION: dict = field(
        default_factory=lambda: {'Spr': 'S', 'Int': 'I'}
    )

    # Base dirs
    ROOT_DIR: Path = Path(__file__).resolve().parent

    DATA_DIR: Path = ROOT_DIR / 'data'
    INFORMATION_DIR: Path = ROOT_DIR / 'information'
    RUNS_DIR: Path = ROOT_DIR / 'runs'
    VISUALIZATION_DIR: Path = ROOT_DIR / 'visualization'

    LOGS_DIR: Path = RUNS_DIR / 'logs'
    ROUTES_DIR: Path = RUNS_DIR / 'routes'
    PARAMETERS_DIR: Path = RUNS_DIR / 'parameters'

    # Intermediate stations file
    INTERMEDIATE_STATIONS_FILE: str = 'intermediate_stations.json'

    # Timetable file names, location dependent on version
    TIMETABLE_FILE: str = 'timetable.csv'
    TIMETABLE_FILE_PROCESSED: str = TIMETABLE_FILE \
        .replace('.csv', '_processed.csv')

    # Distances file names, one location
    DISTANCES_FILE: str = 'station_distances.json'
    DISTANCES_FILE_PROCESSED: str = DISTANCES_FILE \
        .replace('.json', '_processed.json')

    # Distance paths are constant
    DISTANCES_PATH: Path = INFORMATION_DIR / DISTANCES_FILE
    PROCESSED_DISTANCES_PATH: Path = DATA_DIR / DISTANCES_FILE_PROCESSED

    # The station file is given and constant
    STATIONS_FILE: str = 'stations-2023-09.csv'
    STATIONS_PATH: Path = INFORMATION_DIR / STATIONS_FILE

    # Files for plotting purposes are constant
    SPOORKAART_FILE: str = 'spoorkaart-simple.png'
    COORDINATES_FILE: str = 'station-coordinates.json'
    CORNERS_FILE: str = 'corners.json'

    SPOORKAART_PATH: Path = VISUALIZATION_DIR / SPOORKAART_FILE
    COORDINATES_PATH: Path = VISUALIZATION_DIR / COORDINATES_FILE
    CORNERS_PATH: Path = VISUALIZATION_DIR / CORNERS_FILE


@dataclass
class VersionSettings(BaseSettings):
    VERSION: str = field(default='')
    VERSION_NAME: str = field(default='')
    DAY_OF_RUN: str = field(default='')
    DATETIME_FORMAT: str = field(default='')

    DATA_PATH: Path = field(default=Path())
    LOGS_PATH: Path = field(default=Path())
    ROUTES_PATH: Path = field(default=Path())
    PARAMETERS_PATH: Path = field(default=Path())

    @classmethod
    def get_version_settings(cls):
        version = Parameters.VERSION
        assert version in VERSION_SETTINGS['versions'], "Invalid version"

        base_settings = BaseSettings()
        settings_dict = asdict(base_settings)

        return cls(
            VERSION=version,
            VERSION_NAME=VERSION_SETTINGS['name'][version],
            DAY_OF_RUN=VERSION_SETTINGS['day_of_run'][version],
            DATETIME_FORMAT=VERSION_SETTINGS['datetime_format'][version],

            DATA_PATH=settings_dict['DATA_DIR'] / version,
            LOGS_PATH=settings_dict['LOGS_DIR'] / version,
            ROUTES_PATH=settings_dict['ROUTES_DIR'] / version,
            PARAMETERS_PATH=settings_dict['PARAMETERS_DIR'] / version,

            **settings_dict
        )
