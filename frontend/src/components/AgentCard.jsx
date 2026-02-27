import React from 'react';
import { motion } from 'framer-motion';

const AgentCard = ({ agentType, status, currentTask, progress, config }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'green';
      case 'thinking': return 'yellow';
      case 'blocked': return 'red';
      case 'idle': return 'gray';
      default: return 'gray';
    }
  };

  const getStatusEmoji = (status) => {
    switch (status) {
      case 'running': return '🟢';
      case 'thinking': return '🟡';
      case 'blocked': return '🔴';
      case 'idle': return '⚪';
      default: return '⚪';
    }
  };

  return (
    <motion.div
      className="agent-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.3 }}
    >
      <div className="agent-header">
        <div className="agent-icon">{config.icon || '🤖'}</div>
        <div className="agent-info">
          <h3>{config.name}</h3>
          <span className="role">{config.role}</span>
        </div>
      </div>

      <div className="agent-body">
        <div className="agent-status">
          <span className={`status-dot ${getStatusColor(status)}`}></span>
          <span className="status-text">{getStatusEmoji(status)} {status.toUpperCase()}</span>
        </div>

        {currentTask && (
          <div className="current-task">
            <span className="task-label">当前任务：</span>
            <p>{currentTask}</p>
          </div>
        )}

        <div className="progress-section">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <span className="progress-text">{Math.round(progress)}%</span>
        </div>
      </div>

      <div className="agent-footer">
        <div className="capabilities">
          <span className="label">能力：</span>
          <div className="tags">
            {config.capabilities.slice(0, 3).map((cap, index) => (
              <span key={index} className="tag">
                {cap}
              </span>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default AgentCard;
