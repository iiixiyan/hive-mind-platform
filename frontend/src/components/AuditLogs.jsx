import React, { useState, useEffect } from 'react';
import { FileText, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

const AuditLogs = ({ taskId }) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    if (taskId) {
      fetchAuditLogs(taskId);
    }
  }, [taskId]);

  const fetchAuditLogs = async (id) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/audit/logs/${id}?limit=100`);
      const data = await response.json();

      if (data.success) {
        setLogs(data.logs || []);
      } else {
        setError(data.error || '获取日志失败');
      }
    } catch (err) {
      setError('网络错误，无法获取日志');
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'text-red-600 bg-red-50 dark:bg-red-900/20';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20';
      default:
        return 'text-blue-600 bg-blue-50 dark:bg-blue-900/20';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <AlertTriangle className="w-4 h-4" />;
      case 'warning':
        return <Clock className="w-4 h-4" />;
      default:
        return <CheckCircle className="w-4 h-4" />;
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const filteredLogs = filter === 'all'
    ? logs
    : logs.filter(log => log.severity === filter);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          <FileText className="w-5 h-5 inline mr-2" />
          审计日志
        </h2>
        {logs.length > 0 && (
          <span className="text-sm text-gray-500">
            共 {logs.length} 条日志
          </span>
        )}
      </div>

      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {logs.length === 0 && !loading && (
        <div className="text-center py-8 text-gray-500">
          <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无审计日志</p>
        </div>
      )}

      {logs.length > 0 && (
        <div className="space-y-3">
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              全部
            </button>
            <button
              onClick={() => setFilter('critical')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                filter === 'critical'
                  ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              严重
            </button>
            <button
              onClick={() => setFilter('warning')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                filter === 'warning'
                  ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              警告
            </button>
            <button
              onClick={() => setFilter('info')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                filter === 'info'
                  ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              信息
            </button>
          </div>

          <div className="max-h-[500px] overflow-y-auto space-y-2">
            {filteredLogs.map((log, index) => (
              <div
                key={log.id || index}
                className={`p-4 rounded-lg border transition-colors ${
                  log.success
                    ? 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700'
                    : 'bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-800'
                }`}
              >
                <div className="flex items-start gap-3">
                  {getSeverityIcon(log.severity)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {log.agent_type || 'Unknown'}
                      </span>
                      <span className="text-xs px-2 py-0.5 rounded-full font-medium
                        ${getSeverityColor(log.severity)}">
                        {log.severity || 'info'}
                      </span>
                      {log.success === false && (
                        <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-red-100 text-red-700">
                          失败
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 mb-2">
                      <Clock className="w-3 h-3" />
                      <span>{formatDate(log.timestamp)}</span>
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-gray-700 dark:text-gray-300 w-20">
                          操作:
                        </span>
                        <span className="text-sm text-gray-900 dark:text-gray-100 flex-1">
                          {log.action}
                        </span>
                      </div>
                      {log.details && (
                        <div className="flex items-start gap-2 ml-24">
                          <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                            详情:
                          </span>
                          <span className="text-sm text-gray-600 dark:text-gray-400 flex-1 break-words">
                            {log.details}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditLogs;
