"""Configuration management for Rapid Dev Proxy."""

from typing import Dict, Optional, List
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class ProxySettings(BaseModel):
    """Proxy server settings."""
    host: str = Field(default="127.0.0.1", description="Host to bind to")
    port: int = Field(default=8080, ge=1, le=65535, description="Port to bind to")
    timeout: float = Field(default=30.0, gt=0, description="Request timeout in seconds")
    max_connections: int = Field(default=100, gt=0, description="Maximum concurrent connections")


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO", description="Log level")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    destination: str = Field(default="console", description="Log destination (console/file)")


class SecuritySettings(BaseModel):
    """Security settings."""
    cors_enabled: bool = Field(default=True, description="Enable CORS headers")
    rate_limit_enabled: bool = Field(default=False, description="Enable rate limiting")
    auth_headers: Dict[str, str] = Field(default_factory=dict, description="Additional auth headers")


class RouteConfig(BaseModel):
    """Route configuration."""
    target: str = Field(description="Target URL (e.g., http://127.0.0.1:3000)")
    metadata: Optional[Dict[str, str]] = Field(default_factory=dict, description="Route metadata")
    aliases: List[str] = Field(default_factory=list, description="Alternate hostnames that should map to this route")

    @validator('target')
    def validate_target(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Target must be a valid HTTP/HTTPS URL')
        return v


class DefaultRoute(BaseModel):
    """Default route configuration."""
    target: str = Field(description="Default target URL")
    error_pages: Dict[int, str] = Field(default_factory=dict, description="Custom error pages")


class ProxyConfig(BaseModel):
    """Main proxy configuration."""
    proxy: ProxySettings = Field(default_factory=ProxySettings)
    routes: Dict[str, RouteConfig] = Field(description="Domain to route mappings")
    default: DefaultRoute = Field(description="Default route configuration")
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    @validator('routes')
    def validate_routes(cls, v):
        if not v:
            raise ValueError('At least one route must be defined')
        return v


class Settings(BaseSettings):
    """Application settings."""
    config_file: str = Field(default="config.json", description="Configuration file path")
    debug: bool = Field(default=False, description="Enable debug mode")

    model_config = {"env_prefix": "RAPID_PROXY_"} 