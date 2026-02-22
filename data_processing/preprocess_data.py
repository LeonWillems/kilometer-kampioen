from settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()


def perform_preprocesing():
    """Calls the right preprocessing functionality based on the version."""
    match SETTINGS.VERSION:
        case 'v0':
            from data.v0 import preprocessing_v0
            preprocessing_v0.preprocess()

        case 'v1':
            from data.v1 import preprocessing_v1
            preprocessing_v1.preprocess()

        case 'v2':
            from data.v2 import preprocessing_v2
            preprocessing_v2.preprocess()
