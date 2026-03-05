#!/bin/bash
# Hive Mind 开发监控脚本
# 每小时执行一次，检查开发活动

PROJECT_DIR="/root/.openclaw/workspace/hive-mind-platform"
LOG_FILE="/root/.openclaw/workspace/hive-mind-platform/monitor.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================" | tee -a "$LOG_FILE"
echo "[$TIMESTAMP] Hive Mind 开发监控检查" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

cd "$PROJECT_DIR" || exit 1

# 1. 检查 Git 状态
echo -e "\n【1. Git 状态检查】" | tee -a "$LOG_FILE"
git status --short | tee -a "$LOG_FILE"
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${GREEN}✓ 工作树干净，无未提交更改${NC}" | tee -a "$LOG_FILE"
else
    echo -e "${YELLOW}⚠ 检测到未提交的更改${NC}" | tee -a "$LOG_FILE"
fi

# 2. 检查最近 24 小时的提交
echo -e "\n【2. 最近 24 小时提交记录】" | tee -a "$LOG_FILE"
if git log --since="24 hours ago" --pretty=format:"%h - %an, %ar : %s" | head -10 | tee -a "$LOG_FILE"; then
    echo -e "${GREEN}✓ 检测到开发活动${NC}" | tee -a "$LOG_FILE"
else
    echo -e "${RED}✗ 过去 24 小时无提交记录${NC}" | tee -a "$LOG_FILE"
fi

# 3. 检查最近 7 天的提交
echo -e "\n【3. 最近 7 天提交记录】" | tee -a "$LOG_FILE"
git log --since="7 days ago" --pretty=format:"%h - %an, %ar : %s" --graph --all | head -20 | tee -a "$LOG_FILE"

# 4. 检查未合并的分支
echo -e "\n【4. 未合并的分支】" | tee -a "$LOG_FILE"
git branch --no-merged main | tee -a "$LOG_FILE"

# 5. 检查最近的 TAG
echo -e "\n【5. 最近 TAG】" | tee -a "$LOG_FILE"
git tag -l --sort=-creatordate | head -5 | tee -a "$LOG_FILE"

# 6. 检查文件变更统计
echo -e "\n【6. 最近提交的文件变更统计】" | tee -a "$LOG_FILE"
git log -1 --name-status --pretty=format:"" | sort | uniq -c | sort -rn | head -10 | tee -a "$LOG_FILE"

# 7. 检查项目健康状态（如果有）
echo -e "\n【7. 项目健康检查】" | tee -a "$LOG_FILE"
if [ -f "$PROJECT_DIR/README.md" ]; then
    echo "✓ README.md 存在" | tee -a "$LOG_FILE"
else
    echo "✗ README.md 缺失" | tee -a "$LOG_FILE"
fi

if [ -f "$PROJECT_DIR/TODO.md" ]; then
    echo "✓ TODO.md 存在" | tee -a "$LOG_FILE"
else
    echo "✗ TODO.md 缺失" | tee -a "$LOG_FILE"
fi

if [ -f "$PROJECT_DIR/TASKS.md" ]; then
    echo "✓ TASKS.md 存在" | tee -a "$LOG_FILE"
else
    echo "✗ TASKS.md 缺失" | tee -a "$LOG_FILE"
fi

echo -e "\n【8. 项目最新信息】" | tee -a "$LOG_FILE"
echo "当前分支: $(git branch --show-current)" | tee -a "$LOG_FILE"
echo "当前提交: $(git rev-parse --short HEAD)" | tee -a "$LOG_FILE"
echo "提交者: $(git log -1 --pretty=format:'%an')" | tee -a "$LOG_FILE"

echo -e "\n========================================" | tee -a "$LOG_FILE"
