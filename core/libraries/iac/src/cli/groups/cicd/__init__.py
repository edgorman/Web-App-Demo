import click

from config.cli import set_verbose

from .__commands import pull_request, push, release


@click.group()
@click.argument("commit", required=True)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose output.",
    expose_value=False,
    callback=set_verbose,
)
@click.pass_context
def cicd(ctx: dict, commit: str) -> None:
    ctx.obj.commit = commit


# Add subcommands here
cicd.add_command(pull_request)
cicd.add_command(push)
cicd.add_command(release)
