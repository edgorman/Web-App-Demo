import functools

import click


class Context:
    def __init__(self) -> None:
        self.verbose = False

    def set_verbose(self) -> None:
        self.verbose = True


def global_options(func):
    @click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ctx = click.get_current_context()
        if ctx.obj is None:
            ctx.obj = Context()
        if kwargs["verbose"]:
            ctx.obj.set_verbose()
        return func(*args, **kwargs)

    return wrapper
