import click

from cli.groups.cicd import cicd
from config.cli import Context, set_verbose


@click.group()
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose output.",
    expose_value=False,
    callback=set_verbose,
)
@click.pass_context
def cli(ctx: dict) -> None:
    """The main entry point for running the iac library."""
    ctx.obj = Context()


# Add commands/groups of commands here
cli.add_command(cicd)


if __name__ == "__main__":
    cli()
