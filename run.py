import json
from time import time
from datetime import datetime
from .settings import Settings
from .route_finding.greedy_dfs import run_greedy_dfs


if __name__ == "__main__":
    time_start = time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    parameters = {
        'version': 'v0',
        'start_station': 'Ht',
        'start_time': '12:00',
        'end_time': '15:00',
        'min_transfer_time': 3,
        'max_transfer_time': 15,
        'timestamp': timestamp,  # Automatically generated
    }
    
    parameters_path = Settings.VERSIONED_PARAMETERS_PATH[parameters['version']]
    json_file_path = (parameters_path / timestamp).with_suffix('.json')

    with open(json_file_path, 'w') as f:
        json.dump(parameters, f)
    
    run_greedy_dfs(parameters)
    
    time_end = time()
    print(f"That shit took {time_end - time_start:.2f} seconds.")
    
    