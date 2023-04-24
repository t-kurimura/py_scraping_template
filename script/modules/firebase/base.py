
import firebase_admin
from firebase_admin import credentials

DEFAULT_APP_NAME = "app_name"


def get_instance():
    try:
        return firebase_admin.initialize_app(
            credentials.ApplicationDefault(),
            name=DEFAULT_APP_NAME
        )
    except ValueError:
        return firebase_admin.get_app(
            name=DEFAULT_APP_NAME
        )