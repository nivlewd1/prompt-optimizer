#!/usr/bin/env node

/**
 * Prompt Optimizer - Modernized MCP Showcase
 * This file provides a professional implementation using the official MCP SDK.
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { CallToolRequestSchema, ListToolsRequestSchema } = require('@modelcontextprotocol/sdk/types.js');
const axios = require('axios');
const Config = require('./lib/config');
const packageJson = require('./package.json');
const OPTIMIZATION_TEMPLATES = require('./lib/optimization-templates.json');

class PromptOptimizerServer {
  constructor() {
    this.config = new Config();
    this.apiKey = process.env.OPTIMIZER_API_KEY || this.config.getApiKey();
    this.backendUrl = process.env.OPTIMIZER_BACKEND_URL || this.config.getBackendUrl();

    this.server = new Server(
      {
        name: "prompt-optimizer",
        version: packageJson.version,
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
  }

  setupHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "optimize_prompt",
          description: "🎯 Professional AI-powered prompt optimization with intelligent context detection, Bayesian optimization, and template auto-save.",
          inputSchema: {
            type: "object",
            properties: {
              prompt: { type: "string", description: "The prompt text to optimize" },
              goals: { 
                type: "array", 
                items: { type: "string" }, 
                description: "Optimization goals (e.g., 'clarity', 'technical_accuracy', 'conciseness')",
                default: ["clarity"]
              },
              ai_context: { 
                type: "string", 
                description: "The context for the AI's task (e.g., 'code_generation', 'image_generation')",
                enum: ["code_generation", "image_generation", "llm_interaction", "human_communication", "technical_automation", "structured_output"]
              }
            },
            required: ["prompt"]
          }
        },
        {
          name: "detect_ai_context",
          description: "🧠 Detects the AI context for a given prompt using advanced backend analysis.",
          inputSchema: {
            type: "object",
            properties: {
              prompt: { type: "string", description: "The prompt text for which to detect context" }
            },
            required: ["prompt"]
          }
        },
        {
          name: "get_quota_status",
          description: "📊 Check your current subscription status and remaining optimization quota.",
          inputSchema: { type: "object", properties: {} }
        },
        {
          name: "generate_agent_sop",
          description: "🤖 Context Engineer: Generate a structured SOP document for an AI agent.",
          inputSchema: {
            type: "object",
            properties: {
              goal: { type: "string", description: "What the agent should accomplish" },
              context: { type: "string", description: "Additional context or constraints" }
            },
            required: ["goal"]
          }
        },
        {
          name: "generate_skill_package",
          description: "📦 Context Engineer: Create a complete skill package (SOP + SKILL.md + reference).",
          inputSchema: {
            type: "object",
            properties: {
              goal: { type: "string", description: "What the agent should accomplish" }
            },
            required: ["goal"]
          }
        }
      ]
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      
      if (!this.apiKey && name !== "optimize_prompt") {
        return {
          content: [{ type: "text", text: "❌ API Key required. Set OPTIMIZER_API_KEY environment variable or run --setup." }],
          isError: true
        };
      }

      try {
        switch (name) {
          case "optimize_prompt":
            return await this.handleOptimize(args);
          case "detect_ai_context":
            return await this.handleDetectContext(args);
          case "get_quota_status":
            return await this.handleGetQuota();
          case "generate_agent_sop":
            return await this.handleGenerateSOP(args);
          case "generate_skill_package":
            return await this.handleGenerateSkill(args);
          default:
            throw new Error(`Tool not found: ${name}`);
        }
      } catch (error) {
        return {
          content: [{ type: "text", text: `Error: ${error.message}` }],
          isError: true
        };
      }
    });
  }

  async handleOptimize(args) {
    if (!this.apiKey) {
      // Fallback to local rules if no API key
      const localResult = this.applyLocalOptimization(args.prompt, args.ai_context || 'llm_interaction');
      return { content: [{ type: "text", text: this.formatLocalResult(localResult) }] };
    }

    try {
      const response = await axios.post(`${this.backendUrl}/api/v1/mcp/optimize`, {
        prompt: args.prompt,
        goals: args.goals || ['clarity'],
        ai_context: args.ai_context
      }, {
        headers: { 'X-API-Key': this.apiKey }
      });

      return { content: [{ type: "text", text: this.formatBackendResult(response.data) }] };
    } catch (error) {
      // Network failure -> Local Fallback (Tier 3)
      const localResult = this.applyLocalOptimization(args.prompt, args.ai_context || 'llm_interaction');
      localResult.fallback = true;
      return { content: [{ type: "text", text: this.formatLocalResult(localResult) }] };
    }
  }

  applyLocalOptimization(prompt, context) {
    const lc = prompt.toLowerCase();
    let bestTemplate = 'general_assistant';
    
    // Simple matching for showcase
    if (lc.includes('code') || lc.includes('fix') || lc.includes('debug')) bestTemplate = 'debugging_request';
    else if (lc.includes('image') || lc.includes('draw')) bestTemplate = 'image_generation';
    
    const template = OPTIMIZATION_TEMPLATES[bestTemplate] || OPTIMIZATION_TEMPLATES['software_engineering'];
    
    return {
      optimized_prompt: `${prompt}\n\nTo address this effectively:\n- ${template.playbook.principles.join('\n- ')}`,
      confidence: 0.45,
      context: context,
      template: bestTemplate
    };
  }

  formatLocalResult(result) {
    let output = `# 🔧 Rules-Based Optimization Applied\n\n`;
    if (result.fallback) {
      output += `⚠️ *Backend unreachable — your prompt has been structured using local rule templates.*\n\n`;
    } else {
      output += `*No API Key — using local rule templates for demonstration.*\n\n`;
    }
    output += `**Optimized Prompt:**\n\`\`\`\n${result.optimized_prompt}\n\`\`\`\n\n`;
    output += `**Confidence:** ${(result.confidence * 100).toFixed(1)}% *(rules-based)*\n`;
    return output;
  }

  formatBackendResult(data) {
    let output = `# 🎯 Optimized Prompt\n\n${data.optimized_prompt}\n\n`;
    output += `**Confidence:** ${(data.confidence_score * 100).toFixed(1)}%\n`;
    output += `**AI Context:** ${data.ai_context_detected}\n`;
    if (data.template_saved) {
      output += `\n📁 **Template Auto-Save**\n✅ Saved as template (ID: \`${data.template_id}\`)`;
    }
    return output;
  }

  async handleDetectContext(args) {
    const response = await axios.post(`${this.backendUrl}/api/v1/detect-context`, { prompt: args.prompt }, {
      headers: { 'X-API-Key': this.apiKey }
    });
    return { content: [{ type: "text", text: `**Detected Context:** ${response.data.primary_context}\n**Confidence:** ${(response.data.confidence * 100).toFixed(1)}%` }] };
  }

  async handleGetQuota() {
    const response = await axios.get(`${this.backendUrl}/api/v1/mcp/quota-status`, {
      headers: { 'X-API-Key': this.apiKey }
    });
    const { quota } = response.data;
    return { content: [{ type: "text", text: `# 📊 Quota Status\n**Remaining:** ${quota.remaining}/${quota.limit}\n**Reset Date:** ${response.data.reset_date}` }] };
  }

  async handleGenerateSOP(args) {
    const response = await axios.post(`${this.backendUrl}/api/v1/context-engineer/sop`, args, {
      headers: { 'X-API-Key': this.apiKey }
    });
    return { content: [{ type: "text", text: `# Agent SOP\n\n${response.data.sop}` }] };
  }

  async handleGenerateSkill(args) {
    const response = await axios.post(`${this.backendUrl}/api/v1/context-engineer/generate-skill-package`, args, {
      headers: { 'X-API-Key': this.apiKey }
    });
    return { content: [{ type: "text", text: `✅ Skill package generation started. Session ID: ${response.data.session_id}` }] };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('🚀 Prompt Optimizer MCP Server running...');
  }
}

// CLI Command Handling
if (require.main === module) {
  const args = process.argv.slice(2);
  const server = new PromptOptimizerServer();

  if (args.includes('--setup')) {
    require('./lib/setup')(server.config);
  } else if (args.includes('--version')) {
    console.log(`v${packageJson.version}`);
  } else {
    server.run().catch(console.error);
  }
}

module.exports = PromptOptimizerServer;
