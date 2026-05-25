"""图书管理系统 - 自动化测试目标应用。"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
from jwt_utils import generate_token, verify_token, login_required

app = Flask(__name__)
app.secret_key = "test-secret-key"

# 模拟用户数据
USERS = {"admin": "admin123", "test": "test123"}


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if not username:
            error = "用户名不能为空"
        elif not password:
            error = "密码不能为空"
        elif username in USERS and USERS[username] == password:
            session["username"] = username
            return redirect(url_for("welcome"))
        else:
            error = "用户名或密码错误"
    return render_template("login.html", error=error)


@app.route("/welcome")
def welcome():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("welcome.html", username=session["username"])


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


# ---- API 端点（接口测试用）----

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")
    if not username or not password:
        return jsonify({"code": 400, "message": "用户名和密码不能为空"}), 400
    if username in USERS and USERS[username] == password:
        token = generate_token(username)
        return jsonify({
            "code": 200,
            "message": "登录成功",
            "data": {"username": username, "token": token}
        })
    return jsonify({"code": 401, "message": "用户名或密码错误"}), 401


@app.route("/api/welcome", methods=["GET"])
@login_required
def api_welcome():
    """受 JWT 保护的接口，返回当前登录用户的信息。"""
    return jsonify({
        "code": 200,
        "message": "欢迎回来",
        "data": {"username": g.username}
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
