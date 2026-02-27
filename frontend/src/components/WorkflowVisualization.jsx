import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, CheckCircle, Clock, AlertCircle, Play } from 'lucide-react';

const WorkflowVisualization = ({ workflowState }) => {
  const steps = [
    { id: 'goal', name: '目标设定', icon: '🎯', status: workflowState.goal },
    { id: 'echo', name: 'Echo处理', icon: '🎭', status: workflowState.echo },
    { id: 'elon', name: 'Elon执行', icon: '💻', status: workflowState.elon },
    { id: 'henry', name: 'Henry执行', icon: '📢', status: workflowState.henry },
    { id: 'complete', name: '完成', icon: '✅', status: workflowState.complete }
  ];

  const getStatus = (stepId) => {
    const step = steps.find(s => s.id === stepId);
    if (step.status === 'completed') return { emoji: '✅', color: 'green', text: '已完成' };
    if (step.status === 'running') return { emoji: '🟢', color: 'green', text: '进行中' };
    if (step.status === 'pending') return { emoji: '⚪', color: 'gray', text: '待处理' };
    if (step.status === 'failed') return { emoji: '🔴', color: 'red', text: '失败' };
    return { emoji: '⚪', color: 'gray', text: '待处理' };
  };

  return (
    <div className="workflow-visualization">
      <h2>🔄 工作流可视化</h2>

      <div className="workflow-steps">
        <AnimatePresence mode="wait">
          {steps.map((step, index) => {
            const status = getStatus(step.id);
            const isLast = index === steps.length - 1;

            return (
              <motion.div
                key={step.id}
                className="workflow-step"
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 50 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="step-node">
                  <span className="step-icon">{step.icon}</span>
                  <span className="step-name">{step.name}</span>
                </div>

                {!isLast && (
                  <motion.div
                    className="step-arrow"
                    initial={{ opacity: 0, scaleX: 0 }}
                    animate={{ opacity: 1, scaleX: 1 }}
                    transition={{ delay: index * 0.1 + 0.3 }}
                  >
                    <ArrowRight size={20} />
                  </motion.div>
                )}

                <div className="step-status">
                  <span className={`status-icon ${status.color}`}>
                    {status.emoji}
                  </span>
                  <span className="status-text">{status.text}</span>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* 实时日志 */}
      <div className="workflow-logs">
        <h3>📋 执行日志</h3>
        <div className="logs-container">
          {workflowState.logs.map((log, index) => (
            <div key={index} className="log-item">
              <span className="log-time">{log.time}</span>
              <span className="log-content">{log.message}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 进度统计 */}
      <div className="workflow-stats">
        <div className="stat-item">
          <Clock size={24} className="stat-icon" />
          <div>
            <p className="stat-value">{workflowState.duration}</p>
            <p className="stat-label">总耗时</p>
          </div>
        </div>

        <div className="stat-item">
          <Play size={24} className="stat-icon" />
          <div>
            <p className="stat-value">{workflowState.stepsCompleted}/{workflowState.totalSteps}</p>
            <p className="stat-label">完成步骤</p>
          </div>
        </div>

        <div className="stat-item">
          {workflowState.logs.some(l => l.status === 'error') ? (
            <AlertCircle size={24} className="stat-icon error" />
          ) : (
            <CheckCircle size={24} className="stat-icon" />
          )}
          <div>
            <p className="stat-value">
              {workflowState.logs.filter(l => l.status === 'success').length}
            </p>
            <p className="stat-label">成功任务</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowVisualization;
