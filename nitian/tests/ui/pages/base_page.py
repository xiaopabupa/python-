"""Page Object 基类 —— 封装通用 Selenium 操作。"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class BasePage:
    BASE_URL = "http://127.0.0.1:5000"
    TIMEOUT = 10

    def __init__(self, driver):
        self.driver = driver

    def navigate(self, path="/"):
        self.driver.get(f"{self.BASE_URL}{path}")

    def find(self, locator):
        return self.driver.find_element(*locator)

    def click(self, locator):
        self.find(locator).click()

    def type(self, locator, text):
        el = self.find(locator)
        el.clear()
        el.send_keys(text)

    def get_text(self, locator):
        return self.find(locator).text

    def wait_visible(self, locator, timeout=None):
        return WebDriverWait(self.driver, timeout or self.TIMEOUT).until(
            EC.visibility_of_element_located(locator)
        )

    def is_displayed(self, locator, timeout=3):
        try:
            self.wait_visible(locator, timeout)
            return True
        except TimeoutException:
            return False

    def get_url(self):
        return self.driver.current_url
