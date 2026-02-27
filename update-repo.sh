#!/bin/bash

# Hive Mind项目自动更新脚本
# 每30分钟执行一次

echo "========================================" | tee -a /tmp/hive-mind-updates.log
echo "Hive Mind Auto-Update - $(date)" | tee -a /tmp/hive-mind-updates.log
echo "========================================" | tee -a /tmp/hive-mind-updates.log

# 进入项目目录
cd /root/.openclaw/workspace/hive-mind-platform

# 检查是否有更改
if git diff --quiet && git diff --cached --quiet; then
    echo "No changes detected" | tee -a /tmp/hive-mind-updates.log
else
    # 提交更改
    git add -A
    git commit -m "auto-update: $(date '+%Y-%m-%d %H:%M:%S') - Automatic commit"

    # 推送到GitHub
    echo "Pushing to GitHub..." | tee -a /tmp/hive-mind-updates.log
    git push origin main

    if [ $? -eq 0 ]; then
        echo "✅ Successfully pushed to GitHub!" | tee -a /tmp/hive-mind-updates.log
    else
        echo "❌ Failed to push to GitHub" | tee -a /tmp/hive-mind-updates.log
    fi
fi

echo "" | tee -a /tmp/hive-mind-updates.log
