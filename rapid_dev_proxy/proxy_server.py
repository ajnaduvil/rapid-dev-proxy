"""Main proxy server implementation."""

import logging
import time
from typing import Dict, Optional

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse

from .config_manager import ConfigManager

logger = logging.getLogger(__name__)


class ProxyServer:
    """Main proxy server implementation."""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.app = FastAPI(title="Rapid Dev Proxy", version="0.1.0")
        self.client: Optional[httpx.AsyncClient] = None
        self.request_count = 0
        self.error_count = 0

        self._setup_middleware()
        self._setup_routes()

    def _setup_middleware(self):
        """Setup middleware for the FastAPI app."""
        # CORS middleware
        if self.config_manager.config.security.cors_enabled:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

    def _setup_routes(self):
        """Setup routes for the FastAPI app."""
        
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            """Log all requests."""
            start_time = time.time()
            self.request_count += 1
            
            response = await call_next(request)
            
            process_time = time.time() - start_time
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            return response

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "request_count": self.request_count,
                "error_count": self.error_count,
                "uptime": time.time()
            }

        @self.app.get("/routes")
        async def list_routes():
            """List all configured routes."""
            config = self.config_manager.config
            return {
                "routes": config.routes,
                "default": config.default.target
            }

        # Register catch-all proxy route last to avoid shadowing built-in endpoints
        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
        async def proxy_request(request: Request, path: str):
            """Proxy all requests to backend services."""
            return await self._handle_proxy_request(request, path)

    async def _handle_proxy_request(self, request: Request, path: str) -> Response:
        """Handle proxy request to backend service."""
        try:
            # Resolve effective host for routing with override mechanisms
            # Priority order: query param _host -> header x-rdp-host -> path prefix -> Host header
            effective_host: str = ""

            # Query parameter override
            override_host_qp = request.query_params.get("_host")
            if override_host_qp:
                effective_host = override_host_qp

            # Header override if not set via query
            if not effective_host:
                override_host_header = request.headers.get("x-rdp-host") or request.headers.get("x-host")
                if override_host_header:
                    effective_host = override_host_header

            # Path prefix override if not set yet: supports `__host/<domain>/...` or `@<domain>/...`
            # Only consider if path begins with these markers
            stripped_path = path
            if not effective_host and path:
                if path.startswith("__host/"):
                    parts = path.split('/', 2)
                    if len(parts) >= 2:
                        effective_host = parts[1]
                        stripped_path = parts[2] if len(parts) > 2 else ""
                elif path.startswith("@"):
                    # format: @domain/remaining
                    at_parts = path[1:].split('/', 1)
                    if at_parts and at_parts[0]:
                        effective_host = at_parts[0]
                        stripped_path = at_parts[1] if len(at_parts) > 1 else ""

            # Fallback to the actual Host header
            if not effective_host:
                effective_host = request.headers.get("host", "")

            target_url = self.config_manager.get_route(effective_host)
            
            if not target_url:
                self.error_count += 1
                return Response(
                    content="No route found for host",
                    status_code=404,
                    media_type="text/plain"
                )

            # Build target URL
            target_path = f"{target_url.rstrip('/')}/{stripped_path}"
            
            # Prepare headers for forwarding
            headers = dict(request.headers)
            # Remove headers that shouldn't be forwarded
            headers.pop("host", None)
            headers.pop("content-length", None)
            # Remove override headers so they don't leak to backend
            headers.pop("x-rdp-host", None)
            headers.pop("x-host", None)
            
            # Add any configured auth headers
            for key, value in self.config_manager.config.security.auth_headers.items():
                headers[key] = value

            # Prepare request body
            body = await request.body()

            # Make request to backend
            async with httpx.AsyncClient(timeout=self.config_manager.config.proxy.timeout) as client:
                # Filter query params to remove internal override keys
                forwarded_params: Dict[str, str] = dict(request.query_params)
                forwarded_params.pop("_host", None)

                response = await client.request(
                    method=request.method,
                    url=target_path,
                    headers=headers,
                    content=body,
                    params=forwarded_params,
                    follow_redirects=False
                )

                # Prepare response headers
                response_headers = dict(response.headers)
                response_headers.pop("content-length", None)

                # Return streaming response
                return StreamingResponse(
                    content=response.aiter_bytes(),
                    status_code=response.status_code,
                    headers=response_headers,
                    media_type=response.headers.get("content-type")
                )

        except httpx.ConnectError:
            self.error_count += 1
            logger.error(f"Connection error to backend: {target_url}")
            return Response(
                content="Backend service unavailable",
                status_code=502,
                media_type="text/plain"
            )
        except httpx.TimeoutException:
            self.error_count += 1
            logger.error(f"Timeout error to backend: {target_url}")
            return Response(
                content="Backend service timeout",
                status_code=504,
                media_type="text/plain"
            )
        except Exception as e:
            self.error_count += 1
            logger.error(f"Proxy error: {e}")
            return Response(
                content="Internal proxy error",
                status_code=500,
                media_type="text/plain"
            )

    async def startup(self):
        """Startup event handler."""
        logger.info("Starting Rapid Dev Proxy...")
        logger.info(f"Loaded {len(self.config_manager.config.routes)} routes")

    async def shutdown(self):
        """Shutdown event handler."""
        logger.info("Shutting down Rapid Dev Proxy...")
        if self.client:
            await self.client.aclose()

    def get_app(self) -> FastAPI:
        """Get the FastAPI app instance."""
        return self.app 