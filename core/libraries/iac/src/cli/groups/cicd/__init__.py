import click

from cli.__context import global_options

from .__pull_request import pull_request
from .__push import push
from .__release import release


@click.group()
@global_options
@click.pass_context
def cicd(ctx: dict, verbose: bool) -> None:
    """The group of commands related to CICD events."""


# Add subcommands here
cicd.add_command(pull_request)
cicd.add_command(push)
cicd.add_command(release)
