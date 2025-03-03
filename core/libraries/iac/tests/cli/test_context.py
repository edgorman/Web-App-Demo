from contextlib import nullcontext as no_exception

import click
import pytest
from click.testing import CliRunner

from cli.__context import Context, global_options


def test_Context_init():
    with no_exception():
        Context()


def test_Context_set_verbose():
    ctx = Context()
    assert ctx.verbose is False

    ctx.set_verbose()
    assert ctx.verbose is True


@pytest.mark.parametrize(
    "options,expectExitCode,expectMessage",
    [
        ([], 0, "Verbose is False"),
        (["--verbose"], 0, "Verbose is True"),
    ],
)
def test_global_options(options, expectExitCode, expectMessage):
    @click.command()
    @global_options
    def test_command(verbose: bool):
        ctx = click.get_current_context()
        print("Verbose is {}".format(ctx.obj.verbose))

    runner = CliRunner()
    result = runner.invoke(test_command, options)
    assert result.exit_code == expectExitCode
    assert expectMessage in result.output
