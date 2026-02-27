"""
Agent工作流实现
"""

from typing import List, Dict, Literal
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
import json

from core.agents import AgentState, AgentType
from core.system_prompts import (
    ECHO_SYSTEM_PROMPT,
    ELON_SYSTEM_PROMPT,
    HENRY_SYSTEM_PROMPT
)

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

# Echo工作流
def create_echo_workflow():
    """创建Echo工作流"""

    def parse_intention(state: AgentState):
        """解析用户意图"""
        llm = get_llm(AgentType.ECHO)

        prompt = f"""作为Echo，请解析以下用户意图并拆解任务：

用户消息：{state['task']}

请拆解为：
1. Tech_Task: 技术任务（需要Elon执行）
2. Market_Task: 市场任务（需要Henry执行）

格式：
Tech_Task: [描述技术任务]
Market_Task: [描述市场任务]"""

        response = llm.invoke(prompt)
        content = response.content

        # 解析响应
        tech_task = None
        market_task = None

        lines = content.split('\n')
        for line in lines:
            if 'Tech_Task:' in line:
                tech_task = line.replace('Tech_Task:', '').strip()
            elif 'Market_Task:' in line:
                market_task = line.replace('Market_Task:', '').strip()

        return {
            **state,
            'tech_tasks': [{'type': 'tech', 'description': tech_task}] if tech_task else [],
            'market_tasks': [{'type': 'market', 'description': market_task}] if market_task else []
        }

    def dispatch_tasks(state: AgentState):
        """分发任务"""
        return {
            **state,
            'current_agent': 'dispatching',
            'messages': state['messages'] + ['任务已分发，正在执行...']
        }

    def monitor_progress(state: AgentState):
        """监控进度"""
        return {
            **state,
            'current_agent': 'monitoring',
            'status': 'thinking'
        }

    def generate_report(state: AgentState):
        """生成报告"""
        report = f"""✅ 任务执行完成报告
━━━━━━━━━━━━━━━━━━━━━━━━━

📊 执行状态：完成
⏱️  耗时：{state.get('duration', '未知')}秒

📋 任务概览：
"""

        if state.get('tech_tasks'):
            report += "🔧 技术任务：\n"
            for task in state['tech_tasks']:
                report += f"  - {task['description']}\n"

        if state.get('market_tasks'):
            report += "📢 市场任务：\n"
            for task in state['market_tasks']:
                report += f"  - {task['description']}\n"

        if state.get('elon_output'):
            report += f"\n💻 技术产出：\n{state['elon_output']}\n"

        if state.get('henry_output'):
            report += f"\n📢 市场产出：\n{state['henry_output']}\n"

        report += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━\n
感谢使用Hive Mind！"""

        return {
            **state,
            'progress_report': report,
            'status': 'idle',
            'current_agent': 'echo'
        }

    # 创建图
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("parse_intention", parse_intention)
    graph.add_node("dispatch_tasks", dispatch_tasks)
    graph.add_node("monitor_progress", monitor_progress)
    graph.add_node("generate_report", generate_report)

    # 添加边
    graph.set_entry_point("parse_intention")
    graph.add_edge("parse_intention", "dispatch_tasks")
    graph.add_edge("dispatch_tasks", "monitor_progress")
    graph.add_edge("monitor_progress", "generate_report")
    graph.add_edge("generate_report", END)

    return graph.compile()

# Elon工作流
def create_elon_workflow():
    """创建Elon工作流"""

    def architect_design(state: AgentState):
        """架构设计"""
        llm = get_llm(AgentType.ARCHITECT)

        prompt = f"""作为Elon的Architect，请为以下任务设计技术方案：

任务：{state['task']}

请提供：
1. 技术栈选型
2. 模块架构设计
3. API定义
4. 数据库设计

格式：
**技术栈：**
- 语言/框架
- 数据库
- 其他

**架构设计：**
[详细描述]

**API定义：**
[接口列表]"""

        response = llm.invoke(prompt)
        return {
            **state,
            'architecture': json.loads(response.content) if '```json' in response.content else {},
            'elon_output': response.content,
            'progress': 30
        }

    def coder_execute(state: AgentState):
        """代码执行"""
        llm = get_llm(AgentType.CODER)

        prompt = f"""作为Elon的Coder，请实现以下架构设计：

