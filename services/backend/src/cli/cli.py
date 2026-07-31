"""CLI module for the backend service."""
import click
from google.cloud.firestore import Client as FirestoreClient
from src.config.service import ServiceConfig
from src.service.fastapi.api import FastAPIService
from src.storage.firestore.user import FirestoreUserStorage


@click.group()
def cli():
    """Backend service CLI."""
    pass


@cli.command()
def run():
    """Run the backend service."""
    config = ServiceConfig()

    firestore_client = FirestoreClient(
        project=config.storage.firestore.project_id or None,
        database=config.storage.firestore.database,
    )
    user_storage = FirestoreUserStorage(client=firestore_client)

    service = FastAPIService(config, user_storage)
    service.run()


if __name__ == "__main__":
    cli()
