import json
from time import time
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

from settings import Parameters, VersionSettings
SETTINGS = VersionSettings.get_version_settings()


def run_algo(timestamp):
    """Calls the right path finding algorithm based on the version."""
    match SETTINGS.VERSION:
        case 'v0' | 'v1':
            from route_finding.algo_older_versions.v0v1_greedy_dfs \
                import run_greedy_dfs
            run_greedy_dfs(timestamp)

        case 'v2':
            from route_finding.v2_explore_set import run_explore_set
            run_explore_set(timestamp)


if __name__ == "__main__":
    time_start = time()
    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")

    parameters_path: Path = SETTINGS.PARAMETERS_PATH
    json_file_path = (parameters_path / timestamp).with_suffix('.json')

    params_dict = asdict(Parameters())
    params_dict['TIMESTAMP'] = timestamp

    with open(json_file_path, 'w') as f:
        json.dump(params_dict, f)

    run_algo(timestamp)

    time_end = time()
    print(f"That shit took {time_end - time_start:.2f} seconds.")
