# Rapid Dev Proxy - Example Usage

This guide demonstrates how to use the Rapid Dev Proxy for local development.

## Prerequisites

1. Install the proxy:
   ```bash
   uv pip install -e .
   ```

2. Create a sample configuration:
   ```bash
   uv run python -m rapid_dev_proxy.cli init
   ```

## Example 1: Basic Setup

### Step 1: Create Configuration

The `init` command creates a `config.json` file with sample routes:

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

### Step 2: Start Your Backend Services

Start your backend services on the configured ports:

```bash
# Start API server on port 3000
python -m http.server 3000

# Start frontend app on port 8080
python -m http.server 8080
```

### Step 3: Start the Proxy

```bash
uv run python -m rapid_dev_proxy.cli start
```

### Step 4: Test the Proxy

```bash
# Test API route
curl -H "Host: api.local" http://127.0.0.1:8080/

# Test app route
curl -H "Host: app.local" http://127.0.0.1:8080/

# Test health endpoint
curl http://127.0.0.1:8080/health

# List routes
curl http://127.0.0.1:8080/routes
```

## Example 2: Development Workflow

### Step 1: Set up your development environment

```bash
# Create a development configuration
uv run python -m rapid_dev_proxy.cli init dev-config.json

# Edit the configuration for your services
# Add routes for your frontend, API, admin panel, etc.
```

### Step 2: Start your services

```bash
# Terminal 1: Start your React app
cd frontend && npm start

# Terminal 2: Start your API server
cd api && python app.py

# Terminal 3: Start your admin panel
cd admin && python server.py
```

### Step 3: Start the proxy

```bash
uv run python -m rapid_dev_proxy.cli start -c dev-config.json --reload
```

### Step 4: Access your services

- Frontend: http://app.local:8080
- API: http://api.local:8080
- Admin: http://admin.local:8080

## Example 3: Advanced Configuration

### Custom Configuration

```json
{
  "proxy": {
    "host": "0.0.0.0",
    "port": 9000,
    "timeout": 60.0,
    "max_connections": 200
  },
  "routes": {
    "api.dev.local": {
      "target": "http://127.0.0.1:3000",
      "metadata": {
        "description": "Development API"
      }
    },
    "*.dev.local": {
      "target": "http://127.0.0.1:8080",
      "metadata": {
        "description": "Wildcard route"
      }
    }
  },
  "default": {
    "target": "http://127.0.0.1:3000"
  },
  "security": {
    "cors_enabled": true,
    "auth_headers": {
      "X-API-Key": "dev-key-123"
    }
  }
}
```

### Start with custom configuration

```bash
uv run python -m rapid_dev_proxy.cli start -c custom-config.json --port 9000 --debug
```

## Example 4: Testing and Validation

### Validate Configuration

```bash
uv run python -m rapid_dev_proxy.cli validate -c config.json
```

### List Routes

```bash
uv run python -m rapid_dev_proxy.cli routes -c config.json
```

### Health Check

```bash
curl http://127.0.0.1:8080/health
```

Response:
```json
{
  "status": "healthy",
  "request_count": 42,
  "error_count": 0,
  "uptime": 1234.567
}
```

## Example 5: Integration with Hosts File

For easier access, add entries to your hosts file:

### Windows (C:\Windows\System32\drivers\etc\hosts)
```
127.0.0.1 api.local
127.0.0.1 app.local
127.0.0.1 admin.local
```

### Linux/Mac (/etc/hosts)
```
127.0.0.1 api.local
127.0.0.1 app.local
127.0.0.1 admin.local
```

Then access your services directly:
- http://api.local:8080
- http://app.local:8080
- http://admin.local:8080

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the proxy port in configuration
2. **Backend service not responding**: Check if your backend service is running
3. **Configuration errors**: Use `validate` command to check configuration
4. **CORS issues**: Ensure CORS is enabled in configuration

### Debug Mode

Run with debug mode for detailed logging:

```bash
uv run python -m rapid_dev_proxy.cli start --debug
```

### Check Logs

The proxy logs all requests and errors. Look for:
- Request/response details
- Routing decisions
- Error messages
- Performance metrics 