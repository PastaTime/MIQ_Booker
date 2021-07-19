import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException

from definitions import DRIVER_BIN, MIQ_WEBSITE, OUTPUT_FILE


def get_frames(driver):
    return driver.find_elements_by_xpath('//div[@class="pika-lendar"]')


def get_month(frame):
    month, year = frame.find_elements_by_class_name("pika-label")
    return datetime.datetime.strptime(month.text, "%B").month, int(year.text)


def get_day_frames(frame):
    return frame.find_elements_by_xpath(".//td[@data-day]")


def get_day_number(day_frame):
    return int(day_frame.text)


def day_available(day_frame):
    return "has-event" in day_frame.get_attribute("class").split()


def scan_days(driver, calender):
    frames = get_frames(driver)
    for frame in frames:
        day_frames = get_day_frames(frame)
        for day_frame in day_frames:
            if not day_available(day_frame):
                continue
            month, year = get_month(frame)
            day = get_day_number(day_frame)
            calender.add((day, month, year))


def get_next_button(driver):
    return driver.find_element_by_xpath('//button[@class="pika-next"]')


def get_check_flights_element(driver):
    return driver.find_element_by_xpath('//*[text()[contains(., "Check flight availability")]]')


def click_next_button(driver):
    button = get_next_button(driver)
    button.click()


def scroll_into_view(driver):
    button = get_next_button(driver)
    driver.execute_script("arguments[0].scrollIntoView(true);", button)
    time.sleep(1)


def scan_miq(driver):
    results = set()

    driver.get(MIQ_WEBSITE)
    time.sleep(0.5)
    scroll_into_view(driver)
    while True:
        try:
            scan_days(driver, results)
            click_next_button(driver)
        except NoSuchElementException:
            break
    return results


if __name__ == '__main__':
    f = open(OUTPUT_FILE, "a")
    try:
        chrome_options = Options()
        driver = webdriver.Chrome(DRIVER_BIN, options=chrome_options)
        while True:
            calender = scan_miq(driver)
            if len(calender) != 0:
                f.write(f"{datetime.datetime.now()}|{calender}\n")
                f.flush()
                print(f"{datetime.datetime.now()}\n")
            time.sleep(5)
    except KeyboardInterrupt:
        f.close()
