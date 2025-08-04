"""Demo script for Rapid Dev Proxy."""

import asyncio
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DemoServer:
    """Simple demo server for testing the proxy."""

    def __init__(self, port: int, name: str):
        self.port = port
        self.name = name
        self.app = FastAPI(title=f"Demo Server - {name}")

        @self.app.get("/")
        async def root():
            return {"message": f"Hello from {name}", "port": port}

        @self.app.get("/health")
        async def health():
            return {"status": "healthy", "server": name}

    def start(self):
        """Start the demo server."""
        uvicorn.run(self.app, host="127.0.0.1", port=self.port, log_level="error")


def create_demo_config():
    """Create a demo configuration file."""
    config = {
        "proxy": {
            "host": "127.0.0.1",
            "port": 8080,
            "timeout": 30.0,
            "max_connections": 100
        },
        "routes": {
            "api.local": {
                "target": "http://127.0.0.1:3000",
                "metadata": {
                    "description": "API Server"
                }
            },
            "app.local": {
                "target": "http://127.0.0.1:3001",
                "metadata": {
                    "description": "Frontend App"
                }
            },
            "admin.local": {
                "target": "http://127.0.0.1:3002",
                "metadata": {
                    "description": "Admin Panel"
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
            "cors_enabled": True,
            "rate_limit_enabled": False,
            "auth_headers": {}
        }
    }

    with open("demo_config.json", "w") as f:
        json.dump(config, f, indent=2)

    logger.info("Created demo_config.json")


async def test_proxy():
    """Test the proxy with demo servers."""
    logger.info("Testing proxy functionality...")

    # Test health endpoint
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8080/health")
        logger.info(f"Health check: {response.status_code}")
        logger.info(f"Health response: {response.json()}")

        # Test routes endpoint
        response = await client.get("http://127.0.0.1:8080/routes")
        logger.info(f"Routes check: {response.status_code}")
        logger.info(f"Routes response: {response.json()}")

        # Test proxy to API server
        response = await client.get("http://127.0.0.1:8080/", headers={"Host": "api.local"})
        logger.info(f"API proxy: {response.status_code}")
        logger.info(f"API response: {response.json()}")

        # Test proxy to App server
        response = await client.get("http://127.0.0.1:8080/", headers={"Host": "app.local"})
        logger.info(f"App proxy: {response.status_code}")
        logger.info(f"App response: {response.json()}")

        # Test proxy to Admin server
        response = await client.get("http://127.0.0.1:8080/", headers={"Host": "admin.local"})
        logger.info(f"Admin proxy: {response.status_code}")
        logger.info(f"Admin response: {response.json()}")


def main():
    """Main demo function."""
    logger.info("Starting Rapid Dev Proxy Demo")
    logger.info("This demo will:")
    logger.info("1. Create a demo configuration")
    logger.info("2. Start 3 demo servers on ports 3000, 3001, 3002")
    logger.info("3. Start the proxy server on port 8080")
    logger.info("4. Test the proxy functionality")
    logger.info("5. Clean up")

    # Create demo config
    create_demo_config()

    # Start demo servers in background
    logger.info("Starting demo servers...")
    
    # Start API server
    api_server = DemoServer(3000, "API Server")
    api_process = subprocess.Popen([
        sys.executable, "-c", 
        "import uvicorn; from demo import DemoServer; "
        "server = DemoServer(3000, 'API Server'); "
        "uvicorn.run(server.app, host='127.0.0.1', port=3000, log_level='error')"
    ])

    # Start App server
    app_server = DemoServer(3001, "Frontend App")
    app_process = subprocess.Popen([
        sys.executable, "-c", 
        "import uvicorn; from demo import DemoServer; "
        "server = DemoServer(3001, 'Frontend App'); "
        "uvicorn.run(server.app, host='127.0.0.1', port=3001, log_level='error')"
    ])

    # Start Admin server
    admin_server = DemoServer(3002, "Admin Panel")
    admin_process = subprocess.Popen([
        sys.executable, "-c", 
        "import uvicorn; from demo import DemoServer; "
        "server = DemoServer(3002, 'Admin Panel'); "
        "uvicorn.run(server.app, host='127.0.0.1', port=3002, log_level='error')"
    ])

    # Wait for servers to start
    time.sleep(3)

    # Start proxy server
    logger.info("Starting proxy server...")
    proxy_process = subprocess.Popen([
        "uv", "run", "python", "-m", "rapid_dev_proxy.cli", "start", 
        "-c", "demo_config.json", "--port", "8080"
    ])

    # Wait for proxy to start
    time.sleep(3)

    # Test the proxy
    try:
        asyncio.run(test_proxy())
    except Exception as e:
        logger.error(f"Error testing proxy: {e}")

    # Clean up
    logger.info("Cleaning up...")
    api_process.terminate()
    app_process.terminate()
    admin_process.terminate()
    proxy_process.terminate()

    # Remove demo config
    Path("demo_config.json").unlink(missing_ok=True)

    logger.info("Demo completed!")


if __name__ == "__main__":
    main() 