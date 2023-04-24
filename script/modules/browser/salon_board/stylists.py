from time import sleep

from selenium.webdriver.common.by import By


def get_stylists(
    browser
) -> []:
    browser.get("https://hoge.com/KLP/reserve/reserveList/")
    sleep(3)

    stylist_elements = browser.find_elements(By.XPATH, '//select[@id="stylistId"]/option')
    stylists = []

    for element in stylist_elements:
        stylist_id = element.get_attribute("value")
        name = element.text

        # 最初の要素（すべてのスタッフ）をスキップする
        if not stylist_id:
            continue

        stylists.append((stylist_id, {"name": name}))
    return stylists
