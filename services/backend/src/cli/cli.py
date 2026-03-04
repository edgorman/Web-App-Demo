"""CLI module for the backend service."""
import click
from src.config.service import ServiceConfig
from src.service.fastapi.api import FastAPIService


@click.group()
def cli():
    """Backend service CLI."""
    pass


@cli.command()
def run():
    """Run the backend service."""
    config = ServiceConfig()
    service = FastAPIService(config.fastapi)
    service.run()


if __name__ == "__main__":
    cli()
