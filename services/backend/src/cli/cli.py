"""CLI module for the backend service."""
import click
from src.config.service import ServiceConfig
from src.service.fastapi.api import FastAPIService


@click.group()
def cli():
    """Backend service CLI."""
    pass


@cli.command()
@click.option("--host", default=None, help="Host to bind to")
@click.option("--port", default=None, type=int, help="Port to bind to")
@click.option("--reload", is_flag=True, default=None, help="Enable auto-reload")
def run(host, port, reload):
    """Run the backend service."""
    config = ServiceConfig()
    service = FastAPIService(config)
    service.run(host=host, port=port, reload=reload)


if __name__ == "__main__":
    cli()
