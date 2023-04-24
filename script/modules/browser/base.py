import logging
from datetime import datetime

from selenium import webdriver


def create_browser():
    logging.info("Creating browser driver")
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=/home/seluser/userdata")
    options.add_argument("--profile-directory=Profile 1")
    options.add_argument("--headless")
    options.add_argument("--enable-file-cookies")
    options.add_argument("window-size=1400x1200")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")
    browser = webdriver.Remote(
        command_executor="http://selenium-hub:4444/wd/hub",
        desired_capabilities=options.to_capabilities(),
        options=options
    )
    browser.set_page_load_timeout(5)
    logging.info("Created browser driver")
    return browser


def take_screenshot(browser):
    dt_str = datetime.today().strftime("%Y%m%d%H%M%S")
    file_name = f"images/result_{dt_str}.png"
    browser.save_screenshot(file_name)
    logging.info(f"Taken screenshot : {file_name}")
