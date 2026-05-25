"""UI 测试专用 fixture —— 浏览器管理。"""
import pytest
import threading
import os
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from app.app import app


def _run_flask():
    """后台启动 Flask 供浏览器访问。"""
    app.run(port=5000, use_reloader=False)


BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture(scope="session")
def flask_server():
    """会话级：启动 Flask 后台服务。"""
    t = threading.Thread(target=_run_flask, daemon=True)
    t.start()
    import time
    time.sleep(0.5)
    return BASE_URL


@pytest.fixture(scope="function")
def driver(flask_server):
    """每个测试提供独立浏览器实例。"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(5)
    yield drv
    drv.quit()
