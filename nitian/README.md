# 自动化测试框架

基于 Pytest + Selenium + Allure 的自动化测试入门项目，适合软件测试实习生作为面试作品。

## 技术栈

- **Flask** — 被测 Web 应用
- **Selenium** — 浏览器 UI 自动化
- **Pytest** — 测试框架
- **Allure** — 测试报告
- **Page Object 模式** — UI 测试设计模式

## 项目结构

```
├── app/                        # 被测应用
│   ├── app.py                  # Flask 应用（登录 + API）
│   └── templates/
│       ├── login.html          # 登录页面
│       └── welcome.html        # 欢迎页面
├── tests/
│   ├── conftest.py             # 全局 fixture
│   ├── ui/                     # UI 自动化测试
│   │   ├── conftest.py         # 浏览器 fixture
│   │   ├── pages/
│   │   │   ├── base_page.py    # Page Object 基类
│   │   │   ├── login_page.py   # 登录页对象
│   │   │   └── welcome_page.py # 欢迎页对象
│   │   └── test_login_ui.py    # 登录 UI 测试
│   └── api/
│       └── test_api.py         # 登录接口测试
├── pytest.ini                  # Pytest 配置
├── requirements.txt
└── README.md
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行接口测试（不需要浏览器）
pytest tests/api/ -v

# 3. 运行 UI 测试（需要 Chrome 浏览器）
pytest tests/ui/ -v

# 4. 运行冒烟测试
pytest -m smoke -v

# 5. 生成 Allure 报告
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

## 测试账号

| 用户名 | 密码 |
|--------|------|
| admin  | admin123 |
| test   | test123 |

## 测试覆盖

**UI 测试（5 个用例）**
- 正常登录 → 验证跳转欢迎页
- 错误密码 / 空用户名 / 空密码（参数化）
- 退出登录 → 验证回到登录页

**接口测试（5 个用例）**
- 正常登录 → 返回 200 和用户名
- 错误密码 → 返回 401
- 空字段（参数化 3 组）

## 核心知识点

| 知识点 | 代码位置 |
|--------|---------|
| Page Object 模式 | `tests/ui/pages/` |
| 显式等待 | `base_page.py` → `wait_visible()` |
| fixture 分层 | `tests/conftest.py` + `tests/ui/conftest.py` |
| 参数化测试 | `test_login_ui.py` + `test_api.py` |
| Allure 报告 | `@allure.feature` `@allure.story` `@allure.step` |
| 三层断言 | 状态码 → 数据结构 → 业务内容 |
