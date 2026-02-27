import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = {
  // Get agent status
  getAgentStatus: async (agentType) => {
    const response = await axios.get(`${API_URL}/api/agents/${agentType}/status`);
    return response.data;
  },

  // Start workflow
  startWorkflow: async (agentType, message) => {
    const response = await axios.post(`${API_URL}/api/workflow/${agentType}`, {
      message,
      agent_type: agentType
    });
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await axios.get(`${API_URL}/health`);
    return response.data;
  }
};

export default api;
