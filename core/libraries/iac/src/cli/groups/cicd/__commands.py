import click

from config.cli import set_verbose
from usecase import new_pull_request_usecase, new_push_usecase, new_release_usecase


@click.command()
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose output.",
    expose_value=False,
    callback=set_verbose,
)
@click.pass_context
def pull_request(ctx: dict) -> None:
    """Process a pull request event from a Git repository."""
    try:
        usecase = new_pull_request_usecase()
        usecase.run()
    except Exception as e:
        click.Abort(e)


@click.command()
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose output.",
    expose_value=False,
    callback=set_verbose,
)
@click.pass_context
def push(ctx: dict) -> None:
    """Process a push event from a Git repository."""
    try:
        usecase = new_push_usecase()
        usecase.run()
    except Exception as e:
        click.Abort(e)


@click.command()
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose output.",
    expose_value=False,
    callback=set_verbose,
)
@click.pass_context
def release(ctx: dict) -> None:
    """Process a release event from a Git repository."""
    try:
        usecase = new_release_usecase()
        usecase.run()
    except Exception as e:
        click.Abort(e)
