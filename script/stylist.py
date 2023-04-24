#!/usr/local/bin/python3
import logging
import os

import modules.browser.base
import modules.browser.hoge_board.stylists
import modules.browser.hoge_board.login
import modules.firebase.firestore.stylists

import modules.firebase.storage
import modules.firebase.firestore.customers

from modules.logging import setup_logger


if __name__ == "__main__":
    setup_logger({
        "file": os.path.basename(__file__),
    })

    logging.info("Creating headless browser now")

    browser_session = modules.browser.base.create_browser()
    try:
        modules.browser.hoge_board.login.login(browser_session)

        modules.browser.base.take_screenshot(browser_session)
        modules.firebase.storage.upload_latest_and_delete()

        stylists = modules.browser.hoge_board.stylists.get_stylists(
            browser_session
        )
        logging.info("go to each detail page")
        for stylist_id, content in stylists:
            modules.firebase.firestore.stylists.upsert(
                stylist_id,
                content
            )
    except Exception as e:
        logging.error(f"error occurred: {e}", exc_info=True)
    finally:
        logging.info("browser closed")
        browser_session.close()
        browser_session.quit()
