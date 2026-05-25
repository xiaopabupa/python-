"""全局测试 fixture。"""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.app import app as flask_app


@pytest.fixture(scope="session")
def app():
    """Flask 测试应用（会话级）。"""
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture(scope="session")
def client(app):
    """Flask 测试客户端，用于接口测试。"""
    return app.test_client()
