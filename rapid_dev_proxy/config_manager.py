"""Configuration manager for loading and validating proxy configurations."""

import json
import logging
from pathlib import Path
from typing import Optional

import yaml
from pydantic import ValidationError

from .config import ProxyConfig, Settings

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration loading and validation."""

    def __init__(self, config_file: Optional[str] = None):
        self.settings = Settings()
        self.config_file = config_file or self.settings.config_file
        self.config: Optional[ProxyConfig] = None

    def load_config(self) -> ProxyConfig:
        """Load configuration from file."""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)

            self.config = ProxyConfig(**data)
            logger.info(f"Configuration loaded successfully from {self.config_file}")
            return self.config

        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Invalid configuration file format: {e}")
        except ValidationError as e:
            raise ValueError(f"Configuration validation failed: {e}")

    def validate_config(self) -> bool:
        """Validate the current configuration."""
        if not self.config:
            self.load_config()

        try:
            # Additional validation logic can be added here
            logger.info("Configuration validation passed")
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

    def get_route(self, host: str) -> Optional[str]:
        """Get target URL for a given host.

        Enhancements to avoid hosts file requirements:
        - Supports alias matching per route (exact and wildcard).
        - Treats any "<domain>.localhost" as an alias for "<domain>" to leverage the special .localhost TLD.
        """
        if not self.config:
            self.load_config()

        if host is None:
            host = ""

        # Normalize and remove port from host if present
        host = host.split(':')[0].strip().lower()

        # Support <domain>.localhost mapping without hosts file changes
        if host.endswith('.localhost'):
            host = host[: -len('.localhost')]

        # Check for exact match first
        if host in self.config.routes:
            return self.config.routes[host].target

        # Check for alias match (including wildcard aliases)
        for domain, route in self.config.routes.items():
            # Exact alias match
            for alias in getattr(route, 'aliases', []) or []:
                alias_norm = alias.strip().lower()
                if alias_norm == host:
                    return route.target
                if alias_norm.startswith('*.') and host.endswith(alias_norm[1:]):
                    return route.target

        # Check for wildcard subdomain match on primary domain
        for domain, route in self.config.routes.items():
            domain_norm = domain.strip().lower()
            if domain_norm.startswith('*.') and host.endswith(domain_norm[1:]):
                return route.target

        # Return default route
        return self.config.default.target

    def reload_config(self) -> ProxyConfig:
        """Reload configuration from file."""
        logger.info("Reloading configuration...")
        return self.load_config()

    def create_sample_config(self, output_file: str = "config.json") -> None:
        """Create a sample configuration file."""
        sample_config = {
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
                    "target": "http://127.0.0.1:8080",
                    "metadata": {
                        "description": "Frontend App"
                    }
                },
                "admin.local": {
                    "target": "http://127.0.0.1:9000",
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

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2)

        logger.info(f"Sample configuration created: {output_file}") 