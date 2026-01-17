import json
from time import time
from datetime import datetime
from dataclasses import asdict

from .route_finding.greedy_dfs import run_greedy_dfs
from .settings import Parameters, VersionSettings
SETTINGS = VersionSettings.get_version_settings()


if __name__ == "__main__":
    time_start = time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    parameters_path = SETTINGS.PARAMETERS_PATH
    json_file_path = (parameters_path / timestamp).with_suffix('.json')

    params_dict = asdict(Parameters())
    params_dict['TIMESTAMP'] = timestamp

    with open(json_file_path, 'w') as f:
        json.dump(params_dict, f)

    run_greedy_dfs(timestamp)

    time_end = time()
    print(f"That shit took {time_end - time_start:.2f} seconds.")
