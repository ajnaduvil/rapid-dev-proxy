"""Tests for configuration module."""

import pytest
from pydantic import ValidationError

from rapid_dev_proxy.config import ProxyConfig, RouteConfig, ProxySettings


class TestProxySettings:
    """Test ProxySettings model."""

    def test_valid_settings(self):
        """Test valid proxy settings."""
        settings = ProxySettings(host="127.0.0.1", port=8080)
        assert settings.host == "127.0.0.1"
        assert settings.port == 8080

    def test_invalid_port(self):
        """Test invalid port validation."""
        with pytest.raises(ValidationError):
            ProxySettings(port=70000)

    def test_default_values(self):
        """Test default values."""
        settings = ProxySettings()
        assert settings.host == "127.0.0.1"
        assert settings.port == 8080


class TestRouteConfig:
    """Test RouteConfig model."""

    def test_valid_route(self):
        """Test valid route configuration."""
        route = RouteConfig(target="http://127.0.0.1:3000")
        assert route.target == "http://127.0.0.1:3000"

    def test_invalid_target(self):
        """Test invalid target URL."""
        with pytest.raises(ValidationError):
            RouteConfig(target="invalid-url")

    def test_metadata(self):
        """Test route metadata."""
        route = RouteConfig(
            target="http://127.0.0.1:3000",
            metadata={"description": "API Server"}
        )
        assert route.metadata["description"] == "API Server"


class TestProxyConfig:
    """Test ProxyConfig model."""

    def test_valid_config(self):
        """Test valid proxy configuration."""
        config_data = {
            "routes": {
                "api.local": {
                    "target": "http://127.0.0.1:3000"
                }
            },
            "default": {
                "target": "http://127.0.0.1:3000"
            }
        }
        config = ProxyConfig(**config_data)
        assert len(config.routes) == 1
        assert "api.local" in config.routes

    def test_empty_routes(self):
        """Test configuration with empty routes."""
        config_data = {
            "routes": {},
            "default": {
                "target": "http://127.0.0.1:3000"
            }
        }
        with pytest.raises(ValidationError):
            ProxyConfig(**config_data) 