#!/usr/bin/env node

/**
 * Test script for MCP Prompt Optimizer package
 * Run with: node test-package.js or npm test
 */

const Config = require('./lib/config');
const MCPServer = require('./lib/mcp-protocol');
const PromptOptimizerApiClient = require('./lib/api-client');

async function runTests() {
  console.log('🧪 Testing MCP Prompt Optimizer Package v1.0.1\n');

  // Test 1: Config Management
  console.log('1️⃣ Testing Config Management...');
  const config = new Config();
  
  // Test saving/loading config
  const testApiKey = 'sk-opt-test123456789';
  const saveResult = config.setApiKey(testApiKey);
  const loadedKey = config.getApiKey();
  
  if (saveResult && loadedKey === testApiKey) {
    console.log('   ✅ Config save/load works');
  } else {
    console.log('   ❌ Config save/load failed');
    return;
  }

  // Test backend URL configuration
  const backendUrl = config.getBackendUrl();
  const expectedUrl = 'https://p01--project-optimizer--fvrdk8m9k9j.code.run';
  if (backendUrl === expectedUrl) {
    console.log('   ✅ Backend URL correctly configured');
    console.log(`   📋 Backend URL: ${backendUrl}`);
  } else {
    console.log('   ❌ Backend URL configuration failed');
    console.log(`   📋 Expected: ${expectedUrl}`);
    console.log(`   📋 Got: ${backendUrl}`);
  }

  // Test MCP Server Initialization
  console.log('\n2️⃣ Testing MCP Server Initialization...');
  const server = new MCPServer(testApiKey);
  
  if (server && server.tools && server.tools.length > 0) {
    console.log('   ✅ MCP Server created with tools');
    console.log(`   📋 Available tools: ${server.tools.map(t => t.name).join(', ')}`);
    
    // Check tool schema
    const optimizeTool = server.tools.find(t => t.name === 'optimize_prompt');
    if (optimizeTool && optimizeTool.inputSchema && optimizeTool.inputSchema.properties) {
      console.log('   ✅ optimize_prompt tool has proper schema');
      const goals = optimizeTool.inputSchema.properties.goals;
      if (goals && goals.items && goals.items.enum && goals.items.enum.length >= 10) {
        console.log(`   ✅ Optimization goals available: ${goals.items.enum.length} goals`);
        console.log(`   📋 Goals: ${goals.items.enum.slice(0, 5).join(', ')}...`);
      } else {
        console.log('   ❌ Optimization goals schema invalid');
      }
    } else {
      console.log('   ❌ optimize_prompt tool schema missing');
    }
  } else {
    console.log('   ❌ MCP Server initialization failed');
    return;
  }

  // Cleanup test config
  config.clear();
  console.log('\n🧹 Cleaned up test configuration');

  console.log('\n✅ Package structure verification complete!');
  console.log('\n🚀 Package v1.0.1 is ready for deployment!');
  console.log('\n📡 Backend: https://p01--project-optimizer--fvrdk8m9k9j.code.run');
}

// Run tests with error handling
if (require.main === module) {
  runTests().catch((error) => {
    console.error('\n❌ Test execution failed:');
    console.error(error);
    process.exit(1);
  });
}

module.exports = { runTests };