import sys

from settings import Parameters, VersionSettings
SETTINGS = VersionSettings.get_version_settings()


def run_algo(timestamp):
    """Calls the right path finding algorithm based on the version."""
    match SETTINGS.VERSION:
        case 'v0' | 'v1':
            print("Run from save supported from v2 onwards.")

        case 'v2':
            from route_finding.v2_explore_set import run_explore_set
            run_explore_set(timestamp)


if __name__ == "__main__":
    # The last `Stop_ID` value to use, continue from there
    stop_id = sys.argv[1]
