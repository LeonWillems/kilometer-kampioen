from pathlib import Path


class Settings:
    # Datetime settings
    DAY_OF_RUN = "2025-08-02"  # Day where the train times come from
    DATETIME_FORMAT = "ISO8601"  # YYYY-MM-DDThh:mm:ss (or similar!)
    
    # Base path
    ROOT_PATH = Path(__file__).resolve().parent
    
    INFORMATION_PATH = ROOT_PATH / 'information'
    DATA_PATH = ROOT_PATH / 'data'
    VERSIONED_DATA_PATHS = {
        'v0': DATA_PATH / 'v0',
    }

    # Timetable file names, location dependent on version
    TIMETABLE_FILE = 'timetable.csv'
    TIMETABLE_FILE_PROCESSED = TIMETABLE_FILE \
        .replace('.csv', '_processed.csv')
    
    # Distances file names, one location
    DISTANCES_FILE = 'station_distances.json'
    DISTANCES_FILE_PROCESSED = DISTANCES_FILE \
        .replace('.json', '_processed.json')

    # Distance paths are constant
    DISTANCES_PATH = INFORMATION_PATH / DISTANCES_FILE
    PROCESSED_DISTANCES_PATH = DATA_PATH / DISTANCES_FILE_PROCESSED

    # Other train settings
    TYPE_CONVERSION = {'Spr': 'S', 'Int': 'I'}

    # Version names
    VERSION_NAMES = {
        'v0': 'greedy_dfs',
    }
    
    # Runs path
    RUNS_PATH = ROOT_PATH / 'runs'
    
    # Route tables
    ROUTES_PATH = RUNS_PATH / 'routes'
    VERSIONED_ROUTES_PATH = {
        'v0': ROUTES_PATH / 'v0',
    }

    # Logging files
    LOGS_PATH = RUNS_PATH / 'logs'
    VERSIONED_LOGS_PATH = {
        'v0': LOGS_PATH / 'v0',
    }
    
    # Parameter settings
    PARAMETERS_PATH = RUNS_PATH / 'parameters'
    VERSIONED_PARAMETERS_PATH = {
        'v0': PARAMETERS_PATH / 'v0',
    }
    
    