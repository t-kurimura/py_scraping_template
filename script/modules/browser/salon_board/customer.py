from datetime import datetime
from time import sleep
from typing import Optional
import logging

from selenium.webdriver.common.by import By

from ...browser.base import take_screenshot
from ...firebase.storage import upload_latest_and_delete


def get_customer_detail(
    browser,
    customer_id
) -> []:

    # Define a function to get text from an element and print it with a label
    def extract_from_xpath(element_locator: str) -> Optional[str]:
        if len(browser.find_elements(By.XPATH, element_locator)) == 0:
            return None
        elm = browser.find_element(By.XPATH, element_locator)
        return elm.text.strip()

    default_url = f"https://hoge.com/KLP/customer/customerDetail/?customerId={customer_id}"

    browser.get(default_url)
    sleep(3)

    take_screenshot(browser)
    upload_latest_and_delete()

    base_info = {
        "birthday": extract_from_xpath('//th[text()="誕生日"]/following-sibling::td'),
        "gender": extract_from_xpath('//th[text()="性別"]/following-sibling::td')
    }

    page_text = browser.find_element(
        By.CSS_SELECTOR,
        "#customerDetail > div.mod_column02.mt15.cf.reserveListPaging > div > div > p.page.mod_font01"
    )
    reservations = []
    if page_text is None:
        logging.info("No result")
        return (
            base_info,
            reservations
        )

    logging.info(page_text.text)
    numerator, denominator = map(int, page_text.text.replace("ページ", "").split("/"))

    while numerator <= denominator:
        tables = browser.find_elements(By.XPATH, "//form//table[last()]")
        rows = tables[len(tables)-1].find_elements(By.XPATH, ".//tr")
        if len(rows) <= 1:
            break

        for row in rows[1:]:
            # 予約番号を取得
            reserve_id = row.find_element(
                By.CSS_SELECTOR,
                "td a.reserveActionLinkTypePost"
            ).text.strip("()")

            reserve_date = row.find_element(By.CSS_SELECTOR, "td:first-child").text.split("\n")[0]
            reserve_datetime = datetime.strptime(reserve_date, "%Y/%m/%d")
            reservations.append((reserve_id, reserve_datetime))

        numerator += 1
        browser.get(f"{default_url}&pn={numerator + 1}")
        sleep(2)

    logging.info(f"Total past reservations count: {len(reservations)}")
    return (
        base_info,
        reservations
    )
