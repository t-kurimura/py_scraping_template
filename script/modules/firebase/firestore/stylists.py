import logging
from typing import Optional

from firebase_admin import firestore

from ..base import get_instance


def upsert(
    stylist_id: str,
    content: dict
):
    logging.info(f"Save stylists: {stylist_id}")
    firestore.client(
        app=get_instance()
    ).collection(
        u"hogeBoardStylists"
    ).document(
        stylist_id
    ).set(
        {
            **content,
            "metadata": {
                "updatedAt": firestore.firestore.SERVER_TIMESTAMP,
            }
        }
    )


def find_stylist_id_by_name(name: str) -> Optional[str]:
    logging.info(f"search stylists by {name}")
    snapshots = firestore.client(
        app=get_instance()
    ).collection(
        u"hogeBoardStylists"
    ).where(
        field_path="name", op_string="==", value=name
    ).get()

    if len(snapshots) == 0:
        logging.info("Stylist not found")
        return None

    if len(snapshots) > 1:
        logging.info(f"Stylist name conflict: {len(snapshots)}")
        return None

    return snapshots[0].id
