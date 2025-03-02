import click

from cli.context import global_options
from cli.types import PositiveNumberParamType
from usecase import new_pull_request_usecase


@click.command()
@global_options
@click.argument("number", required=True, type=PositiveNumberParamType())
@click.pass_context
def pull_request(ctx: dict, verbose: bool, number: int) -> None:
    """Process a pull-request (e.g. 3) as an event from the Git repository."""
    try:
        usecase = new_pull_request_usecase(ctx.obj)
        usecase.run(number)
    except Exception as e:
        raise click.ClickException(e)
