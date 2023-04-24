from datetime import datetime, timedelta
from time import sleep
import logging

from selenium.webdriver.common.by import By


def reservation_list_page(
    browser,
    search_range: (str, str)
):
    results = []
    set_conditions_on_search_page(
        browser,
        *search_range
    )
    browser.find_element(By.ID, "search").click()
    sleep(5)

    page_text = browser.find_element(
        By.CSS_SELECTOR,
        "#sortList > div.mod_column02.mt15.cf > div.columnBlock02 > div > p.page.mod_font01"
    )
    if page_text is None:
        logging.info("No result")
        return results

    logging.info(page_text.text)
    numerator, denominator = map(int, page_text.text.replace("ページ", "").split("/"))

    while numerator <= denominator:
        logging.info(f"Result page {numerator}/{denominator}")
        table = browser.find_element(By.ID, "resultList")
        rows = table.find_elements(By.XPATH, ".//tr")

        for row in rows:
            cols = row.find_elements(By.XPATH, ".//td")

            if len(cols) == 0:
                continue

            reserve_num = cols[2].find_element(By.XPATH, ".//a").text.split("(")[-1].replace(")", "")
            customer_name = cols[2].find_element(By.XPATH, ".//p[1]").text
            status = cols[1].text.replace("\n", "")
            staff = cols[3].text.replace("\n", "")
            visit_time_str = cols[0].find_element(By.XPATH, ".//a").text.replace("\n", "")

            visit_time = datetime.strptime(
                f"{str(datetime.now().year)}/{visit_time_str}",
                "%Y/%m/%d%H:%M"
            ) - timedelta(hours=9)

            logging.info(f" 予約番号: {reserve_num}, ステータス: {status}, 来店時間: {visit_time}, スタッフ:{staff}")

            results.append((
                reserve_num,
                {
                    "status": status,
                    "staff": staff,
                    "time": {
                        "start": visit_time
                    },
                    "name": customer_name
                }
            ))

        numerator += 1
        browser.get(f"https://hoge.com/KLP/reserve/reserveList/changePage?pn={(numerator + 1)}")
        sleep(5)

        logging.info(f"Total count: {len(rows)}")
    return results


def set_conditions_on_search_page(
        browser,
        start_ymd: str,
        end_ymd: str,
):
    # ページにアクセスしてIDのValueを設定
    browser.get("https://hoge.com/KLP/reserve/reserveList/")
    browser.execute_script("document.getElementById('rsvDateFrom').value = arguments[0]", start_ymd)
    browser.execute_script("document.getElementById('rsvDateTo').value = arguments[0]", end_ymd)
