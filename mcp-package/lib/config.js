const fs = require('fs');
const path = require('path');
const os = require('os');

class Config {
  constructor() {
    this.configDir = path.join(os.homedir(), '.prompt-optimizer');
    this.configFile = path.join(this.configDir, 'config.json');
  }

  load() {
    try {
      if (fs.existsSync(this.configFile)) {
        const data = fs.readFileSync(this.configFile, 'utf8');
        return JSON.parse(data);
      }
    } catch (error) {
      console.error('Error loading config:', error.message);
    }
    return null;
  }

  save(config) {
    try {
      fs.mkdirSync(this.configDir, { recursive: true });
      fs.writeFileSync(this.configFile, JSON.stringify(config, null, 2));
      return true;
    } catch (error) {
      console.error('Error saving config:', error.message);
      return false;
    }
  }

  getApiKey() {
    const config = this.load();
    return config?.apiKey;
  }

  setApiKey(apiKey) {
    const config = this.load() || {};
    config.apiKey = apiKey;
    config.updatedAt = new Date().toISOString();
    return this.save(config);
  }

  getBackendUrl() {
    const config = this.load();
    return config?.backendUrl || 'https://p01--project-optimizer--fvrdk8m9k9j.code.run';
  }

  setBackendUrl(url) {
    const config = this.load() || {};
    config.backendUrl = url;
    config.updatedAt = new Date().toISOString();
    return this.save(config);
  }

  clear() {
    try {
      if (fs.existsSync(this.configFile)) {
        fs.unlinkSync(this.configFile);
        return true;
      }
    } catch (error) {
      console.error('Error clearing config:', error.message);
    }
    return false;
  }

  exists() {
    return fs.existsSync(this.configFile);
  }
}

module.exports = Config;