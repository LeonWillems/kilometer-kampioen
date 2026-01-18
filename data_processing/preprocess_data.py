from data.v0 import preprocessing_v0
from data.v1 import preprocessing_v1

from settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()


def perform_preprocesing():
    match SETTINGS.VERSION:
        case 'v0':
            preprocessing_v0.preprocess()
        case 'v1':
            preprocessing_v1.preprocess()
