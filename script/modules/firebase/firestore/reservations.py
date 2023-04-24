import logging

from firebase_admin import firestore

from ..base import get_instance


def upsert_listed_items_if_different(reservation_id: str, content: dict) -> bool:
    reservation_ref = firestore.client(app=get_instance()) \
        .collection("hogeBoardReservations").document(reservation_id)

    batch = firestore.client(app=get_instance()).batch()

    listed_snapshot = reservation_ref.collection("listed").document(reservation_id).get()
    if listed_snapshot.exists:
        current_data = listed_snapshot.to_dict()
        is_diff = False

        for key in content.keys():
            if key == "metadata":
                continue
            if key not in current_data:
                is_diff = True
                break
            if content[key] != current_data[key]:
                is_diff = True
                break
        if is_diff:
            batch.set(
                reservation_ref,
                {
                    "listedUpdatedAt": firestore.firestore.SERVER_TIMESTAMP
                }
            )
            batch.set(listed_snapshot.reference, content)
            batch.commit()
            return True
        else:
            return False

    batch.set(
        reservation_ref,
        {
            "listedCreatedAt": firestore.firestore.SERVER_TIMESTAMP,
            "listedUpdatedAt": firestore.firestore.SERVER_TIMESTAMP
        }
    )
    batch.set(
        listed_snapshot.reference, content
    )
    batch.commit()
    return True


def upsert_detail_items(
    reservation_id: str,
    content: dict
):
    logging.info(f"upsert_detail_items: {reservation_id}")

    client = firestore.client(app=get_instance())
    ref = client.collection("hogeBoardReservations").document(reservation_id)
    detail_ref = ref.collection("detail").document(reservation_id)

    batch = client.batch()
    if ref.get().exists:
        batch.update(ref, {"detailUpdatedAt": firestore.firestore.SERVER_TIMESTAMP})
    else:
        batch.set(ref, {"detailUpdatedAt": firestore.firestore.SERVER_TIMESTAMP})
    batch.set(detail_ref, content)

    batch.commit()


def is_exist(
        reservation_id: str,
):
    client = firestore.client(app=get_instance())
    ref = client.collection("hogeBoardReservations").document(reservation_id)
    detail_ref = ref.collection("detail").document(reservation_id)

    return detail_ref.get().exists
