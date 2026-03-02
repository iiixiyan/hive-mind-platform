import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, AlertCircle, Shield } from 'lucide-react';

const SafetyEvents = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSafetyEvents();
  }, []);

  const fetchSafetyEvents = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/safety/events?limit=50');
      const data = await response.json();

      if (data.success) {
        setEvents(data.events || []);
      } else {
        setError(data.error || '获取安全事件失败');
      }
    } catch (err) {
      setError('网络错误，无法获取安全事件');
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getEventTypeColor = (eventType) => {
    switch (eventType) {
      case 'dangerous_command':
        return 'text-red-600 bg-red-50 dark:bg-red-900/20';
      case 'goal_alignment_failed':
        return 'text-orange-600 bg-orange-50 dark:bg-orange-900/20';
      case 'rate_limited':
        return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20';
      default:
        return 'text-blue-600 bg-blue-50 dark:bg-blue-900/20';
    }
  };

  const getEventTypeIcon = (eventType) => {
    switch (eventType) {
      case 'dangerous_command':
        return <AlertTriangle className="w-4 h-4" />;
      case 'goal_alignment_failed':
        return <AlertCircle className="w-4 h-4" />;
      case 'rate_limited':
        return <Shield className="w-4 h-4" />;
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
      minute: '2-digit'
    });
  };

  const resolvedCount = events.filter(e => e.resolved).length;
  const unresolvedCount = events.filter(e => !e.resolved).length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          <Shield className="w-5 h-5 inline mr-2" />
          安全事件
        </h2>
        <div className="flex gap-4 text-sm">
          <span className="text-gray-600 dark:text-gray-400">
            已解决: {resolvedCount}
          </span>
          <span className="text-gray-600 dark:text-gray-400">
            未解决: {unresolvedCount}
          </span>
        </div>
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

      {events.length === 0 && !loading && (
        <div className="text-center py-8 text-gray-500">
          <Shield className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无安全事件</p>
          <p className="text-sm mt-1">系统运行正常</p>
        </div>
      )}

      {events.length > 0 && (
        <div className="max-h-[600px] overflow-y-auto space-y-3">
          {events.map((event, index) => (
            <div
              key={event.id || index}
              className={`p-4 rounded-lg border transition-colors ${
                event.resolved
                  ? 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700 opacity-60'
                  : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700'
              }`}
            >
              <div className="flex items-start gap-3">
                {getEventTypeIcon(event.event_type)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {event.event_type.replace(/_/g, ' ').toUpperCase()}
                    </span>
                    {event.resolved ? (
                      <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-green-100 text-green-700">
                        已解决
                      </span>
                    ) : (
                      <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-red-100 text-red-700">
                        未解决
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 mb-2">
                    {formatDate(event.timestamp)}
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-900/50 rounded-md">
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {event.details}
                    </p>
                  </div>
                  {event.task_id && (
                    <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                      任务 ID: {event.task_id}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SafetyEvents;
