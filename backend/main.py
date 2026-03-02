"""
Hive Mind 后端主服务 - v0.1.1
FastAPI + LangGraph + 实际工作流实现
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import json
import asyncio
from datetime import datetime
import time
import uuid
from typing import Optional

from core.agents import (
    AgentType,
    get_agent_config,
    get_agent_workflow,
    get_all_agent_types,
    AgentState
)
from core.system_prompts import CORE_SYSTEM_PROMPT
from core.audit_store import audit_store

# 创建FastAPI应用
app = FastAPI(
    title="Hive Mind API",
    description="Multi-Agent Collaboration Platform - Powered by AI",
    version="0.1.1"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class UserMessage(BaseModel):
    message: str
    agent_type: Optional[str] = AgentType.ECHO
    context: Optional[dict] = {}

class AgentStatus(BaseModel):
    agent_type: str
    status: str  # running, thinking, blocked, idle
    current_task: Optional[str] = None
    progress: float = 0.0
    capabilities: Optional[list] = []

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

manager = ConnectionManager()

# 任务存储（内存中）
tasks_db = {}

# 健康检查
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "0.1.1",
        "timestamp": datetime.now().isoformat(),
        "agents": {
            agent_type: {
                "status": "ready",
                "workflow": get_agent_workflow(agent_type) is not None
            }
            for agent_type in get_all_agent_types()
        }
    }

# 获取所有Agent列表
@app.get("/api/agents")
async def list_agents():
    return {
        "success": True,
        "agents": [
            {
                "type": agent_type,
                "config": get_agent_config(agent_type),
                "workflow": get_agent_workflow(agent_type) is not None
            }
            for agent_type in get_all_agent_types()
        ]
    }

# 获取单个Agent状态
@app.get("/api/agents/{agent_type}/status")
async def get_agent_status(agent_type: str):
    config = get_agent_config(agent_type)
    workflow = get_agent_workflow(agent_type)

    return {
        "success": true,
        "agent": {
            "type": agent_type,
            "name": config.name,
            "role": config.role,
            "capabilities": config.capabilities,
            "workflow": workflow is not None
        },
        "status": "idle",
        "message": f"{agent_type} is ready to work"
    }

# 启动Agent工作流
@app.post("/api/workflow/{agent_type}")
async def start_workflow(agent_type: str, message: UserMessage):
    """
    启动Agent工作流

    - agent_type: agent类型 (echo, elon, henry)
    - message: 用户输入
    """

    # 验证Agent类型
    if agent_type not in get_all_agent_types():
        return {
            "success": False,
            "error": f"Unknown agent type: {agent_type}"
        }

    # 创建任务ID
    task_id = f"task_{uuid.uuid4().hex[:12]}"

    # 创建任务状态
    tasks_db[task_id] = {
        "id": task_id,
        "agent_type": agent_type,
        "message": message.message,
        "status": "pending",
        "progress": 0.0,
        "start_time": datetime.now().isoformat(),
        "logs": [],
        "outputs": {}
    }

    # 异步执行工作流
    asyncio.create_task(execute_agent_workflow(task_id, agent_type, message))

    return {
        "success": true,
        "task_id": task_id,
        "agent_type": agent_type,
        "message": message.message,
        "status": "started"
    }

async def execute_agent_workflow(task_id: str, agent_type: str, message: UserMessage):
    """执行Agent工作流"""
    task = tasks_db[task_id]
    workflow = get_agent_workflow(agent_type)

    if not workflow:
        task["status"] = "failed"
        task["logs"].append({
            "time": datetime.now().isoformat(),
            "message": f"Workflow for {agent_type} not found",
            "status": "error"
        })
        return

    try:
        # 安全检查1: 目标对齐
        from core.agents import goal_alignment_check
        if not goal_alignment_check({
            "task": message.message,
            "progress": 0.0
        }):
            task["status"] = "rejected"
            task["logs"].append({
                "time": datetime.now().isoformat(),
                "message": "目标对齐检查失败，任务被拒绝",
                "status": "error"
            })
            return

        # 安全检查2: 频率限制
        from core.agents import rate_limit_check
        if not rate_limit_check(agent_type):
            task["status"] = "rate_limited"
            task["logs"].append({
                "time": datetime.now().isoformat(),
                "message": "操作频率过高，任务被限制",
                "status": "warning"
            })
            return

        # 初始化状态
        initial_state = {
            "messages": [f"Task: {message.message}"],
            "current_agent": agent_type,
            "task": message.message,
            "status": "running",
            "progress": 0.0,
            "start_time": datetime.now(),
            "task_id": task_id,
            "audit_logs": []
        }

        # 执行工作流
        result = await workflow.ainvoke(initial_state)

        # 更新任务状态
        task["status"] = "completed"
        task["progress"] = 100.0
        task["end_time"] = datetime.now().isoformat()

        # 提取输出
        if agent_type in result:
            task["outputs"] = result[agent_type]

        task["logs"].append({
            "time": datetime.now().isoformat(),
            "message": f"{agent_type} workflow completed successfully",
            "status": "success",
            "duration": (datetime.now() - task["start_time"]).total_seconds()
        })

    except Exception as e:
        task["status"] = "failed"
        task["logs"].append({
            "time": datetime.now().isoformat(),
            "message": f"Error executing workflow: {str(e)}",
            "status": "error"
        })
        print(f"Error executing workflow: {e}")

    # 通知客户端（如果有）
    await manager.send_message("main", {
        "type": "task_complete",
        "task_id": task_id,
        "agent_type": agent_type,
        "status": task["status"],
        "logs": task["logs"],
        "outputs": task.get("outputs", {})
    })

# 获取任务状态
@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in tasks_db:
        return {
            "success": False,
            "error": "Task not found"
        }

    task = tasks_db[task_id]

    return {
        "success": true,
        "task": {
            "id": task_id,
            "agent_type": task["agent_type"],
            "message": task["message"],
            "status": task["status"],
            "progress": task["progress"],
            "start_time": task["start_time"],
            "end_time": task.get("end_time"),
            "logs": task["logs"],
            "outputs": task.get("outputs", {})
        }
    }

# 删除任务
@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    if task_id in tasks_db:
        del tasks_db[task_id]
        return {"success": True, "message": "Task deleted"}

    return {"success": False, "error": "Task not found"}

# 获取所有任务列表
@app.get("/api/tasks")
async def list_tasks():
    return {
        "success": True,
        "tasks": [
            {
                "id": t["id"],
                "agent_type": t["agent_type"],
                "message": t["message"],
                "status": t["status"],
                "progress": t["progress"]
            }
            for t in tasks_db.values()
        ]
    }

# ===== 审计日志 API =====

@app.get("/api/audit/logs")
async def get_audit_logs(
    task_id: Optional[str] = None,
    agent_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """获取审计日志列表"""
    if task_id:
        # 获取特定任务的日志
        logs = audit_store.get_task_logs(task_id, limit)
        return {
            "success": True,
            "task_id": task_id,
            "logs": logs,
            "total": len(logs)
        }
    elif agent_type:
        # 获取特定 Agent 的日志（需要从日志中筛选）
        logs = audit_store.get_task_logs("", limit)
        filtered_logs = [log for log in logs if log.get("agent_type") == agent_type]
        return {
            "success": True,
            "agent_type": agent_type,
            "logs": filtered_logs,
            "total": len(filtered_logs)
        }
    else:
        # 获取所有日志
        # 注意：SQLite 查询需要修改 audit_store 来支持 offset/limit
        return {
            "success": True,
            "message": "Use task_id or agent_type parameter to filter logs",
            "hint": "Pass task_id to get logs for a specific task, or agent_type to get logs for a specific agent"
        }

@app.get("/api/safety/events")
async def get_safety_events(
    limit: int = Query(50, ge=1, le=500),
    resolved: Optional[bool] = None
):
    """获取安全事件列表"""
    events = audit_store.get_all_safety_events(limit)

    if resolved is not None:
        events = [e for e in events if e.get("resolved") == resolved]

    return {
        "success": True,
        "events": events,
        "total": len(events)
    }

@app.get("/api/safety/stats")
async def get_safety_stats():
    """获取安全统计信息"""
    # 获取频率限制统计
    stats = {
        "henry_networker": audit_store.get_rate_limit_stats(AgentType.NETWORKER, "hourly_mentions"),
        "elon_test_failures": audit_store.get_rate_limit_stats(AgentType.CODER, "test_failures")
    }

    return {
        "success": True,
        "stats": stats
    }

@app.get("/api/audit/logs/{task_id}")
async def get_task_audit_logs(task_id: str, limit: int = Query(100, ge=1, le=1000)):
    """获取特定任务的审计日志（旧端点，保留兼容性）"""
    logs = audit_store.get_task_logs(task_id, limit)

    return {
        "success": True,
        "task_id": task_id,
        "logs": logs,
        "total": len(logs)
    }

# WebSocket端点
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            # 处理客户端消息
            if data.get("type") == "subscribe" and data.get("task_id"):
                task_id = data["task_id"]
                if task_id in tasks_db:
                    task = tasks_db[task_id]
                    await manager.send_message(
                        client_id,
                        {
                            "type": "task_update",
                            "task_id": task_id,
                            "status": task["status"],
                            "progress": task["progress"],
                            "logs": task["logs"]
                        }
                    )
    except WebSocketDisconnect:
        manager.disconnect(client_id)

# 前端Dashboard
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    with open("frontend/index.html", "r") as f:
        return f.read()

# 启动服务
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
