#!/bin/bash
# 简单的端口和进程监控脚本

LOG_FILE="./monitor.log"

echo "===== 开始监控 $(date) ====="  >> $LOG_FILE

# 1. 检查端口：用 netstat 查看端口是否在监听
echo "--- 端口检查 ---"  >> $LOG_FILE

netstat -tln | grep ":80 "  > /dev/null
if [ $? -eq 0 ]; then
    echo "[正常] 端口 80 (Web) 在监听"  >> $LOG_FILE
else
    echo "[告警] 端口 80 (Web) 未监听！" >> $LOG_FILE
fi

netstat -tln | grep ":3306 "  > /dev/null
if [ $? -eq 0 ]; then
    echo "[正常] 端口 3306 (MySQL) 在监听"  >> $LOG_FILE
else
    echo "[告警] 端口 3306 (MySQL) 未监听！" >> $LOG_FILE
fi

# 2. 检查进程：用 ps 查看进程是否存在
echo "--- 进程检查 ---"  >> $LOG_FILE

ps aux | grep "nginx" | grep -v "grep" > /dev/null
if [ $? -eq 0 ]; then
    echo "[正常] 进程 nginx 在运行"  >> $LOG_FILE
else
    echo "[告警] 进程 nginx 未运行！" >> $LOG_FILE
fi

ps aux | grep "mysqld" | grep -v "grep" > /dev/null
if [ $? -eq 0 ]; then
    echo "[正常] 进程 mysqld 在运行"  >> $LOG_FILE
else
    echo "[告警] 进程 mysqld 未运行！" >> $LOG_FILE
fi

echo "===== 检查完毕 $(date) ====="  >> $LOG_FILE
echo "" >> $LOG_FILE

# 把日志也打印到屏幕上
cat $LOG_FILE | tail -12
