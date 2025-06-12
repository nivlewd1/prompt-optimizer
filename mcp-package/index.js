#!/usr/bin/env node

const MCPServer = require('./lib/mcp-protocol');
const Config = require('./lib/config');

async function setup() {
  const readline = require('readline');
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  return new Promise((resolve) => {
    console.log('🔧 MCP Prompt Optimizer Setup');
    console.log('Get your API key from: https://promptoptimizer-blog.vercel.app/dashboard\n');
    
    rl.question('Enter your API key: ', (apiKey) => {
      if (!apiKey || !apiKey.startsWith('sk-opt-')) {
        console.error('❌ Invalid API key format. Must start with "sk-opt-"');
        process.exit(1);
      }

      const config = new Config();
      if (config.setApiKey(apiKey)) {
        console.log('✅ API key saved successfully');
        console.log('\n📋 Add this to your Claude Desktop config:');
        console.log('File location: ~/.claude/claude_desktop_config.json');
        console.log(JSON.stringify({
          "mcpServers": {
            "prompt-optimizer": {
              "command": "npx",
              "args": ["mcp-prompt-optimizer"]
            }
          }
        }, null, 2));
        
        console.log('\n📋 Or for Cursor:');
        console.log('File location: ~/.cursor/mcp.json');
        console.log(JSON.stringify({
          "mcpServers": {
            "prompt-optimizer": {
              "command": "npx",
              "args": ["mcp-prompt-optimizer"]
            }
          }
        }, null, 2));

        console.log('\n📋 Or for Windsurf:');
        console.log('Add via Windsurf settings or config file');
        console.log(JSON.stringify({
          "mcpServers": {
            "prompt-optimizer": {
              "command": "npx",
              "args": ["mcp-prompt-optimizer"]
            }
          }
        }, null, 2));

        console.log('\n🎉 Setup complete! Restart your MCP client to use the tool.');
        console.log('💡 Run "mcp-prompt-optimizer" to test the server manually.');
      } else {
        console.error('❌ Failed to save configuration');
        process.exit(1);
      }
      
      rl.close();
      resolve();
    });
  });
}

async function startServer() {
  const config = new Config();
  const apiKey = config.getApiKey();
  
  if (!apiKey) {
    console.error('❌ No API key found. Run: mcp-prompt-optimizer --setup');
    process.exit(1);
  }

  const server = new MCPServer(apiKey);
  
  if (!(await server.initialize())) {
    console.error('💡 If your API key is invalid, run: mcp-prompt-optimizer --setup');
    process.exit(1);
  }

  // Handle STDIO communication (MCP protocol)
  process.stdin.setEncoding('utf8');
  
  let buffer = '';
  process.stdin.on('data', async (chunk) => {
    buffer += chunk;
    
    // Process complete lines (JSON-RPC messages)
    let lines = buffer.split('\n');
    buffer = lines.pop(); // Keep incomplete line in buffer
    
    for (const line of lines) {
      if (line.trim()) {
        try {
          const message = JSON.parse(line);
          const response = await server.handleMessage(message);
          process.stdout.write(JSON.stringify(response) + '\n');
        } catch (error) {
          console.error('Protocol error:', error.message);
          // Send proper JSON-RPC error response
          const errorResponse = {
            jsonrpc: "2.0",
            id: null,
            error: {
              code: -32700,
              message: 'Parse error'
            }
          };
          process.stdout.write(JSON.stringify(errorResponse) + '\n');
        }
      }
    }
  });

  process.stdin.on('end', () => {
    console.error('📡 MCP connection closed');
    process.exit(0);
  });

  process.on('SIGINT', () => {
    console.error('\n👋 MCP server shutting down...');
    process.exit(0);
  });

  process.on('SIGTERM', () => {
    console.error('\n👋 MCP server shutting down...');
    process.exit(0);
  });

  console.error('🚀 MCP Prompt Optimizer Server running...');
  console.error('💡 Use Ctrl+C to stop the server');
}

async function showHelp() {
  console.log('MCP Prompt Optimizer - Local server for prompt optimization');
  console.log('');
  console.log('Usage:');
  console.log('  mcp-prompt-optimizer          Start the MCP server');
  console.log('  mcp-prompt-optimizer --setup  Configure API key');
  console.log('  mcp-prompt-optimizer --help   Show this help');
  console.log('  mcp-prompt-optimizer --version Show version');
  console.log('');
  console.log('Configuration:');
  console.log('  Config file: ~/.prompt-optimizer/config.json');
  console.log('  API keys: Get from https://promptoptimizer-blog.vercel.app/dashboard');
  console.log('');
  console.log('Supported MCP clients:');
  console.log('  - Claude Desktop');
  console.log('  - Cursor IDE');  
  console.log('  - Windsurf IDE');
}

async function showVersion() {
  const packageJson = require('./package.json');
  console.log(`mcp-prompt-optimizer v${packageJson.version}`);
}

// Main execution
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.includes('--setup')) {
    setup();
  } else if (args.includes('--help') || args.includes('-h')) {
    showHelp();
  } else if (args.includes('--version') || args.includes('-v')) {
    showVersion();
  } else {
    startServer();
  }
}

module.exports = MCPServer;