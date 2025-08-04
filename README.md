# Rapid Dev Proxy

A high-performance, configuration-driven reverse proxy tool built in Python that enables developers to easily route HTTP requests from custom domain names to different backend services running on localhost ports.

## Features

- **Simple Configuration**: Single JSON/YAML configuration file
- **Host-based Routing**: Route requests based on HTTP Host header
- **Fast Performance**: Built with FastAPI and async I/O
- **Easy Setup**: Minimal configuration for local development
- **Health Monitoring**: Built-in health check and monitoring endpoints
- **CORS Support**: Automatic CORS handling for development
- **Rich CLI**: Beautiful command-line interface with Rich

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd rapid-dev-proxy

# Install dependencies
uv sync

# Install the package in development mode
uv pip install -e .
```

### Using pip

```bash
pip install rapid-dev-proxy
```

## Quick Start

1. **Create a sample configuration**:
   ```bash
   rapid-dev-proxy init
   ```

2. **Edit the configuration file** (`config.json`):
   ```json
   {
     "proxy": {
       "host": "127.0.0.1",
       "port": 8080
     },
     "routes": {
       "api.local": {
         "target": "http://127.0.0.1:3000",
         "metadata": {
           "description": "API Server"
         }
       },
       "app.local": {
         "target": "http://127.0.0.1:8080",
         "metadata": {
           "description": "Frontend App"
         }
       }
     },
     "default": {
       "target": "http://127.0.0.1:3000"
     }
   }
   ```

3. **Start the proxy server**:
   ```bash
   rapid-dev-proxy start
   ```

4. **Add to your hosts file** (optional):
   ```
   127.0.0.1 api.local
   127.0.0.1 app.local
   ```

5. **Access your services**:
   - API: http://api.local:8080
   - App: http://app.local:8080

## Configuration

### Configuration File Format

The proxy uses a JSON or YAML configuration file with the following structure:

```json
{
  "proxy": {
    "host": "127.0.0.1",
    "port": 8080,
    "timeout": 30.0,
    "max_connections": 100
  },
  "routes": {
    "domain.local": {
      "target": "http://127.0.0.1:3000",
      "metadata": {
        "description": "Service Description"
      }
    }
  },
  "default": {
    "target": "http://127.0.0.1:3000",
    "error_pages": {
      "404": "Not Found",
      "502": "Bad Gateway"
    }
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "destination": "console"
  },
  "security": {
    "cors_enabled": true,
    "rate_limit_enabled": false,
    "auth_headers": {}
  }
}
```

### Configuration Options

| Section | Option | Type | Default | Description |
|---------|--------|------|---------|-------------|
| `proxy` | `host` | string | `127.0.0.1` | Host to bind to |
| `proxy` | `port` | integer | `8080` | Port to bind to |
| `proxy` | `timeout` | float | `30.0` | Request timeout in seconds |
| `proxy` | `max_connections` | integer | `100` | Maximum concurrent connections |
| `routes` | `domain` | object | - | Domain to route mapping |
| `default` | `target` | string | - | Default target URL |
| `logging` | `level` | string | `INFO` | Log level |
| `security` | `cors_enabled` | boolean | `true` | Enable CORS headers |

## Command Line Interface

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `start` | Start the proxy server | `rapid-dev-proxy start` |
| `validate` | Validate configuration | `rapid-dev-proxy validate` |
| `init` | Create sample config | `rapid-dev-proxy init` |
| `routes` | List configured routes | `rapid-dev-proxy routes` |
| `version` | Show version info | `rapid-dev-proxy version` |

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--config, -c` | Configuration file path | `config.json` |
| `--host, -h` | Override bind host | From config |
| `--port, -p` | Override bind port | From config |
| `--reload` | Enable auto-reload | `false` |
| `--debug` | Enable debug mode | `false` |

## API Endpoints

The proxy server provides several built-in endpoints:

- `GET /health` - Health check and statistics
- `GET /routes` - List all configured routes
- `{path}` - Proxy all other requests to backend services

## Development

### Project Structure

```
rapid-dev-proxy/
├── rapid_dev_proxy/
│   ├── __init__.py
│   ├── config.py          # Configuration models
│   ├── config_manager.py  # Configuration management
│   ├── proxy_server.py    # Main proxy server
│   └── cli.py            # Command line interface
├── pyproject.toml
├── README.md
└── config.json
```

### Running in Development

```bash
# Install in development mode
uv pip install -e .

# Run with auto-reload
rapid-dev-proxy start --reload --debug

# Run tests
uv run pytest
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=rapid_dev_proxy

# Run specific test file
uv run pytest tests/test_proxy_server.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- CLI powered by [Click](https://click.palletsprojects.com/)
- Beautiful output with [Rich](https://rich.readthedocs.io/)
- Configuration validation with [Pydantic](https://pydantic-docs.helpmanual.io/) 