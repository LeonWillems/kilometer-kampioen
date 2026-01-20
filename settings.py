from pathlib import Path
from pandas import Timestamp
from dataclasses import dataclass, asdict, field


@dataclass
class Parameters:
    VERSION: str = 'v1'  # 'v0' / 'v1'
    START_STATION: str = 'Ehv'
    START_TIME: str = '08:00'
    END_TIME: str = '20:00'
    MIN_TRANSFER_TIME: int = 3
    MAX_TRANSFER_TIME: int = 15


VERSION_SETTINGS = {
    'versions': ['v0', 'v1'],
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
    RUNS_DIR: Path = ROOT_DIR / 'runs'
    INFORMATION_DIR: Path = ROOT_DIR / 'information'

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
