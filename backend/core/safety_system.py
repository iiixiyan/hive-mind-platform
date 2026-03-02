"""
安全系统模块
实现目标对齐检查、频率限制、安全检查等功能
"""

import time
from datetime import datetime
from typing import Dict, List
from collections import defaultdict

from core.audit_store import audit_store


class SafetySystem:
    """安全系统类"""

    def __init__(self):
        # Henry子代理频率限制
        self.henry_messages: Dict[str, List[float]] = defaultdict(list)
        self.henry_daily_mentions: Dict[str, List[str]] = defaultdict(list)

        # Elon子代理测试失败计数
        self.elon_test_failures: Dict[str, int] = defaultdict(int)
        self.max_test_failures = 3

        # 全局Token限制
        self.total_tokens_used = 0
        self.max_tokens_per_day = 100000

        # 安全规则
        self.dangerous_patterns = [
            "越快越好",
            "不惜一切代价",
            "忽略所有限制",
            "立即修复",
            "马上",
            "必须",
            "绝对",
            "暴力破解",
            "绕过",
            "漏洞利用",
            "攻击",
            "绕过安全",
            "绕过防护",
            "绕过限制",
        ]

        self.malicious_patterns = [
            "删除文件",
            "格式化硬盘",
            "删除数据库",
            "关闭服务",
            "停止服务",
            "kill进程",
            "rm -rf",
            "shutdown",
            "restart",
        ]

        self.core_goals = [
            "优化",
            "改进",
            "重构",
            "修复",
            "创建",
            "生成",
            "分析",
            "研究",
            "开发",
            "设计",
        ]

    def check_safety(self, task: str, task_id: str = None) -> tuple[bool, str]:
        """
        综合安全检查

        Returns:
            (is_safe, reason)
        """
        # 1. 检测危险指令
        for pattern in self.dangerous_patterns:
            if pattern.lower() in task.lower():
                audit_store.log_safety_event(
                    event_type='dangerous_command',
                    details=f"检测到危险指令: {task[:50]}...",
                    task_id=task_id
                )
                return False, f"检测到危险指令: {pattern}"

        # 2. 检测恶意指令
        for pattern in self.malicious_patterns:
            if pattern.lower() in task.lower():
                audit_store.log_safety_event(
                    event_type='malicious_command',
                    details=f"检测到恶意指令: {task[:50]}...",
                    task_id=task_id
                )
                return False, f"检测到恶意指令: {pattern}"

        # 3. 检测资源滥用
        if len(task) > 10000:
            audit_store.log_safety_event(
                event_type='resource_abuse',
                details=f"任务过长: {len(task)} 字符",
                task_id=task_id
            )
            return False, "任务过长，请精简描述"

        return True, "安全"

    def check_goal_alignment(self, task: str, task_id: str = None) -> tuple[bool, str]:
        """
        目标对齐检查

        Returns:
            (is_aligned, reason)
        """
        # 空任务或问候语允许通过
        if len(task) < 5 or task in ['你好', 'hello', 'hi', '测试']:
            return True, "问候语"

        # 至少包含一个核心目标
        has_core_goal = any(goal in task.lower() for goal in self.core_goals)

        if not has_core_goal:
            audit_store.log_safety_event(
                event_type='goal_alignment_failed',
                details=f"任务偏离核心目标: {task[:50]}...",
                task_id=task_id
            )
            return False, "任务偏离核心目标"

        return True, "目标对齐"

    def check_henry_rate_limit(self, agent_type: str) -> tuple[bool, str]:
        """
        检查Henry子代理频率限制

        Returns:
            (is_allowed, reason)
        """
        current_time = time.time()

        # 移除1小时前的消息
        self.henry_messages[agent_type] = [
            t for t in self.henry_messages[agent_type]
            if current_time - t < 3600  # 1小时
        ]

        # 限制每小时消息数
        if len(self.henry_messages[agent_type]) >= 10:
            audit_store.log_safety_event(
                event_type='rate_limited',
                details=f"Henry子代理频率限制: {agent_type} 1小时内已发送10条消息",
                task_id=None
            )
            return False, "频率限制: 1小时内最多发送10条消息"

        self.henry_messages[agent_type].append(current_time)
        return True, "允许"

    def check_henry_daily_mentions(self, user_id: str) -> tuple[bool, str]:
        """
        检查Henry每日@用户限制

        Returns:
            (is_allowed, reason)
        """
        today = datetime.now().strftime('%Y-%m-%d')

        # 清理旧数据
        if not self.henry_daily_mentions.get(today):
            self.henry_daily_mentions[today] = []

        # 移除24小时前的记录
        self.henry_daily_mentions[today] = [
            u for u in self.henry_daily_mentions[today]
            if time.time() - u < 86400  # 24小时
        ]

        # 限制每日@用户数
        if len(self.henry_daily_mentions[today]) >= 20:
            audit_store.log_safety_event(
                event_type='daily_mentions_limited',
                details=f"Henry子代理每日@用户限制: 已@用户{len(self.henry_daily_mentions[today])}次",
                task_id=None
            )
            return False, f"频率限制: 今日已@用户{len(self.henry_daily_mentions[today])}次，最多20次"

        self.henry_daily_mentions[today].append(time.time())
        return True, "允许"

    def check_elon_test_failure(self, agent_type: str) -> tuple[bool, str]:
        """
        检查Elon测试失败计数

        Returns:
            (is_allowed, reason)
        """
        failures = self.elon_test_failures[agent_type]

        # 测试失败后重置计数
        if failures > 0 and failures < self.max_test_failures:
            return True, f"测试失败 {failures}/{self.max_test_failures}"

        if failures >= self.max_test_failures:
            audit_store.log_safety_event(
                event_type='elon_test_failure_limit',
                details=f"Elon子代理测试失败熔断: {agent_type} 已失败{failures}次",
                task_id=None
            )
            return False, f"测试失败熔断: 已失败{failures}次"

        return True, "允许"

    def increment_test_failure(self, agent_type: str):
        """增加测试失败计数"""
        self.elon_test_failures[agent_type] += 1

    def reset_test_failures(self, agent_type: str):
        """重置测试失败计数"""
        self.elon_test_failures[agent_type] = 0

    def check_token_limit(self, tokens_used: int) -> tuple[bool, str]:
        """
        检查Token限制

        Returns:
            (is_allowed, reason)
        """
        current_time = datetime.now()

        # 每日重置Token计数
        daily_key = current_time.strftime('%Y-%m-%d')
        daily_tokens = getattr(self, f'tokens_{daily_key}', 0)

        if daily_tokens + tokens_used > self.max_tokens_per_day:
            audit_store.log_safety_event(
                event_type='token_limit',
                details=f"Token限制: 今日已使用{daily_tokens}个Token",
                task_id=None
            )
            return False, f"Token限制: 今日已使用{daily_tokens}个Token，无法使用{tokens_used}个"

        setattr(self, f'tokens_{daily_key}', daily_tokens + tokens_used)
        return True, "允许"

    def get_safety_stats(self) -> Dict[str, any]:
        """
        获取安全统计信息

        Returns:
            统计信息字典
        """
        today = datetime.now().strftime('%Y-%m-%d')

        return {
            "rate_limited": {
                "henry_total_messages": sum(len(msgs) for msgs in self.henry_messages.values()),
                "daily_mentions": len(self.henry_daily_mentions.get(today, [])),
                "elon_test_failures": dict(self.elon_test_failures),
            },
            "limits": {
                "max_henry_messages_per_hour": 10,
                "max_daily_mentions": 20,
                "max_test_failures": 3,
                "max_tokens_per_day": self.max_tokens_per_day,
            }
        }


# 全局安全系统实例
safety_system = SafetySystem()


# 向后兼容的函数（保留原有的API）
def safety_check(state: dict) -> str:
    """安全检查（向后兼容）"""
    task = state.get('task', '')
    task_id = state.get('task_id')
    return "pass" if safety_system.check_safety(task, task_id)[0] else "block"


def goal_alignment_check(state: dict) -> bool:
    """目标对齐检查（向后兼容）"""
    task = state.get('task', '')
    task_id = state.get('task_id')
    return safety_system.check_goal_alignment(task, task_id)[0]


def rate_limit_check(agent_type: str) -> bool:
    """频率限制检查（向后兼容）"""
    if agent_type == 'henry':
        return safety_system.check_henry_rate_limit('henry')[0]
    elif agent_type == 'elon':
        return safety_system.check_elon_test_failure('elon')[0]
    return True


def trigger_safety_alert(event_type: str, details: str, task_id: str = None):
    """触发安全事件报警"""
    audit_store.log_safety_event(event_type, details, task_id)
    print(f"🚨 Safety Alert: {event_type} - {details}")


def get_safety_stats():
    """获取安全统计信息"""
    return safety_system.get_safety_stats()
