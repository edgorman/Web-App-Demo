import click

from cli.__commands.cicd import cicd
from cli.__context import global_options


@click.group()
@global_options
@click.pass_context
def cli(ctx: dict, verbose: bool) -> None:
    """The main entry point for running the iac library."""


# Add commands/groups of commands here
cli.add_command(cicd)


if __name__ == "__main__":
    cli()
