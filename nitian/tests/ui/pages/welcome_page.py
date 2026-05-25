"""欢迎页 Page Object。"""
from selenium.webdriver.common.by import By
from .base_page import BasePage


class WelcomePage(BasePage):
    WELCOME_USER = (By.ID, "welcome-user")
    LOGOUT_BUTTON = (By.ID, "logout-btn")

    def get_welcome_text(self):
        return self.get_text(self.WELCOME_USER)