任务：{state['task']}
架构：{json.dumps(state.get('architecture', {}), ensure_ascii=False, indent=2)}

请提供完整的代码实现"""

        response = llm.invoke(prompt)
        return {
            **state,
            'code': response.content,
            'elon_output': response.content,
            'progress': 60
        }

    def qa_test(state: AgentState):
        """测试"""
        llm = get_llm(AgentType.QA)

        prompt = f"""作为Elon的QA，请对以下代码进行测试：

代码：
{state.get('code', '')}

请提供：
1. 单元测试代码
2. 测试用例
3. 预期结果"""

        response = llm.invoke(prompt)
        return {
            **state,
            'tests': response.content,
            'progress': 80
        }

    def reviewer_check(state: AgentState):
        """代码审查"""
        llm = get_llm(AgentType.REVIEWER)

        prompt = f"""作为Elon的Reviewer，请审查以下代码：

代码：
{state.get('code', '')}

测试：
{state.get('tests', '')}

请提供审查意见和改进建议"""

        response = llm.invoke(prompt)
        return {
            **state,
            'review': response.content,
            'progress': 100
        }

    # 创建图
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("architect_design", architect_design)
    graph.add_node("coder_execute", coder_execute)
    graph.add_node("qa_test", qa_test)
    graph.add_node("reviewer_check", reviewer_check)

    # 添加边
    graph.set_entry_point("architect_design")
    graph.add_edge("architect_design", "coder_execute")
    graph.add_edge("coder_execute", "qa_test")
    graph.add_edge("qa_test", "reviewer_check")
    graph.add_edge("reviewer_check", END)

    return graph.compile()

# Henry工作流
def create_henry_workflow():
    """创建Henry工作流"""

    def researcher_scan(state: AgentState):
        """社区调研"""
        llm = get_llm(AgentType.RESEARCHER)

        prompt = f"""作为Henry的Researcher，请调研以下信息：

任务：{state['task']}

请提供：
1. 相关的开源项目
2. 社区讨论热点
3. 类似功能的实现方案
4. 市场机会"""

        response = llm.invoke(prompt)
        return {
            **state,
            'research': response.content,
            'henry_output': response.content,
            'progress': 30
        }

    def writer_create(state: AgentState):
        """内容创作"""
        llm = get_llm(AgentType.WRITER)

        prompt = f"""作为Henry的Writer，请根据以下调研结果创建内容：

调研结果：
{state.get('research', '')}

任务：{state['task']}

请提供：
1. PR描述
2. Release Notes
3. 社区推文
4. 博客文章

格式：
**PR描述：**
[内容]

**Release Notes：**
[内容]

**社区推文：**
[内容]

**博客文章：**
[内容]"""

        response = llm.invoke(prompt)
        return {
            **state,
            'content': response.content,
            'henry_output': response.content,
            'progress': 60
        }

    def networker_interact(state: AgentState):
        """社交互动"""
        llm = get_llm(AgentType.NETWORKER)

        prompt = f"""作为Henry的Networker，请准备社交互动内容：

任务：{state['task']}
内容：{state.get('content', '')}

请提供：
1. 社区互动策略
2. 回复模板
3. @提及建议
4. 注意事项"""

        response = llm.invoke(prompt)
        return {
            **state,
            'networking': response.content,
            'progress': 100
        }

    # 创建图
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("researcher_scan", researcher_scan)
    graph.add_node("writer_create", writer_create)
    graph.add_node("networker_interact", networker_interact)

    # 添加边
    graph.set_entry_point("researcher_scan")
    graph.add_edge("researcher_scan", "writer_create")
    graph.add_edge("writer_create", "networker_interact")
    graph.add_edge("networker_interact", END)

    return graph.compile()

# 编译所有工作流
ECHO_WORKFLOW = create_echo_workflow()
ELON_WORKFLOW = create_elon_workflow()
HENRY_WORKFLOW = create_henry_workflow()
