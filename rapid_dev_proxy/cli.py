"""Command line interface for Rapid Dev Proxy."""

import logging
import sys
from pathlib import Path
from typing import Optional

import click
import uvicorn
from rich.console import Console
from rich.table import Table

try:
    from .config_manager import ConfigManager
    from .proxy_server import ProxyServer
except ImportError:
    # For PyInstaller packaged executable
    from rapid_dev_proxy.config_manager import ConfigManager
    from rapid_dev_proxy.proxy_server import ProxyServer

console = Console()


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Rapid Dev Proxy - A high-performance reverse proxy for local development."""
    pass


@main.command()
@click.option("--config", "-c", default="config.json", help="Configuration file path")
@click.option("--host", "-h", help="Override bind host")
@click.option("--port", "-p", type=int, help="Override bind port")
@click.option("--reload", is_flag=True, help="Enable auto-reload on config changes")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def start(config: str, host: Optional[str], port: Optional[int], reload: bool, debug: bool):
    """Start the proxy server."""
    try:
        setup_logging("DEBUG" if debug else "INFO")
        
        # Load configuration
        config_manager = ConfigManager(config)
        config_manager.load_config()
        
        # Override host/port if specified
        if host:
            config_manager.config.proxy.host = host
        if port:
            config_manager.config.proxy.port = port
        
        # Create proxy server
        proxy_server = ProxyServer(config_manager)
        
        console.print(f"[green]Starting Rapid Dev Proxy on {config_manager.config.proxy.host}:{config_manager.config.proxy.port}[/green]")
        console.print(f"[blue]Configuration file: {config}[/blue]")
        console.print(f"[blue]Loaded {len(config_manager.config.routes)} routes[/blue]")
        
        # Start server
        uvicorn.run(
            proxy_server.get_app(),
            host=config_manager.config.proxy.host,
            port=config_manager.config.proxy.port,
            reload=reload,
            log_level="debug" if debug else "info"
        )
        
    except Exception as e:
        console.print(f"[red]Error starting proxy: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option("--config", "-c", default="config.json", help="Configuration file path")
def validate(config: str):
    """Validate configuration file."""
    try:
        setup_logging("INFO")
        
        config_manager = ConfigManager(config)
        config_manager.load_config()
        
        if config_manager.validate_config():
            console.print("[green]✓ Configuration is valid[/green]")
            
            # Display routes
            table = Table(title="Configured Routes")
            table.add_column("Domain", style="cyan")
            table.add_column("Target", style="green")
            table.add_column("Description", style="yellow")
            
            for domain, route in config_manager.config.routes.items():
                description = route.metadata.get("description", "")
                table.add_row(domain, route.target, description)
            
            console.print(table)
            
        else:
            console.print("[red]✗ Configuration validation failed[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error validating configuration: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option("--output", "-o", default="config.json", help="Output file path")
def init(output: str):
    """Create a sample configuration file."""
    try:
        config_manager = ConfigManager()
        config_manager.create_sample_config(output)
        
        console.print(f"[green]✓ Sample configuration created: {output}[/green]")
        console.print("[blue]Edit the configuration file to add your routes and start the proxy with:[/blue]")
        console.print(f"[yellow]rapid-dev-proxy start -c {output}[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error creating sample configuration: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option("--config", "-c", default="config.json", help="Configuration file path")
def routes(config: str):
    """List all configured routes."""
    try:
        setup_logging("INFO")
        
        config_manager = ConfigManager(config)
        config_manager.load_config()
        
        table = Table(title="Configured Routes")
        table.add_column("Domain", style="cyan")
        table.add_column("Target", style="green")
        table.add_column("Description", style="yellow")
        
        for domain, route in config_manager.config.routes.items():
            description = route.metadata.get("description", "")
            table.add_row(domain, route.target, description)
        
        console.print(table)
        console.print(f"[blue]Default route: {config_manager.config.default.target}[/blue]")
        
    except Exception as e:
        console.print(f"[red]Error listing routes: {e}[/red]")
        sys.exit(1)


@main.command()
def version():
    """Show version information."""
    console.print("[green]Rapid Dev Proxy v0.1.0[/green]")
    console.print("[blue]A high-performance reverse proxy for local development[/blue]")


if __name__ == "__main__":
    main() 