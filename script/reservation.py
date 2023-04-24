#!/usr/local/bin/python3
import os
import sys
import logging
from datetime import datetime, timedelta

import modules.browser.base
import modules.browser.hoge_board.reservation_detail
import modules.browser.hoge_board.reservation_list
import modules.browser.hoge_board.customer
import modules.browser.hoge_board.login
import modules.firebase.firestore.reservation_sales
import modules.firebase.firestore.reservations
import modules.firebase.firestore.customers
import modules.firebase.firestore.stylists
import modules.firebase.storage
from modules.logging import setup_logger

if __name__ == "__main__":
    logger = setup_logger({
        "file": os.path.basename(__file__),
    })

    arg1 = int(sys.argv[1])
    arg2 = int(sys.argv[2])

    now = datetime.now()
    search_range = (
        (now + timedelta(days=arg1)).strftime("%Y%m%d"),
        (now + timedelta(days=arg2)).strftime("%Y%m%d")
    )

    logging.info("Start to get data from {} to {}".format(
        *search_range
    ))
    browser_session = modules.browser.base.create_browser()
    try:
        modules.browser.hoge_board.login.login(browser_session)

        modules.browser.base.take_screenshot(browser_session)
        modules.firebase.storage.upload_latest_and_delete()

        logging.info("Searching list => ")
        reservation_list = modules.browser.hoge_board.reservation_list.reservation_list_page(
            browser_session,
            search_range,
        )
        logging.info("Go to each reservation detail page => ")
        for reservation_id, content in reservation_list:
            stylist_id = modules.firebase.firestore.stylists.find_stylist_id_by_name(
                content.get("staff").replace("(指)", "")
            )
            logging.info(f"Found stylist : {stylist_id}")

            logging.info(f"=== reservation_id: {reservation_id} ====")
            has_updated = modules.firebase.firestore.reservations.upsert_listed_items_if_different(
                reservation_id=reservation_id,
                content={
                    **content,
                    "stylistId": stylist_id
                }
            )
            logging.info(f"Is updated?: {has_updated}")

            if not has_updated:
                logging.info("Skipped by not updated!")
                continue

            result = modules.browser.hoge_board.reservation_detail.scrape_reservation_page(
                browser_session,
                reservation_id,
                search_range,
            )
            logging.info("Got reservation detail")
            if result is None:
                logging.info("Skipped by no detail!")
                continue

            reservation, customer, sale = result.values()
            modules.firebase.firestore.reservations.upsert_detail_items(
                reservation_id=reservation.get("reservation_id"),
                content={
                    **reservation.get("content"),
                    "stylistId": stylist_id,
                }
            )

            if sale is not None:
                modules.firebase.firestore.reservation_sales.upsert(
                    reservation_id,
                    **sale
                )

            new_customer = modules.firebase.firestore.customers.upsert(
                **customer
            )
            logging.info(f"Is new customer?: {new_customer}")

            if new_customer:
                customer_id, _ = customer.values()

                logging.info(f"Go to customer detail: {customer_id}")
                customer_detail_result = modules.browser.hoge_board.customer.get_customer_detail(
                    browser_session,
                    customer_id,
                )
                modules.firebase.firestore.customers.update(
                    customer_id,
                    customer_detail_result[0]
                )

                for past_reservations in customer_detail_result[1]:
                    past_reservation_id = past_reservations[0]
                    logging.info(f"* Check past reservation : {past_reservation_id}")

                    if reservation_id == past_reservation_id:
                        logging.info("Skipped by exact same to base reservation")
                        continue

                    is_already_saved = modules.firebase.firestore.reservations.is_exist(
                        past_reservation_id
                    )
                    logging.info(f"Is already saved user? : {is_already_saved}")
                    if is_already_saved:
                        logging.info("Skipped by already saved")
                        continue

                    past_reservation_result = modules.browser.hoge_board.reservation_detail.scrape_reservation_page(
                        browser_session,
                        past_reservations[0],
                        (
                            past_reservations[1].strftime("%Y%m%d"),
                            past_reservations[1].strftime("%Y%m%d")
                        ),
                    )
                    logging.info("Got past reservation detail")
                    if past_reservation_result is None:
                        logging.info("Skip by past reservation result none")
                        continue

                    p_reservation, _, p_sale = past_reservation_result.values()
                    stylist_id = modules.firebase.firestore.stylists.find_stylist_id_by_name(
                        p_reservation.get("content").get("staff").replace("(指)", "")
                    )
                    modules.firebase.firestore.reservations.upsert_detail_items(
                        reservation_id=p_reservation.get("reservation_id"),
                        content={
                            **p_reservation.get("content"),
                            "stylistId": stylist_id,
                        }
                    )
                    if p_sale is not None:
                        modules.firebase.firestore.reservation_sales.upsert(
                            past_reservation_id,
                            **p_sale
                        )
    except Exception as e:
        logging.error(f"error occurred: {e}", exc_info=True)
    finally:
        logging.info("browser closed")
        browser_session.close()
        browser_session.quit()
