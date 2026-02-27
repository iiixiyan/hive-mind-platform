"""
Agent定义与状态管理 - v0.1.1
"""

from typing import TypedDict, List, Annotated, Literal, Optional
from langgraph.graph.message import add_messages
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from core.workflows import ECHO_WORKFLOW, ELON_WORKFLOW, HENRY_WORKFLOW

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

# 安全检查函数
def safety_check(state: AgentState) -> Literal["pass", "fail", "block"]:
    """安全检查"""
    # TODO: 实现完整的安全检查逻辑
    return "pass"

# 目标对齐检查
def goal_alignment_check(state: AgentState) -> bool:
    """目标对齐检查"""
    # TODO: 实现目标对齐逻辑
    return True

# 频率限制检查
def rate_limit_check(agent_type: str) -> bool:
    """频率限制检查"""
    # TODO: 实现频率限制
    return True

# 获取所有Agent类型
def get_all_agent_types():
    """获取所有Agent类型"""
    return list(AGENT_CONFIG.keys())

# 获取Agent工作流
def get_agent_workflow(agent_type: str):
    """获取Agent工作流"""
    return AGENT_WORKFLOWS.get(agent_type)
