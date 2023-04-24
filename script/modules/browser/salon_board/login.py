import os
import pickle
from time import sleep
import logging

from dotenv import load_dotenv

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from ...browser.base import take_screenshot
from ...firebase.storage import upload_latest_and_delete


def _get_hoge_board_env() -> [str, str]:
    load_dotenv("../cred/hoge-board-ipass")
    return [
        os.getenv("ID"),
        os.getenv("PASSWORD")
    ]


def login(browser):
    logging.info("Start login")
    pickle_file_name = "cookies.pkl"

    logging.info(f"Search {pickle_file_name}")
    if os.path.isfile(f"res/{pickle_file_name}"):
        logging.info("Found pickle")
        browser.get("https://hoge.com")
        cookies = pickle.load(open("res/cookies.pkl", "rb"))
        for cookie in cookies:
            browser.add_cookie(cookie)
        logging.info("Add cookie to driver")

    browser.get("https://hoge.com/KLP/top/")
    logging.info("Move to console top")
    sleep(3)
    logging.info(f"Transitioned to the page : {browser.title}")

    if "エラー" in browser.title:
        logging.info("Failed to open console top, move to login flow")
        browser.get("https://hoge.com/login/")
        sleep(3)

        sb_id, sb_password = _get_hoge_board_env()

        logging.info("Input Id & password")
        user_name_input = browser.find_element(By.NAME, "userId")
        user_name_input.send_keys(sb_id)

        password_input = browser.find_element(By.NAME, "password")
        password_input.send_keys(sb_password)
        logging.info("Completed to input")

        take_screenshot(browser)
        upload_latest_and_delete()

        password_input.send_keys(Keys.RETURN)
        logging.info("Push login button...")
        sleep(5)

        logging.info(f"Page transitioned to : {browser.title}")
        if "TOP PAGE" == browser.title:
            logging.info("Login succeeded")
            pickle.dump(
                browser.get_cookies(),
                open(
                    f"res/{pickle_file_name}",
                    "wb"
                )
            )
            logging.info("Saved pickle")

    sleep(2)

