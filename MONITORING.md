# Hive Mind 开发监控系统

## 📊 监控概览

Hive Mind 项目已配置每小时定时监控，持续跟踪开发活动。

## 🕐 执行时间

- **监控频率**: 每小时整点执行
- **Cron 表达式**: `0 * * * *`
- **日志位置**: `/root/.openclaw/workspace/hive-mind-platform/monitor.log`

## 🔧 监控项目

### 1. Git 状态检查
- 检查未提交的更改
- 监控工作树状态

### 2. 提交记录监控
- 过去 24 小时提交历史
- 过去 7 天完整提交轨迹
- 自动提交识别

### 3. 分支管理
- 未合并到 main 的分支
- 最新 TAG 信息
- 分支发展状态

### 4. 文件变更统计
- 最近提交的文件类型
- 变更模式分析

### 5. 项目健康检查
- README.md 存在性
- TODO.md 存在性
- TASKS.md 存在性

## 📋 脚本说明

### monitor.sh
主监控脚本，执行所有检查项目。

**功能:**
- Git 状态分析
- 提交历史追踪
- 分支管理监控
- 项目健康检查
- 彩色日志输出

**执行方式:**
```bash
/root/.openclaw/workspace/hive-mind-platform/monitor.sh
```

### notify.sh
通知脚本，用于发送 Telegram 通知。

**环境变量:**
- `HIVE_MIND_BOT_TOKEN`: Telegram Bot Token
- `HIVE_MIND_CHAT_ID`: 目标聊天 ID

**使用场景:**
- 检测到新的开发活动时发送通知
- 可扩展为更复杂的告警规则

**配置方式:**
```bash
export HIVE_MIND_BOT_TOKEN="your_bot_token"
export HIVE_MIND_CHAT_ID="your_chat_id"
```

## 📈 日志示例

```bash
========================================
[2026-03-05 11:43:17] Hive Mind 开发监控检查
========================================

【1. Git 状态检查】
?? monitor.log
?? monitor.sh

【2. 最近 24 小时提交记录】
* aec1ff9 - iiixiyan, 3 days ago : feat: 重构安全系统到独立模块
* 1474e91 - iiixiyan, 3 days ago : chore: 更新构建产物和缓存文件

【3. 最近 7 天提交记录】
* aec1ff9 - iiixiyan, 3 days ago : feat: 重构安全系统到独立模块
...

【7. 项目健康检查】
✓ README.md 存在
✓ TODO.md 存在
✓ TASKS.md 存在

【8. 项目最新信息】
当前分支: main
当前提交: aec1ff9
提交者: iiixiyan

========================================
```

## 🔄 扩展建议

### 1. 添加告警规则
可以扩展 `monitor.sh` 添加更复杂的告警逻辑:
- 连续 3 小时无提交 → 发送提醒
- 检测到危险提交 → 立即通知
- 超过 5 天无更新 → 重度告警

### 2. 集成 Telegram 通知
配置环境变量后,自动发送开发活动通知:
```bash
export HIVE_MIND_BOT_TOKEN="your_token"
export HIVE_MIND_CHAT_ID="your_chat_id"
```

### 3. 数据统计仪表板
创建前端页面展示:
- 开发活动趋势图
- 提交频率统计
- 开发者贡献排行

### 4. 集成 CI/CD
将监控结果与 CI/CD 管道集成:
- 开发活动状态作为 pipeline 状态
- 自动生成周报/月报

## 📝 相关文件

- `monitor.sh` - 主监控脚本
- `notify.sh` - 通知脚本
- `monitor.log` - 监控日志
- `CRON.md` - Cron 配置说明

## 🎯 维护说明

### 查看最新监控结果
```bash
tail -f /root/.openclaw/workspace/hive-mind-platform/monitor.log
```

### 手动执行监控
```bash
cd /root/.openclaw/workspace/hive-mind-platform
./monitor.sh
```

### 更新 Cron 任务
```bash
crontab -l > crontab_backup.txt
crontab -l | { cat; echo "0 * * * * /root/.openclaw/workspace/hive-mind-platform/monitor.sh >> /root/.openclaw/workspace/hive-mind-platform/monitor.log 2>&1"; } | crontab -
```

### 查看当前 Cron 配置
```bash
crontab -l
```

---

**创建时间**: 2026-03-05
**最后更新**: 2026-03-05
**状态**: ✅ 运行中
