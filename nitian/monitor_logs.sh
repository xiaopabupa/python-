#!/bin/bash
# ============================================================
# 日志监控脚本 - 图书管理系统 (Flask)
# ============================================================
# 用法:
#   ./monitor_logs.sh                  # 实时监控（tail -f）
#   ./monitor_logs.sh --stats          # 输出统计摘要
#   ./monitor_logs.sh --errors         # 只看错误日志
#   ./monitor_logs.sh --report N       # 最近 N 分钟的日志报告
#   ./monitor_logs.sh --watch-keyword  # 监控指定关键词
# ============================================================

set -euo pipefail

# ---- 配置 ----
APP_LOG="${APP_LOG:-./app.log}"
ACCESS_LOG="${ACCESS_LOG:-./access.log}"
ERROR_LOG="${ERROR_LOG:-./error.log}"
FLASK_LOG="${FLASK_LOG:-./flask.log}"
LOG_DIR="$(dirname "$APP_LOG")"
MAX_LINES="${MAX_LINES:-200}"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ---- 工具函数 ----
color_print() {
    local color="$1"; shift
    echo -e "${color}$*${NC}"
}

divider() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

# ---- 确保日志文件存在 ----
init_logs() {
    mkdir -p "$LOG_DIR"
    for f in "$APP_LOG" "$ACCESS_LOG" "$ERROR_LOG" "$FLASK_LOG"; do
        touch "$f" 2>/dev/null || true
    done
}

# ---- 实时监控 ----
tail_logs() {
    color_print "$BOLD" "  实时日志监控中... (Ctrl+C 退出)"
    divider

    local files=()
    for f in "$APP_LOG" "$ACCESS_LOG" "$ERROR_LOG" "$FLASK_LOG"; do
        [ -f "$f" ] && files+=("$f")
    done

    if [ ${#files[@]} -eq 0 ]; then
        color_print "$YELLOW" "⚠ 没有找到日志文件"
        return
    fi

    tail -f -n "$MAX_LINES" "${files[@]}" 2>/dev/null | while IFS= read -r line; do
        local ts; ts="$(timestamp)"
        if echo "$line" | grep -qiE "error|exception|traceback|fail|critical"; then
            color_print "$RED"   "[$ts] ERROR | $line"
        elif echo "$line" | grep -qiE "warn|warning"; then
            color_print "$YELLOW" "[$ts] WARN  | $line"
        elif echo "$line" | grep -qiE "success|ok|200|201|done"; then
            color_print "$GREEN"  "[$ts] OK    | $line"
        elif echo "$line" | grep -qiE "GET|POST|PUT|DELETE|PATCH"; then
            color_print "$CYAN"   "[$ts] REQ   | $line"
        else
            echo "[$ts] INFO  | $line"
        fi
    done
}

# ---- 统计摘要 ----
show_stats() {
    color_print "$BOLD" "  日志统计摘要"
    divider

    local all_logs=()
    for f in "$APP_LOG" "$ACCESS_LOG" "$ERROR_LOG" "$FLASK_LOG"; do
        [ -f "$f" ] && all_logs+=("$f")
    done

    if [ ${#all_logs[@]} -eq 0 ]; then
        color_print "$YELLOW" "⚠ 没有找到日志文件"
        return
    fi

    # 总行数
    local total_lines; total_lines=$(cat "${all_logs[@]}" 2>/dev/null | wc -l)
    echo "  日志总行数:      $total_lines"

    # 错误数量
    local errors; errors=$(grep -ciE "error|exception|traceback|fail" "${all_logs[@]}" 2>/dev/null || echo 0)
    echo "  错误/异常数:     $errors"

    # 警告数量
    local warns; warns=$(grep -ciE "warn|warning" "${all_logs[@]}" 2>/dev/null || echo 0)
    echo "  警告数:          $warns"

    # HTTP 状态码分布
    echo ""
    color_print "$CYAN" "  HTTP 状态码分布:"
    for code in 200 201 301 302 400 401 403 404 500 502 503; do
        local count; count=$(grep -ocE "\b${code}\b" "${all_logs[@]}" 2>/dev/null || echo 0)
        if [ "$count" -gt 0 ]; then
            case $code in
                200|201) color_print "$GREEN"  "    $code → $count" ;;
                301|302) color_print "$CYAN"   "    $code → $count" ;;
                400|401|403|404) color_print "$YELLOW" "    $code → $count" ;;
                500|502|503) color_print "$RED"    "    $code → $count" ;;
            esac
        fi
    done

    # 端点访问 TOP 10
    echo ""
    color_print "$CYAN" "  热门端点 TOP 10:"
    grep -oE '"[A-Z]+ (/[^ ]*)' "${all_logs[@]}" 2>/dev/null \
        | awk '{print $2}' \
        | sort | uniq -c | sort -rn \
        | head -10 \
        | while read -r count path; do
            echo "    $count  $path"
        done

    # 文件大小
    echo ""
    color_print "$CYAN" "  日志文件大小:"
    for f in "$APP_LOG" "$ACCESS_LOG" "$ERROR_LOG" "$FLASK_LOG"; do
        if [ -f "$f" ]; then
            local size; size=$(du -h "$f" 2>/dev/null | cut -f1)
            echo "    $(basename "$f"): $size"
        fi
    done

    divider
    color_print "$GREEN" "  统计时间: $(timestamp)"
}

