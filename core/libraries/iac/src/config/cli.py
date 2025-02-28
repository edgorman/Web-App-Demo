import click


class Context:
    def __init__(self):
        self.verbose = False
        self.commit = None


pass_context = click.make_pass_decorator(Context, ensure=True)


def set_verbose(ctx, _, value):
    if value:
        ctx.ensure_object(Context).verbose = True
