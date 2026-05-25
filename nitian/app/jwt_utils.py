import jwt
import datetime
from functools import wraps
from flask import request, jsonify, g

SECRET_KEY = "nitian-jwt-secret-key-2024-must-be-32bytes"
EXPIRATION_HOURS = 12


def generate_token(username: str) -> str:
    """生成 JWT 令牌，有效期为 EXPIRATION_HOURS 小时。"""
    payload = {
        "username": username,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=EXPIRATION_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> dict | None:
    """解析并校验 JWT 令牌，成功返回 payload，失败返回 None。"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def login_required(f):
    """装饰器：从 Authorization 头提取 Bearer Token 并校验，校验通过后将 username 存入 g 对象。"""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"code": 401, "message": "缺少或格式错误的认证令牌"}), 401

        token = auth_header.split(" ", 1)[1]
        payload = verify_token(token)
        if payload is None:
            return jsonify({"code": 401, "message": "令牌无效或已过期，请重新登录"}), 401

        g.username = payload.get("username")
        return f(*args, **kwargs)

    return decorated
