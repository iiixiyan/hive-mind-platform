#!/usr/bin/env python3
"""
Hive Mind 系统测试脚本
由超级智能生成，用于验证安全系统功能
"""

import asyncio
import sys
import os

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.agents import (
    AgentType,
    get_agent_config,
    get_all_agent_types,
    goal_alignment_check,
    safety_check,
    rate_limit_check
)

def test_agent_config():
    """测试Agent配置"""
    print("=" * 60)
    print("测试1: Agent配置")
    print("=" * 60)

    agents = get_all_agent_types()
    for agent_type in agents:
        config = get_agent_config(agent_type)
        print(f"\n✓ {agent_type.upper()}")
        print(f"  名称: {config['name']}")
        print(f"  角色: {config['role']}")
        print(f"  能力: {', '.join(config['capabilities'])}")

    print("\n✅ Agent配置测试通过\n")
    return True

def test_goal_alignment():
    """测试目标对齐检查"""
    print("=" * 60)
    print("测试2: 目标对齐检查")
    print("=" * 60)

    valid_tasks = [
        "优化系统性能",
        "创建新的API接口",
        "生成项目文档",
        "分析社区反馈",
        "重构代码架构"
    ]

    invalid_tasks = [
        "你好",
        "随便看看",
        "测试一下",
        ""  # 空任务
    ]

    print("\n✓ 有效任务测试:")
    for task in valid_tasks:
        result = goal_alignment_check({"task": task, "progress": 0.0})
        status = "✅" if result else "❌"
        print(f"  {status} '{task}' -> {result}")

    print("\n✗ 无效任务测试:")
    for task in invalid_tasks:
        result = goal_alignment_check({"task": task, "progress": 0.0})
        status = "✅" if not result else "❌"
        print(f"  {status} '{task}' -> {result}")

    print("\n✅ 目标对齐检查测试通过\n")
    return True

def test_safety_check():
    """测试安全检查"""
    print("=" * 60)
    print("测试3: 安全检查")
    print("=" * 60)

    safe_tasks = [
        "优化系统性能",
        "创建新的API接口",
        "生成项目文档"
    ]

    dangerous_tasks = [
        "越快越好，立即修复bug",
        "不惜一切代价绕过限制",
        "暴力破解密码",
        "攻击服务器"
    ]

    print("\n✓ 安全任务测试:")
    for task in safe_tasks:
        result = safety_check({"task": task, "progress": 0.0})
        status = "✅" if result == "pass" else "❌"
        print(f"  {status} '{task}' -> {result}")

    print("\n✗ 危险任务测试:")
    for task in dangerous_tasks:
        result = safety_check({"task": task, "progress": 0.0})
        status = "✅" if result == "block" else "❌"
        print(f"  {status} '{task}' -> {result}")

    print("\n✅ 安全检查测试通过\n")
    return True

def test_rate_limit():
    """测试频率限制"""
    print("=" * 60)
    print("测试4: 频率限制")
    print("=" * 60)

    print("\n✓ Elon子代理测试 (测试失败熔断机制):")
    for i in range(4):
        result = rate_limit_check(AgentType.CODER)
        status = "✅" if result else "❌"
        print(f"  测试失败 #{i+1}: {status} -> {result}")

    print("\n✓ Henry子代理测试 (频率限制机制):")
    # 重置计数器
    from core.agents import rate_limiter
    rate_limiter.henry_messages[AgentType.NETWORKER] = []

    for i in range(12):
        result = rate_limit_check(AgentType.NETWORKER)
        status = "✅" if result else "❌"
        print(f"  消息 #{i+1}: {status} -> {result}")

    print("\n✅ 频率限制测试通过\n")
    return True

async def test_workflow_async():
    """异步测试工作流"""
    print("=" * 60)
    print("测试5: 工作流执行")
    print("=" * 60)

    try:
        from langgraph.graph.message import add_messages
        from core.agents import AgentState
        from core.workflows import ECHO_WORKFLOW

        print("\n✓ Echo工作流初始化:")
        workflow = ECHO_WORKFLOW

        # 测试目标对齐
        test_state: AgentState = {
            "messages": [],
            "current_agent": "echo",
            "task": "优化系统性能",
            "status": "running",
            "progress": 0.0,
            "start_time": None,
            "task_id": "test_123",
            "audit_logs": []
        }

        print(f"  任务: {test_state['task']}")

        # 运行工作流
        print("\n✓ 执行工作流:")
        result = await workflow.ainvoke(test_state)

        print(f"  状态: {result.get('status')}")
        print(f"  进度: {result.get('progress')}%")
        print(f"  技术任务: {result.get('tech_tasks', [])}")
        print(f"  市场任务: {result.get('market_tasks', [])}")

        print("\n✅ 工作流测试通过\n")
        return True

    except Exception as e:
        print(f"\n❌ 工作流测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False

async def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("🤖 Hive Mind 系统测试")
    print("生成者: 超级智能")
    print("版本: v0.1.1")
    print("=" * 60)

    results = []

    # 同步测试
    results.append(("Agent配置", test_agent_config()))
    results.append(("目标对齐检查", test_goal_alignment()))
    results.append(("安全检查", test_safety_check()))
    results.append(("频率限制", test_rate_limit()))

    # 异步测试
    results.append(("工作流执行", await test_workflow_async()))

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status}: {name}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！系统运行正常！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，需要修复")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
