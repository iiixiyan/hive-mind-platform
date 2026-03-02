"""
Agent定义与状态管理 - v0.1.1
"""

from typing import TypedDict, List, Annotated, Literal, Optional
from langgraph.graph.message import add_messages
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from core.workflows import ECHO_WORKFLOW, ELON_WORKFLOW, HENRY_WORKFLOW
from core.audit_store import audit_store
from core.safety_system import safety_system

# Agent类型
class AgentType:
    ECHO = "echo"
    ELON = "elon"
    HENRY = "henry"
    ARCHITECT = "architect"
    CODER = "coder"
    QA = "qa"
    REVIEWER = "reviewer"
    RESEARCHER = "researcher"
    WRITER = "writer"
    NETWORKER = "networker"

# Agent状态
class AgentState(TypedDict):
    # 通用字段
    messages: Annotated[List[str], add_messages]
    current_agent: str
    task: str
    status: str  # running, thinking, blocked, idle
    progress: float
    task_id: Optional[str]  # 任务ID，用于审计日志
    audit_logs: List[str]  # 审计日志列表

    # Echo专用字段
    tech_tasks: List[dict]
    market_tasks: List[dict]
    progress_report: str

    # Elon专用字段
    code: str
    tests: str
    architecture: dict
    elon_output: str

    # Henry专用字段
    research: str
    content: str
    henry_output: str
    networking: str

    # 安全字段
    safety_flags: List[str]
    goal_alignment: bool

# Agent工作流映射
AGENT_WORKFLOWS = {
    AgentType.ECHO: ECHO_WORKFLOW,
    AgentType.ELON: ELON_WORKFLOW,
    AgentType.HENRY: HENRY_WORKFLOW,
}

# Agent配置
AGENT_CONFIG = {
    AgentType.ECHO: {
        "name": "Echo",
        "role": "首席助理",
        "personality": "30岁英国剑桥毕业的天才产品经理",
        "capabilities": ["意图翻译", "上下文管理", "任务分发"]
    },
    AgentType.ELON: {
        "name": "Elon",
        "role": "CTO",
        "personality": "40岁硅谷硬核极客",
        "capabilities": ["架构设计", "代码开发", "测试", "审查"]
    },
    AgentType.HENRY: {
        "name": "Henry",
        "role": "CMO",
        "personality": "28岁社区运营专家",
        "capabilities": ["社区调研", "内容创作", "社交互动"]
    },
    AgentType.ARCHITECT: {
        "name": "Architect",
        "role": "架构师",
        "capabilities": ["技术选型", "模块设计", "API定义"]
    },
    AgentType.CODER: {
        "name": "Coder",
        "role": "开发者",
        "capabilities": ["代码开发", "实现架构设计"]
    },
    AgentType.QA: {
        "name": "QA",
        "role": "测试员",
        "capabilities": ["单元测试", "调试", "自修复"]
    },
    AgentType.REVIEWER: {
        "name": "Reviewer",
        "role": "审查员",
        "capabilities": ["代码审查", "安全检查", "质量评估"]
    },
    AgentType.RESEARCHER: {
        "name": "Researcher",
        "role": "调研员",
        "capabilities": ["GitHub调研", "社区热点分析", "市场研究"]
    },
    AgentType.WRITER: {
        "name": "Writer",
        "role": "内容创作",
        "capabilities": ["PR描述", "Release Notes", "博客文章"]
    },
    AgentType.NETWORKER: {
        "name": "Networker",
        "role": "社交专员",
        "capabilities": ["社区互动", "@提及", "评论回复"]
    },
}

# 创建LLM实例
def get_llm(agent_type: str):
    """获取对应Agent的LLM实例"""
    if agent_type in [AgentType.ELON, AgentType.ARCHITECT, AgentType.CODER, AgentType.QA]:
        return ChatOpenAI(model="gpt-4", temperature=0.2)
    else:
        return ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0.3
        )

# 获取Agent配置
def get_agent_config(agent_type: str) -> dict:
    """获取Agent配置"""
    return AGENT_CONFIG.get(agent_type, {
        "name": "Unknown",
        "role": "未知",
        "capabilities": []
    })

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict

# 安全检查函数
def safety_check(state: AgentState) -> Literal["pass", "fail", "block"]:
    """安全检查（使用新的安全系统）"""
    task = state.get('task', '')
    task_id = state.get('task_id')

    is_safe, reason = safety_system.check_safety(task, task_id)
    if not is_safe:
        return "block"

    return "pass"

# 目标对齐检查
def goal_alignment_check(state: AgentState) -> bool:
    """目标对齐检查"""
    task = state.get('task', '')

    # 检查是否偏离核心目标
    core_goals = [
        "优化",
        "改进",
        "重构",
        "修复",
        "创建",
        "生成",
        "分析",
        "研究"
    ]

    # 至少包含一个核心目标
    has_core_goal = any(goal in task.lower() for goal in core_goals)

    if not has_core_goal and '你好' not in task and '测试' not in task:
        return False

    return True

def generate_audit_log(task_id: str, agent_type: str, action: str, details: str) -> str:
    """生成审计日志"""
    timestamp = datetime.now().isoformat()
    return f"[{timestamp}] {task_id} | {agent_type} | {action} | {details}"

def rate_limit_check(agent_type: str) -> bool:
    """频率限制检查"""
    # Henry子代理限制
    if agent_type == AgentType.NETWORKER:
        return rate_limiter.check_henry_rate_limit(agent_type)

    # Elon子代理熔断
    if agent_type in [AgentType.CODER, AgentType.QA]:
        return rate_limiter.check_elon_test_failure(agent_type)

    return True

# 获取审计日志
def get_audit_logs(task_id: str, limit: int = 100) -> List[dict]:
    """获取任务审计日志"""
    # 实际实现需要存储到数据库
    # 这里返回空列表作为占位符
    return []

# 安全事件报警
def trigger_safety_alert(event_type: str, details: str, task_id: str = None):
    """触发安全事件报警"""
    alert = {
        "type": event_type,
        "details": details,
        "task_id": task_id,
        "timestamp": datetime.now().isoformat()
    }

    # 实际实现需要发送到监控系统
    print(f"🚨 Safety Alert: {alert}")

    return alert

# 获取所有Agent类型
def get_all_agent_types():
    """获取所有Agent类型"""
    return list(AGENT_CONFIG.keys())

# 获取Agent工作流
def get_agent_workflow(agent_type: str):
    """获取Agent工作流"""
    return AGENT_WORKFLOWS.get(agent_type)
