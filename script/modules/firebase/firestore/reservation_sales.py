import logging

from firebase_admin import firestore

from ..base import get_instance


def upsert(
    parent_reservation_id: str,
    sales_id: str,
    content: dict
):
    logging.info(f"Save sales: {sales_id}")

    firestore.client(
        app=get_instance()
    ).collection(
        "hogeBoardReservations"
    ).document(
        parent_reservation_id
    ).collection(
        "sales"
    ).document(
        sales_id
    ).set({
        **content,
        "metadata": {
            "updatedAt": firestore.firestore.SERVER_TIMESTAMP,
        }
    })