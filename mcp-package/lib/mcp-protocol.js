const PromptOptimizerApiClient = require('./api-client');

class MCPServer {
  constructor(apiKey) {
    this.apiClient = new PromptOptimizerApiClient(apiKey);
    this.tools = [{
      name: "optimize_prompt",
      description: "Optimize prompts for clarity, conciseness, and effectiveness using advanced AI techniques",
      inputSchema: {
        type: "object",
        properties: {
          prompt: { 
            type: "string", 
            description: "The prompt to optimize" 
          },
          goals: { 
            type: "array", 
            items: { 
              type: "string",
              enum: [
                "clarity", 
                "conciseness", 
                "technical_accuracy", 
                "contextual_relevance", 
                "specificity", 
                "actionability", 
                "structure", 
                "technical_precision",
                "linguistic_precision", 
                "holistic_effectiveness"
              ]
            },
            description: "Optimization goals (default: clarity)",
            default: ["clarity"]
          }
        },
        required: ["prompt"]
      }
    }];
  }

  async initialize() {
    try {
      const userData = await this.apiClient.validateKey();
      console.error(`✅ Connected to Prompt Optimizer API`);
      console.error(`   Tier: ${userData.tier}`);
      console.error(`   Quota: ${userData.quota_used}/${userData.quota_limit} used`);
      console.error(`   Status: ${userData.subscription_status}`);
      return true;
    } catch (error) {
      console.error(`❌ Failed to connect: ${error.message}`);
      return false;
    }
  }

  async handleToolCall(name, args) {
    if (name === 'optimize_prompt') {
      const { prompt, goals = ['clarity'] } = args;
      
      // Validate prompt
      if (!prompt || typeof prompt !== 'string' || prompt.trim().length === 0) {
        return {
          content: [{
            type: "text",
            text: "❌ **Error:** Prompt cannot be empty"
          }],
          isError: true
        };
      }

      // Validate goals
      const validGoals = [
        "clarity", "conciseness", "technical_accuracy", "contextual_relevance", 
        "specificity", "actionability", "structure", "technical_precision",
        "linguistic_precision", "holistic_effectiveness"
      ];
      
      const filteredGoals = goals.filter(goal => validGoals.includes(goal));
      if (filteredGoals.length === 0) {
        filteredGoals.push('clarity'); // Default fallback
      }
      
      try {
        const result = await this.apiClient.optimize(prompt.trim(), filteredGoals);
        
        return {
          content: [{
            type: "text",
            text: `# Optimized Prompt\n\n${result.optimized_prompt}\n\n---\n\n**Confidence Score:** ${result.confidence_score.toFixed(2)}\n**Goals Applied:** ${filteredGoals.join(', ')}\n**Quota Remaining:** ${result.metadata?.quota_remaining ?? 'Unknown'}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text", 
            text: `❌ **Optimization Error:** ${error.message}`
          }],
          isError: true
        };
      }
    }
    
    throw new Error(`Unknown tool: ${name}`);
  }

  async handleMessage(message) {
    const { method, params, id } = message;
    
    try {
      switch (method) {
        case 'initialize':
          return { 
            jsonrpc: "2.0",
            id, 
            result: { 
              protocolVersion: "2024-11-05",
              capabilities: {
                tools: {}
              },
              serverInfo: {
                name: "mcp-prompt-optimizer",
                version: "1.0.0"
              }
            } 
          };
          
        case 'tools/list':
          return { 
            jsonrpc: "2.0",
            id, 
            result: { tools: this.tools } 
          };
          
        case 'tools/call':
          if (!params || !params.name) {
            throw new Error('Missing tool name in call parameters');
          }
          const result = await this.handleToolCall(params.name, params.arguments || {});
          return { 
            jsonrpc: "2.0",
            id, 
            result 
          };
          
        default:
          throw new Error(`Unknown method: ${method}`);
      }
    } catch (error) {
      return {
        jsonrpc: "2.0",
        id,
        error: {
          code: -32000,
          message: error.message
        }
      };
    }
  }
}

module.exports = MCPServer;