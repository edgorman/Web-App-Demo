import click

from cli.__context import global_options
from cli.__types import SHA1ParamType
from usecase import new_push_usecase


@click.command()
@global_options
@click.argument("commit", required=True, type=SHA1ParamType())
@click.argument("branch", required=True, type=str)
@click.pass_context
def push(ctx: dict, verbose: bool, commit: str, branch: str) -> None:
    """Process a push commit (e.g. abcd123) as an event from the Git repository."""
    try:
        usecase = new_push_usecase(ctx.obj)
        usecase.run(commit, branch)
    except Exception as e:
        raise click.ClickException(e)
