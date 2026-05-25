"""UI 自动化测试 —— 登录功能。"""
import allure
import pytest
from .pages.login_page import LoginPage
from .pages.welcome_page import WelcomePage


@allure.feature("用户登录")
class TestLoginUI:

    @allure.story("正常登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_login_success(self, driver):
        """输入正确的账号密码，登录成功跳转到欢迎页。"""
        with allure.step("打开登录页面"):
            login_page = LoginPage(driver).load()

        with allure.step("输入账号密码并登录"):
            login_page.login("admin", "admin123")

        with allure.step("验证登录成功——显示欢迎信息"):
            welcome_page = WelcomePage(driver)
            welcome_page.wait_visible(WelcomePage.WELCOME_USER)
            assert "admin" in welcome_page.get_welcome_text()
            assert "/welcome" in welcome_page.get_url()

    @allure.story("登录失败")
    @pytest.mark.parametrize("username, password, expected_error", [
        ("admin", "wrong", "用户名或密码错误"),
        ("", "admin123", "用户名不能为空"),
        ("admin", "", "密码不能为空"),
    ])
    def test_login_failed(self, driver, username, password, expected_error):
        """参数化测试：错误密码、空用户名、空密码三种失败场景。"""
        login_page = LoginPage(driver).load()
        login_page.login(username, password)
        assert expected_error in login_page.get_error()

    @allure.story("退出登录")
    @pytest.mark.smoke
    def test_logout(self, driver):
        """登录后退出，应回到登录页。"""
        # 先登录
        LoginPage(driver).load().login("admin", "admin123")
        WelcomePage(driver).wait_visible(WelcomePage.WELCOME_USER)

        # 退出
        driver.get("http://127.0.0.1:5000/logout")
        login_page = LoginPage(driver)
        login_page.wait_visible(LoginPage.LOGIN_BUTTON)
        assert "/login" in login_page.get_url()
