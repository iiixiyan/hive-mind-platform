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
        "success": true,
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
