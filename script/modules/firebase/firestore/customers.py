import logging

from firebase_admin import firestore
from ..base import get_instance


def upsert(
        customer_id: str,
        content: dict
) -> bool:
    logging.info(f"Upsert customer: {customer_id}")
    doc_ref = firestore.client(
        app=get_instance()
    ).collection(
        u"hogeBoardCustomers"
    ).document(
        customer_id
    )
    if doc_ref.get().exists:
        doc_ref.update(
            {
                **content,
                "metadata": {
                    "updatedAt": firestore.firestore.SERVER_TIMESTAMP,
                }
            }
        )
        return False
    else:
        doc_ref.set(
            {
                **content,
                "metadata": {
                    "createdAt": firestore.firestore.SERVER_TIMESTAMP,
                    "updatedAt": firestore.firestore.SERVER_TIMESTAMP,
                }
            }
        )
        return True


def update(
        customer_id: str,
        content: dict
):
    logging.info(f"Update customer: {customer_id}")
    firestore.client(
        app=get_instance()
    ).collection(
        u"hogeBoardCustomers"
    ).document(
        customer_id
    ).update(
        {
            **content,
            "metadata": {
                "updatedAt": firestore.firestore.SERVER_TIMESTAMP,
            }
        }
    )
