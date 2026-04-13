const readline = require('readline');

module.exports = function(config) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  console.log('🔧 Prompt Optimizer Setup');
  console.log('Get your API key from: https://promptoptimizer.xyz/dashboard\n');
  
  rl.question('Enter your API key (sk-opt-...): ', (apiKey) => {
    if (!apiKey || (!apiKey.startsWith('sk-opt-') && !apiKey.startsWith('sk-team-') && !apiKey.startsWith('sk-local-'))) {
      console.error('❌ Invalid API key format.');
      process.exit(1);
    }

    if (config.setApiKey(apiKey)) {
      console.log('✅ API key saved successfully.');
      console.log('\n📋 Add this to your Claude Desktop config (~/.claude/claude_desktop_config.json):');
      console.log(JSON.stringify({
        "mcpServers": {
          "prompt-optimizer": {
            "command": "npx",
            "args": ["mcp-prompt-optimizer"]
          }
        }
      }, null, 2));
      
      console.log('\n🎉 Setup complete! Restart your MCP client.');
    } else {
      console.error('❌ Failed to save configuration.');
    }
    
    rl.close();
  });
};
