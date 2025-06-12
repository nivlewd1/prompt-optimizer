const axios = require('axios');

class PromptOptimizerApiClient {
  constructor(apiKey, backendUrl = 'https://p01--project-optimizer--fvrdk8m9k9j.code.run') {
    this.apiKey = apiKey;
    this.backendUrl = backendUrl;
    this.client = axios.create({
      baseURL: backendUrl,
      headers: {
        'X-API-Key': apiKey,
        'Content-Type': 'application/json'
      },
      timeout: 30000
    });
  }

  async validateKey() {
    try {
      const response = await this.client.post('/api/v1/validate-key');
      return response.data;
    } catch (error) {
      if (error.response?.status === 401) {
        throw new Error('Invalid API key');
      }
      if (error.response?.status === 403) {
        throw new Error('API key expired or subscription inactive');
      }
      if (error.response?.status === 429) {
        throw new Error('Rate limit exceeded. Please try again later.');
      }
      throw new Error(`Validation failed: ${error.message}`);
    }
  }

  async optimize(prompt, goals = ['clarity']) {
    try {
      // Encode config as base64 (MCP protocol requirement)
      const config = { prompt, goals };
      const configB64 = Buffer.from(JSON.stringify(config)).toString('base64');
      
      const response = await this.client.post(`/api/v1/mcp/optimize?config=${encodeURIComponent(configB64)}`);
      return response.data;
    } catch (error) {
      if (error.response?.status === 429) {
        const detail = error.response.data?.detail || 'Quota exceeded';
        throw new Error(`${detail}. Please upgrade your plan or wait for quota reset.`);
      }
      if (error.response?.status === 401) {
        throw new Error('API key invalid or expired');
      }
      if (error.response?.status === 400) {
        throw new Error(`Invalid request: ${error.response.data?.detail || 'Bad request'}`);
      }
      if (error.response?.status === 500) {
        throw new Error('Server error. Please try again later.');
      }
      throw new Error(`Optimization failed: ${error.response?.data?.detail || error.message}`);
    }
  }

  async getHealthStatus() {
    try {
      const response = await this.client.get('/api/v1/mcp/health');
      return response.data;
    } catch (error) {
      throw new Error(`Health check failed: ${error.message}`);
    }
  }
}

module.exports = PromptOptimizerApiClient;