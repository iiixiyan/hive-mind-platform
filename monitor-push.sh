#!/bin/bash
# Hive Mind 自动监控与推送脚本
# 每30分钟执行一次，检测开发活动并自动推送

PROJECT_DIR="/root/.openclaw/workspace/hive-mind-platform"
LOG_FILE="/root/.openclaw/workspace/hive-mind-platform/monitor-push.log"
NOTIFY_LOG="/tmp/hive-mind-notifications.txt"
GIT_AUTHOR_NAME="${HIVE_MIND_AUTHOR_NAME:-iiixiyan}"
GIT_AUTHOR_EMAIL="${HIVE_MIND_AUTHOR_EMAIL:-iiixiyan@users.noreply.github.com}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

cd "$PROJECT_DIR" || exit 1

echo "========================================" | tee -a "$LOG_FILE"
echo "[$TIMESTAMP] Hive Mind 自动监控与推送" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 1. 检查 Git 状态
echo -e "\n【1. Git 状态检查】" | tee -a "$LOG_FILE"
CHANGES=$(git status --short)
echo "$CHANGES" | tee -a "$LOG_FILE"

if [ -z "$CHANGES" ]; then
    echo -e "${GREEN}✓ 工作树干净，无需提交${NC}" | tee -a "$LOG_FILE"
else
    echo -e "${YELLOW}⚠ 检测到未提交的更改${NC}" | tee -a "$LOG_FILE"

    # 提交更改
    echo -e "\n【2. 自动提交更改】" | tee -a "$LOG_FILE"
    COMMIT_MESSAGE="auto-commit: $(date '+%Y-%m-%d %H:%M:%S') - Automatic commit"
    git add -A
    git commit -m "$COMMIT_MESSAGE" --author="$GIT_AUTHOR_NAME <$GIT_AUTHOR_EMAIL>" 2>&1 | tee -a "$LOG_FILE"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 提交成功${NC}" | tee -a "$LOG_FILE"

        # 推送到 GitHub
        echo -e "\n【3. 推送到 GitHub】" | tee -a "$LOG_FILE"
        git push origin main 2>&1 | tee -a "$LOG_FILE"

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 推送成功${NC}" | tee -a "$LOG_FILE"

            # 记录通知
            echo "$TIMESTAMP - $(git log -1 --pretty=format:'%h - %s')" >> "$NOTIFY_LOG"
            echo -e "${GREEN}✓ 已记录开发活动通知${NC}" | tee -a "$LOG_FILE"
        else
            echo -e "${RED}✗ 推送失败${NC}" | tee -a "$LOG_FILE"
        fi
    else
        echo -e "${RED}✗ 提交失败${NC}" | tee -a "$LOG_FILE"
    fi
fi

# 4. 检查最近 1 小时是否有新提交
echo -e "\n【4. 最近 1 小时提交记录】" | tee -a "$LOG_FILE"
ONE_HOUR_AGO=$(date -d '1 hour ago' '+%Y-%m-%d %H:%M:%S')
if git log --since="$ONE_HOUR_AGO" --pretty=format:"%h - %an, %ar : %s" | head -5 | tee -a "$LOG_FILE"; then
    echo -e "${GREEN}✓ 检测到最近 1 小时的开发活动${NC}" | tee -a "$LOG_FILE"
else
    echo -e "${BLUE}ℹ 过去 1 小时无新提交${NC}" | tee -a "$LOG_FILE"
fi

# 5. 检查项目健康
echo -e "\n【5. 项目健康检查】" | tee -a "$LOG_FILE"
if [ -f "README.md" ] && [ -f "TASKS.md" ]; then
    echo -e "${GREEN}✓ 关键文档完整${NC}" | tee -a "$LOG_FILE"
else
    echo -e "${YELLOW}⚠ 缺少部分文档${NC}" | tee -a "$LOG_FILE"
fi

# 6. 当前状态
echo -e "\n【6. 当前状态】" | tee -a "$LOG_FILE"
echo "分支: $(git branch --show-current)" | tee -a "$LOG_FILE"
echo "提交: $(git rev-parse --short HEAD)" | tee -a "$LOG_FILE"

echo -e "\n========================================" | tee -a "$LOG_FILE"
