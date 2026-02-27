import { useState, useEffect } from 'react';
import './App.css';
import AgentCard from './components/AgentCard.jsx';
import WorkflowVisualization from './components/WorkflowVisualization.jsx';
import api from './services/api.js';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Settings, Activity, MessageSquare, Activity as ActivityIcon } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [agents, setAgents] = useState({});
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [tasks, setTasks] = useState([]);
  const [currentTaskId, setCurrentTaskId] = useState(null);
  const [workflowState, setWorkflowState] = useState({
    goal: 'pending',
    echo: 'pending',
    elon: 'pending',
    henry: 'pending',
    complete: 'pending',
    duration: '0s',
    stepsCompleted: 0,
    totalSteps: 5,
    logs: []
  });

  // 初始化Agent状态
  useEffect(() => {
    initializeAgents();
    loadTasks();
    startLogRotation();
  }, []);

  const initializeAgents = async () => {
    const agentPromises = Object.keys(agents).map(async (agentType) => {
      try {
        const status = await api.getAgentStatus(agentType);
        setAgents(prev => ({
          ...prev,
          [agentType]: {
            ...status,
            status: 'idle',
            currentTask: null,
            progress: 0
          }
        }));
      } catch (error) {
        console.error(`Error checking ${agentType} status:`, error);
      }
    });

    await Promise.all(agentPromises);
  };

  const loadTasks = async () => {
    try {
      const response = await api.listTasks();
      if (response.success) {
        setTasks(response.tasks);
      }
    } catch (error) {
      console.error('Error loading tasks:', error);
    }
  };

  const startLogRotation = () => {
    // 定期更新任务状态
    setInterval(async () => {
      if (currentTaskId) {
        try {
          const response = await api.getTaskStatus(currentTaskId);
          if (response.success) {
            const task = response.task;
            setWorkflowState(prev => ({
              ...prev,
              goal: task.progress > 20 ? 'completed' : 'pending',
              echo: task.progress > 40 ? 'completed' : 'running',
              elon: task.progress > 60 ? 'completed' : 'running',
              henry: task.progress > 80 ? 'completed' : 'running',
              complete: task.progress >= 100 ? 'completed' : 'pending',
              logs: task.logs
            }));

            if (task.status === 'completed') {
              setCurrentTaskId(null);
            }
          }
        } catch (error) {
          console.error('Error updating task status:', error);
        }
      }
    }, 2000);
  };

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return;

    const newMessage = {
      role: 'user',
      content: currentMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, newMessage]);
    setCurrentMessage('');

    // 获取第一个可用的Agent
    const availableAgent = Object.keys(agents).find(
      key => agents[key].status === 'idle'
    ) || 'echo';

    // 启动工作流
    const response = await api.startWorkflow(availableAgent, {
      message: currentMessage,
      agent_type: availableAgent
    });

    if (response.success) {
      setCurrentTaskId(response.task_id);
      setAgents(prev => ({
        ...prev,
        [availableAgent]: {
          ...prev[availableAgent],
          status: 'running',
          currentTask: currentMessage,
          progress: 10
        }
      }));

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `🤖 ${availableAgent.toUpperCase()} 正在处理您的消息...`,
        timestamp: new Date().toISOString()
      }]);
    }
  };

  const addLog = (log) => {
    setWorkflowState(prev => ({
      ...prev,
      logs: [{ time: new Date().toLocaleTimeString(), message: log, status: 'info' }, ...prev.logs].slice(0, 50)
    }));
  };

  const clearLogs = () => {
    setWorkflowState(prev => ({ ...prev, logs: [] }));
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'green';
      case 'thinking': return 'yellow';
      case 'blocked': return 'red';
      case 'idle': return 'gray';
      default: return 'gray';
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="logo">
          <h1>🐝 Hive Mind</h1>
          <p>Multi-Agent Collaboration Platform</p>
          <span className="version">v0.1.1</span>
        </div>
        <nav className="nav">
          <button
            className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Dashboard
          </button>
          <button
            className={`nav-btn ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            💬 Chat
          </button>
          <button
            className={`nav-btn ${activeTab === 'workflow' ? 'active' : ''}`}
            onClick={() => setActiveTab('workflow')}
          >
            🔄 Workflow
          </button>
          <button
            className={`nav-btn ${activeTab === 'tasks' ? 'active' : ''}`}
            onClick={() => setActiveTab('tasks')}
          >
            📋 Tasks
          </button>
        </nav>
      </header>

      {/* Main Content */}
      <main className="main">
        <AnimatePresence mode="wait">
          {activeTab === 'dashboard' && (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="dashboard"
            >
              {/* Agent Grid */}
              <div className="agent-grid">
                <h2>🤖 Agent Network</h2>
                <div className="grid-container">
                  {Object.keys(agents).map((agentType) => {
                    const config = api.getAgentConfig(agentType);
                    const agent = agents[agentType];

                    return (
                      <AgentCard
                        key={agentType}
                        agentType={agentType}
                        status={agent.status}
                        currentTask={agent.currentTask}
                        progress={agent.progress}
                        config={config}
                      />
                    );
                  })}
                </div>
              </div>

              {/* Quick Actions */}
              <div className="quick-actions">
                <h2>⚡ Quick Actions</h2>
                <div className="actions-grid">
                  <button className="action-card" onClick={() => setCurrentMessage('优化系统性能')}>
                    🚀 优化系统性能
                  </button>
                  <button className="action-card" onClick={() => setCurrentMessage('创建新的API接口')}>
                    📝 创建API接口
                  </button>
                  <button className="action-card" onClick={() => setCurrentMessage('生成项目文档')}>
                    📚 生成文档
                  </button>
                  <button className="action-card" onClick={() => setCurrentMessage('分析社区反馈')}>
                    📊 分析社区反馈
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'chat' && (
            <motion.div
              key="chat"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="chat"
            >
              <h2>💬 Agent Chat</h2>
              <div className="chat-messages">
                {messages.length === 0 && (
                  <div className="empty-state">
                    <MessageSquare size={48} />
                    <p>开始与Agent对话...</p>
                    <p className="hint">输入消息或选择快速操作</p>
                  </div>
                )}
                {messages.map((msg, index) => (
                  <div key={index} className={`message ${msg.role}`}>
                    <div className="message-header">
                      <span className="role">{msg.role.toUpperCase()}</span>
                      <span className="timestamp">
                        {new Date(msg.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="message-content">
                      {msg.content}
                    </div>
                  </div>
                ))}
              </div>
              <div className="chat-input">
                <input
                  type="text"
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="输入消息与Agent交互..."
                />
                <button onClick={handleSendMessage}>
                  <Send size={20} />
                </button>
              </div>
            </motion.div>
          )}

          {activeTab === 'workflow' && (
            <motion.div
              key="workflow"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="workflow"
            >
              <WorkflowVisualization workflowState={workflowState} />
            </motion.div>
          )}

          {activeTab === 'tasks' && (
            <motion.div
              key="tasks"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="tasks"
            >
              <h2>📋 Tasks</h2>
              {tasks.length === 0 ? (
                <div className="empty-state">
                  <ActivityIcon size={48} />
                  <p>暂无任务</p>
                </div>
              ) : (
                <div className="tasks-list">
                  {tasks.map((task) => (
                    <div key={task.id} className="task-item">
                      <div className="task-info">
                        <span className={`status ${task.status}`}>
                          {task.status === 'completed' ? '✅' : task.status === 'running' ? '🟢' : '⚪'}
                          {task.status}
                        </span>
                        <span className="agent-type">{task.agent_type}</span>
                      </div>
                      <p className="task-message">{task.message}</p>
                      <div className="task-progress">
                        <div className="progress-bar">
                          <div
                            className="progress-fill"
                            style={{ width: `${task.progress}%` }}
                          ></div>
                        </div>
                        <span className="progress-text">{Math.round(task.progress)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'settings' && (
            <motion.div
              key="settings"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="settings"
            >
              <h2>⚙️ Settings</h2>
              <div className="settings-content">
                <div className="setting-item">
                  <h3>API Configuration</h3>
                  <input type="text" placeholder="API Endpoint" defaultValue="http://localhost:8000" />
                  <input type="password" placeholder="API Key" />
                  <button className="btn-primary">Save</button>
                </div>
                <div className="setting-item">
                  <h3>Agent Configuration</h3>
                  <label>
                    <input type="checkbox" defaultChecked />
                    Enable Echo
                  </label>
                  <label>
                    <input type="checkbox" defaultChecked />
                    Enable Elon
                  </label>
                  <label>
                    <input type="checkbox" defaultChecked />
                    Enable Henry
                  </label>
                </div>
                <div className="setting-item">
                  <h3>Safety Settings</h3>
                  <label>
                    <input type="checkbox" defaultChecked />
                    Enable Safety Check
                  </label>
                  <label>
                    <input type="checkbox" defaultChecked />
                    Enable Rate Limiting
                  </label>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>🐝 Hive Mind - Multi-Agent Collaboration Platform | v0.1.1</p>
        <p>Started: 2026-02-27 | GitHub: https://github.com/iiixiyan/hive-mind-platform</p>
      </footer>
    </div>
  );
}

export default App;
