from pathlib import Path

from settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()


def get_latest_run_path() -> Path:
    """Get latest run path for current version."""
    runs_path = SETTINGS.RUNS_PATH
    run_paths = [path for path in runs_path.iterdir() if path.is_dir()]
    return run_paths[-1]


def get_file_path(extension: str) -> Path:
    """Get file with some extension from the latest run path.

    Args:
    - extension (str): File extension, including dot, example: `.csv`

    Returns:
    - Path: Path to corresponding file
    """
    last_run_path = get_latest_run_path()

    route_files_paths = sorted(last_run_path.glob(f"*{extension}"))
    return route_files_paths[0]
