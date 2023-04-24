import re
from datetime import datetime, timedelta
from time import sleep
from typing import Optional
import logging

from selenium.webdriver.common.by import By

from .reservation_list import set_conditions_on_search_page
from ...firebase import storage
from ...browser import base


def scrape_reservation_page(
        browser,
        reservation_id: str,
        search_range: (str, str)
) -> Optional[dict]:

    set_conditions_on_search_page(
        browser,
        *search_range
    )

    browser.execute_script("document.getElementById('reserveId').value = arguments[0]", reservation_id)

    browser.find_element(By.ID, "search").click()
    logging.info(f"Searching detail {reservation_id}")
    sleep(4)

    base.take_screenshot(browser)
    storage.upload_latest_and_delete()

    reserve_links = browser.find_elements(
        By.CSS_SELECTOR,
        "#reserveListArea a[href*=reserveId]"
    )
    if len(reserve_links) == 0 or len(reserve_links[0].get_attribute("href")) == 0:
        logging.info("No data")
        return None
    logging.info(reserve_links[0].get_attribute("href"))
    browser.get(reserve_links[0].get_attribute("href"))
    sleep(5)

    # 来店日時の取得とdatetime型への変換
    rsv_date_locator = (By.CSS_SELECTOR, "#rsvDate")
    rsv_date = browser.find_element(*rsv_date_locator).text.strip()
    date_str = rsv_date.split("（")[0]
    time_pattern = re.compile(r"\d{1,2}:\d{2}")
    times = time_pattern.findall(rsv_date)
    start_time = datetime.strptime("".join([
        date_str,
        times[0]
    ]), "%Y年%m月%d日%H:%M") - timedelta(hours=9)
    end_time = datetime.strptime("".join([
        date_str,
        times[1]
    ]), "%Y年%m月%d日%H:%M") - timedelta(hours=9)

    # 会計情報
    sales_exists = len(browser.find_elements(By.ID, "salesId"))

    # Define a function to get text from an element and print it with a label
    def extract_from_xpath(element_locator: str) -> Optional[str]:
        if len(browser.find_elements(By.XPATH, element_locator)) == 0:
            return None
        element = browser.find_element(By.XPATH, element_locator)
        return element.text.strip()

    return {
        "reservation": {
            "reservation_id": extract_from_xpath('//th[text()="予約番号"]/following-sibling::td'),
            "content": {
                "status": extract_from_xpath('//th[text()="ステータス"]/following-sibling::td'),
                "time": {
                    "start": start_time,
                    "end": end_time,
                },
            },
        },
        "customer": {
            "customer_id": browser.find_element(By.ID, "customerDetailLink").get_attribute('data-customerid'),
            "content": {
                "nameKana": extract_from_xpath('//th[text()="氏名 (カナ)"]/following-sibling::td/div[@class="nameKana"]'),
                "nameKanji": extract_from_xpath('//th[text()="氏名 (漢字)"]/following-sibling::td'),
                "phoneNumber": extract_from_xpath('//th[text()="電話番号"]/following-sibling::td'),
            }
        },
        "sale": {
            "sales_id": browser.find_element(By.ID, "salesId").get_attribute("value") if sales_exists else None,
            "content": {
                "items": [
                    {
                        "category": item.find_element(By.XPATH, './td[1]').text.strip(),
                        "menu": item.find_element(By.XPATH, './td[2]').text.strip(),
                        "staff": item.find_element(By.XPATH, './td[3]').text.strip(),
                        "price": item.find_element(By.XPATH, './td[4]').text.strip(),
                        "units": item.find_element(By.XPATH, './td[5]').text.strip(),
                        "amount": item.find_element(By.XPATH, './td[6]').text.strip(),
                    } for item in browser.find_elements(By.XPATH, '//tr[@class="reserveSales mod_middle"]')
                ]
            }
        } if sales_exists else None
    }