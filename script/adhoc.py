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

    browser_session = modules.browser.base.create_browser()
    try:
        modules.browser.hoge_board.login.login(browser_session)

        modules.browser.base.take_screenshot(browser_session)
        modules.firebase.storage.upload_latest_and_delete()

        customer_id = "C00973021354"
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
            modules.firebase.firestore.reservations.upsert_detail_items(
                **p_reservation
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
