"""读取 allure-results JSON，生成独立 HTML 测试报告。"""
import json
import os
import glob
from datetime import datetime

RESULTS_DIR = "reports/allure-results"
OUTPUT_PATH = "reports/test_report.html"

def collect_results():
    """收集所有 result.json 文件并分类。"""
    results = []
    for f in glob.glob(os.path.join(RESULTS_DIR, "*-result.json")):
        with open(f, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            if "feature" not in str(data.get("labels", [])):
                continue
            results.append(data)
    return sorted(results, key=lambda x: x.get("fullName", ""))

def build_html(results):
    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")
    total = len(results)
    pass_rate = (passed / total * 100) if total > 0 else 0

    # 按 feature 分组
    features = {}
    for r in results:
        feat = next((l["value"] for l in r.get("labels", []) if l["name"] == "feature"), "未分类")
        story = next((l["value"] for l in r.get("labels", []) if l["name"] == "story"), "—")
        features.setdefault(feat, []).append((story, r))

    # 渲染统计卡片
    status_color = "#28a745" if passed == total else ("#ffc107" if passed > 0 else "#dc3545")
    rows_html = ""
    for feat, items in features.items():
        rows_html += f'<tr><td colspan="5" class="feature-header">{feat}</td></tr>'
        for story, r in items:
            status_badge = '<span class="badge pass">PASSED</span>' if r["status"] == "passed" else '<span class="badge fail">FAILED</span>'
            duration = (r.get("stop", 0) - r.get("start", 0)) / 1000.0
            params = r.get("parameters", [])
            param_text = ", ".join(f"{p['name']}={p['value']}" for p in params) if params else "—"
            desc = r.get("description", "")
            rows_html += f"""
            <tr>
                <td class="case-name">{r['name']}</td>
                <td>{story}</td>
                <td>{param_text}</td>
                <td>{duration:.3f}s</td>
                <td>{status_badge}</td>
            </tr>
            <tr><td colspan="5" class="desc-cell">{desc}</td></tr>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>nitian 自动化测试报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f6fa; color: #333; }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 32px 20px; }}
        h1 {{ font-size: 26px; margin-bottom: 8px; }}
        .subtitle {{ color: #666; font-size: 14px; margin-bottom: 28px; }}
        .stats {{ display: flex; gap: 20px; margin-bottom: 32px; }}
        .stat-card {{ background: white; border-radius: 10px; padding: 22px 28px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); flex: 1; text-align: center; }}
        .stat-card .num {{ font-size: 36px; font-weight: 700; color: {status_color}; }}
        .stat-card .label {{ font-size: 13px; color: #888; margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
        th {{ background: #f0f1f4; padding: 12px 16px; text-align: left; font-size: 12px; text-transform: uppercase; color: #666; letter-spacing: 0.5px; }}
        td {{ padding: 12px 16px; border-bottom: 1px solid #eee; font-size: 14px; }}
        .feature-header {{ background: #eef1f7; font-weight: 600; font-size: 14px; color: #444; }}
        .case-name {{ font-family: 'SF Mono', 'Fira Code', monospace; font-size: 13px; max-width: 380px; word-break: break-all; }}
        .desc-cell {{ color: #999; font-size: 12px; padding-top: 0; padding-bottom: 16px; border-bottom: 1px solid #eee; }}
        .badge {{ display: inline-block; padding: 3px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }}
        .badge.pass {{ background: #d4edda; color: #155724; }}
        .badge.fail {{ background: #f8d7da; color: #721c24; }}
        .footer {{ text-align: center; color: #aaa; font-size: 12px; margin-top: 24px; }}
    </style>
</head>
<body>
<div class="container">
    <h1>nitian 自动化测试报告</h1>
    <p class="subtitle">Pytest + Selenium + Allure &nbsp;|&nbsp; 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

    <div class="stats">
        <div class="stat-card"><div class="num">{total}</div><div class="label">总用例数</div></div>
        <div class="stat-card"><div class="num">{passed}</div><div class="label">通过</div></div>
        <div class="stat-card"><div class="num">{failed}</div><div class="label">失败</div></div>
        <div class="stat-card"><div class="num">{pass_rate:.1f}%</div><div class="label">通过率</div></div>
    </div>

    <table>
        <thead>
            <tr><th>用例名称</th><th>测试场景</th><th>参数</th><th>耗时</th><th>状态</th></tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>

    <p class="footer">nitian — 自动化测试框架 · Flask + Selenium + Pytest + Allure</p>
</div>
</body>
</html>"""

if __name__ == "__main__":
    results = collect_results()
    html = build_html(results)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"报告已生成: {OUTPUT_PATH}  ({len(results)} 个用例)")
