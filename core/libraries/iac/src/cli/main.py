import click
from pydantic import BaseModel, ValidationError

from usecase import new_pull_request_usecase, new_push_usecase, new_release_usecase


class GitContext(BaseModel):
    actor: str
    commit: str
    domain: str
    owner: str
    repository: str


class Context(BaseModel):
    verbose: bool
    gitContext: GitContext


@click.group()
@click.option("--verbose", help="Enable verbose output.", is_flag=True)
@click.option("--git-actor", help="The name of the user running the cli.")
@click.option("--git-commit", help="The commit for the event.")
@click.option("--git-domain", help="The domain of the git repository.")
@click.option("--git-owner", help="The name of the git owner.")
@click.option("--git-repository", help="The name of the git repository.")
@click.pass_context
def cli(
    ctx: dict,
    verbose: bool,
    git_actor: str,
    git_commit: str,
    git_domain: str,
    git_owner: str,
    git_repository: str,
) -> None:
    """The main entry point for running the iac library."""
    try:
        ctx.obj = Context(
            verbose=verbose,
            gitContext=GitContext(
                actor=git_actor,
                commit=git_commit,
                domain=git_domain,
                owner=git_owner,
                repository=git_repository,
            ),
        )
    except ValidationError as ve:
        raise click.MissingParameter(str(ve), ctx)


@click.pass_context
@cli.command()
def pull_request() -> None:
    """Process a pull request event from a Git repository."""
    try:
        usecase = new_pull_request_usecase()
    except Exception as e:
        click.Abort(e)

    try:
        usecase.run()
    except Exception as e:
        click.Abort(e)


@click.pass_context
@cli.command()
def push() -> None:
    """Process a push event from a Git repository."""
    try:
        usecase = new_push_usecase()
    except Exception as e:
        click.Abort(e)

    try:
        usecase.run()
    except Exception as e:
        click.Abort(e)


@click.pass_context
@cli.command()
def release() -> None:
    """Process a release event from a Git repository."""
    try:
        usecase = new_release_usecase()
    except Exception as e:
        click.Abort(e)

    try:
        usecase.run()
    except Exception as e:
        click.Abort(e)


if __name__ == "__main__":
    cli()
