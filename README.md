# MCP Prompt Optimizer

A high-performance server implementation for optimizing large language model prompts with real-time streaming capabilities, pattern-based enhancement, and comprehensive session management.

## Features

- **Real-time Prompt Optimization**: Stream-based optimization with adaptive processing levels
- **Pattern-Based Enhancement**: Intelligent pattern detection and application for improved prompt quality
- **Comprehensive Session Management**: Robust session handling with transport-aware capabilities
- **Rate Limiting**: Adaptive rate limiting with size-aware token management
- **Security**: Enhanced security features with proper encryption and validation
- **Windows Support**: Optimized for Windows environments with proper resource management
- **Metrics Collection**: Detailed metrics tracking and performance monitoring
- **Configuration Management**: Dynamic configuration with validation and hot-reload support

## Technical Stack

- **Language**: Python 3.8+
- **Core Dependencies**:
  - FastAPI for API endpoints
  - DSPy for prompt optimization
  - asyncio for asynchronous operations
  - SQLite for session persistence
  - WebSocket support for real-time communication

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nivlewd1/mcp-prompt-optimizer.git
cd mcp-prompt-optimizer
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Configuration is managed through JSON files in the config directory. Key configuration options include:

- Rate limiting rules
- Session timeout settings
- Transport configurations
- Optimization parameters

See the `config.json` example for detailed settings.

## Usage

Start the server:
```bash
python -m app.run_server
```

The server supports both WebSocket and STDIO transport modes for flexibility in different deployment scenarios.

## Development

### Project Structure
```
mcp/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config_manager.py
│   ├── connection.py
│   ├── conversation_handler.py
│   ├── initialization.py
│   ├── interfaces.py
│   ├── models.py
│   ├── prompt_optimizer.py
│   ├── prompt_patterns.py
│   ├── prompt_strategies.py
│   ├── protocol_handler.py
│   ├── rate_limiter.py
│   ├── run_server.py
│   ├── session_manager.py
│   ├── shared_types.py
│   └── transport_manager.py
└── tests/
    └── ... (test files)
```

### Testing

Run tests with:
```bash
pytest tests/
```

## License

All rights reserved. This source code is proprietary and confidential.

## Support

For issues and support, please contact the development team.
