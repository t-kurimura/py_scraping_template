import os
import logging

from firebase_admin import storage
from ..firebase.base import get_instance


def upload_latest_and_delete():
    dir_path = "./images"
    files = os.listdir(dir_path)
    files_with_time = [(f, os.path.getmtime(os.path.join(dir_path, f))) for f in files]
    latest_file = sorted(files_with_time, key=lambda x: x[1], reverse=True)[0][0]
    target_file_path = f"./images/{latest_file}"

    storage.bucket(
        name="will_be_deleted_after_14d",
        app=get_instance()
    ).blob(
        f"screenshots/{latest_file}"
    ).upload_from_filename(
        target_file_path
    )
    logging.info(f" Uploaded to GCS: {latest_file}")

    if os.path.exists(target_file_path):
        os.remove(target_file_path)
    logging.info(f" Removed from local: {latest_file}")
