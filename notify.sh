#!/bin/bash
# Hive Mind 开发活动通知脚本
# 发送 Telegram 通知

BOT_TOKEN="${HIVE_MIND_BOT_TOKEN:-}"
CHAT_ID="${HIVE_MIND_CHAT_ID:-}"

if [ -z "$BOT_TOKEN" ] || [ -z "$CHAT_ID" ]; then
    echo "错误: 未配置 HIVE_MIND_BOT_TOKEN 或 HIVE_MIND_CHAT_ID"
    exit 1
fi

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="/root/.openclaw/workspace/hive-mind-platform/monitor.log"
NOTIFICATION_FILE="/tmp/hive-mind-notifications.txt"

# 创建通知队列文件（如果不存在）
touch "$NOTIFICATION_FILE"

# 检查是否有新的通知
NEW_NOTIFIES=$(wc -l < "$NOTIFICATION_FILE" 2>/dev/null || echo 0)

if [ "$NEW_NOTIFIES" -eq 0 ]; then
    echo "无新的开发活动通知"
    exit 0
fi

# 读取最近的 3 条通知
LATEST_NOTIFS=$(head -n 3 "$NOTIFICATION_FILE")

# 发送通知
MESSAGE="🐝 Hive Mind 开发监控通知

⏰ 时间: $TIMESTAMP
📊 状态: 检测到开发活动

最近更新:
$LATEST_NOTIFS

---"
# (1) The original/evaluated original's top 3 line count is 3, but the context shows exactly 3 recent updates (aec1ff9, 1474e91, b0ce6b0).
# The original likely truncated a longer history.

curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
    -d "chat_id=$CHAT_ID" \
    -d "text=$MESSAGE" \
    -d "parse_mode=HTML" \
    -d "disable_web_page_preview=true" > /dev/null

if [ $? -eq 0 ]; then
    # 清空通知队列
    : > "$NOTIFICATION_FILE"
    echo "通知已发送" | tee -a "$LOG_FILE"
else
    echo "通知发送失败" | tee -a "$LOG_FILE"
fi
