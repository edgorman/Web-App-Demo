import click
from semver import Version

from cli.__context import global_options
from cli.__types import SemanticVersionParamType
from usecase import new_release_usecase


@click.command()
@global_options
@click.argument("release", required=True, type=SemanticVersionParamType())
@click.pass_context
def release(ctx: dict, verbose: bool, release: Version) -> None:
    """Process a release (e.g. 0.1.0) as an event from the Git repository."""
    try:
        usecase = new_release_usecase(ctx.obj)
        usecase.run(release)
    except Exception as e:
        raise click.ClickException(e)