# ---- 只看错误 ----
show_errors() {
    color_print "$BOLD" "  错误日志 (最近 $MAX_LINES 条)"
    divider

    local all_logs=()
    for f in "$APP_LOG" "$ACCESS_LOG" "$ERROR_LOG" "$FLASK_LOG"; do
        [ -f "$f" ] && all_logs+=("$f")
    done

    grep -niE "error|exception|traceback|fail|critical" "${all_logs[@]}" 2>/dev/null \
        | tail -n "$MAX_LINES" \
        | while IFS= read -r line; do
            color_print "$RED" "$line"
        done

    local total; total=$(grep -ciE "error|exception|traceback|fail|critical" "${all_logs[@]}" 2>/dev/null || echo 0)
    echo ""
    echo "  错误总数: $total"
}

# ---- 最近 N 分钟报告 ----
recent_report() {
    local minutes="${1:-10}"
    color_print "$BOLD" "  最近 ${minutes} 分钟日志报告"
    divider

    local since; since=$(date -d "-${minutes} minutes" "+%Y-%m-%d %H:%M:%S" 2>/dev/null \
        || date -v "-${minutes}M" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)

    local all_logs=()
    for f in "$APP_LOG" "$ACCESS_LOG" "$ERROR_LOG" "$FLASK_LOG"; do
        [ -f "$f" ] && all_logs+=("$f")
    done

    if [ ${#all_logs[@]} -eq 0 ]; then
        color_print "$YELLOW" "⚠ 没有找到日志文件"
        return
    fi

    # awk 过滤时间范围内的日志行
    grep -hE "^\[?[0-9]{4}-[0-9]{2}-[0-9]{2}" "${all_logs[@]}" 2>/dev/null \
        | awk -v since="$since" '$0 >= since' \
        | tail -n "$MAX_LINES"
}

# ---- 关键词监控 ----
watch_keyword() {
    color_print "$BOLD" "  关键词监控模式"
    echo -n "  输入要监控的关键词 (回车确认): "
    read -r keyword
    if [ -z "$keyword" ]; then
        color_print "$YELLOW" "⚠ 关键词不能为空"
        return
    fi

    color_print "$GREEN" "  开始监控关键词: \"$keyword\" (Ctrl+C 退出)"
    divider

    local all_logs=()
    for f in "$APP_LOG" "$ACCESS_LOG" "$ERROR_LOG" "$FLASK_LOG"; do
        [ -f "$f" ] && all_logs+=("$f")
    done

    tail -f -n "$MAX_LINES" "${all_logs[@]}" 2>/dev/null \
        | grep --color=always -iE "$keyword" \
        | while IFS= read -r line; do
            echo "[$(timestamp)] $line"
        done
}

# ---- 后台日志守护进程 ----
start_daemon() {
    local pid_file="${PID_FILE:-./monitor_daemon.pid}"
    local alert_threshold="${ALERT_THRESHOLD:-10}"

    if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
        color_print "$YELLOW" "⚠ 守护进程已在运行 (PID: $(cat "$pid_file"))"
        return
    fi

    color_print "$GREEN" "  启动日志守护进程..."

    (
        echo $$ > "$pid_file"
        local count=0
        while true; do
            sleep 60
            local new_errors
            new_errors=$(grep -ciE "error|exception|traceback" "$APP_LOG" "$ERROR_LOG" 2>/dev/null || echo 0)

            if [ "$new_errors" -gt "$count" ]; then
                local diff=$((new_errors - count))
                if [ "$diff" -ge "$alert_threshold" ]; then
                    echo "[$(timestamp)] ⚠  ALERT: $diff 个新错误出现在过去1分钟内!" \
                        >> "${ALERT_LOG:-./alert.log}"
                fi
            fi
            count=$new_errors
        done
    ) &
    color_print "$GREEN" "  守护进程已启动 (PID: $!)"
}

stop_daemon() {
    local pid_file="${PID_FILE:-./monitor_daemon.pid}"
    if [ -f "$pid_file" ]; then
        local pid; pid=$(cat "$pid_file")
        if kill "$pid" 2>/dev/null; then
            color_print "$GREEN" "  守护进程已停止 (PID: $pid)"
        fi
        rm -f "$pid_file"
    else
        color_print "$YELLOW" "⚠ 没有找到运行中的守护进程"
    fi
}

# ---- 帮助 ----
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  (无参数)           实时彩色日志监控"
    echo "  --stats            输出日志统计摘要"
    echo "  --errors           只看错误/异常日志"
    echo "  --report N         最近 N 分钟的日志报告 (默认10分钟)"
    echo "  --watch-keyword    交互式关键词监控"
    echo "  --daemon-start     启动后台日志守护进程 (每分钟检查异常)"
    echo "  --daemon-stop      停止后台守护进程"
    echo "  --help             显示此帮助信息"
    echo ""
    echo "环境变量:"
    echo "  APP_LOG        应用日志文件 (默认: ./app.log)"
    echo "  ACCESS_LOG     访问日志文件 (默认: ./access.log)"
    echo "  ERROR_LOG      错误日志文件 (默认: ./error.log)"
    echo "  FLASK_LOG      Flask日志文件 (默认: ./flask.log)"
    echo "  MAX_LINES      最大显示行数 (默认: 200)"
    echo "  PID_FILE       守护进程PID文件 (默认: ./monitor_daemon.pid)"
    echo "  ALERT_THRESHOLD 告警阈值 (默认: 10)"
    echo ""
    echo "示例:"
    echo "  $0                        # 实时监控"
    echo "  $0 --stats                # 查看统计"
    echo "  $0 --report 30            # 最近30分钟报告"
    echo "  APP_LOG=myapp.log $0      # 监控指定日志文件"
}

# ---- 入口 ----
main() {
    init_logs

    case "${1:-}" in
        --stats)
            show_stats
            ;;
        --errors)
            show_errors
            ;;
        --report)
            recent_report "${2:-10}"
            ;;
        --watch-keyword)
            watch_keyword
            ;;
        --daemon-start)
            start_daemon
            ;;
        --daemon-stop)
            stop_daemon
            ;;
        --help|-h)
            show_help
            ;;
        "")
            tail_logs
            ;;
        *)
            color_print "$RED" "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
