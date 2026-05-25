"""接口测试 —— 登录 API 及 JWT 鉴权。"""
import allure
import pytest


@allure.feature("登录接口")
class TestLoginAPI:

    @allure.story("正常登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_login_success(self, client):
        """正确账号密码，返回 200、用户名和 JWT token。"""
        resp = client.post("/api/login", json={
            "username": "admin", "password": "admin123"
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["code"] == 200
        assert data["data"]["username"] == "admin"
        assert "token" in data["data"]
        assert len(data["data"]["token"]) > 0

    @allure.story("登录失败")
    def test_login_wrong_password(self, client):
        """错误密码，返回 401。"""
        resp = client.post("/api/login", json={
            "username": "admin", "password": "wrong"
        })
        assert resp.status_code == 401
        assert "错误" in resp.get_json()["message"]

    @allure.story("参数校验")
    @pytest.mark.parametrize("payload, expected_msg", [
        ({"username": "", "password": "admin123"}, "用户名和密码不能为空"),
        ({"username": "admin", "password": ""}, "用户名和密码不能为空"),
        ({}, "用户名和密码不能为空"),
    ])
    def test_login_empty_fields(self, client, payload, expected_msg):
        """空用户名、空密码、空请求体三种情况。"""
        resp = client.post("/api/login", json=payload)
        assert resp.status_code == 400
        assert expected_msg in resp.get_json()["message"]


@allure.feature("JWT 鉴权")
class TestJWTAuth:

    @pytest.fixture
    def token(self, client):
        """登录获取有效 token 供后续测试使用。"""
        resp = client.post("/api/login", json={
            "username": "admin", "password": "admin123"
        })
        return resp.get_json()["data"]["token"]

    @allure.story("携带有效 Token 访问受保护接口")
    def test_access_with_valid_token(self, client, token):
        """Authorization 头携带有效 token，返回 200 和用户信息。"""
        resp = client.get("/api/welcome", headers={
            "Authorization": f"Bearer {token}"
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["code"] == 200
        assert data["data"]["username"] == "admin"

    @allure.story("未携带 Token 访问受保护接口")
    def test_access_without_token(self, client):
        """请求头无 Authorization，返回 401。"""
        resp = client.get("/api/welcome")
        assert resp.status_code == 401
        assert "认证" in resp.get_json()["message"]

    @allure.story("携带无效 Token 访问受保护接口")
    def test_access_with_invalid_token(self, client):
        """携带伪造 token，返回 401。"""
        resp = client.get("/api/welcome", headers={
            "Authorization": "Bearer invalid.token.here"
        })
        assert resp.status_code == 401
        assert "无效" in resp.get_json()["message"]

    @allure.story("Authorization 头格式错误")
    @pytest.mark.parametrize("header_value", [
        "",
        "Token some-token",
        "Bearer",
    ])
    def test_access_with_malformed_header(self, client, header_value):
        """非标准 Bearer 格式，均返回 401。"""
        resp = client.get("/api/welcome", headers={
            "Authorization": header_value
        })
        assert resp.status_code == 401
