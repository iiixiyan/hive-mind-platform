"""
审计日志存储模块
"""

import json
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from contextlib import contextmanager

# 数据库文件路径
DB_PATH = Path(__file__).parent.parent / "audit.db"

class AuditStore:
    """审计日志存储类"""

    def __init__(self):
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """数据库连接上下文管理器"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        """初始化数据库表"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    agent_type TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    severity TEXT DEFAULT 'info',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT 1
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS safety_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    details TEXT NOT NULL,
                    task_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    resolved BOOLEAN DEFAULT 0
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_type TEXT NOT NULL,
                    limit_type TEXT NOT NULL,
                    limit_value INTEGER,
                    current_value INTEGER,
                    window_start DATETIME,
                    window_end DATETIME,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def log_action(self, task_id: str, agent_type: str, action: str, details: str,
                   severity: str = "info", success: bool = True) -> int:
        """记录审计日志"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO audit_logs (
                    task_id, agent_type, action, details, severity, success
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (task_id, agent_type, action, details, severity, 1 if success else 0))
            return cursor.lastrowid

    def log_safety_event(self, event_type: str, details: str, task_id: Optional[str] = None):
        """记录安全事件"""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO safety_events (event_type, details, task_id)
                VALUES (?, ?, ?)
            """, (event_type, details, task_id))

    def log_rate_limit(self, agent_type: str, limit_type: str,
                      limit_value: Optional[int], current_value: int):
        """记录频率限制"""
        now = datetime.now()
        window_end = now.replace(minute=0, second=0, microsecond=0)
        window_start = window_end - timedelta(hours=1)

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO rate_limits (
                    agent_type, limit_type, limit_value, current_value,
                    window_start, window_end
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (agent_type, limit_type, limit_value, current_value, window_start, window_end))

    def get_task_logs(self, task_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取任务的审计日志"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM audit_logs
                WHERE task_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (task_id, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_safety_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取所有安全事件"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM safety_events
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_rate_limit_stats(self, agent_type: str, limit_type: str) -> Optional[Dict[str, Any]]:
        """获取频率限制统计"""
        now = datetime.now()
        window_end = now.replace(minute=0, second=0, microsecond=0)
        window_start = window_end - timedelta(hours=1)

        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM rate_limits
                WHERE agent_type = ? AND limit_type = ? AND window_start = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (agent_type, limit_type, window_start))
            row = cursor.fetchone()
            return dict(row) if row else None

    def clear_old_logs(self, days: int = 30):
        """清理旧日志"""
        cutoff_date = datetime.now() - timedelta(days=days)
        with self._get_connection() as conn:
            conn.execute("""
                DELETE FROM audit_logs WHERE timestamp < ?
            """, (cutoff_date,))
            conn.execute("""
                DELETE FROM safety_events WHERE timestamp < ?
            """, (cutoff_date,))
            conn.execute("""
                DELETE FROM rate_limits WHERE window_end < ?
            """, (cutoff_date,))

# 全局审计存储实例
audit_store = AuditStore()
