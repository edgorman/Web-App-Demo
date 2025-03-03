import re

import click
from semver import Version


class PositiveNumberParamType(click.ParamType):
    name = "positive_number"

    def convert(self, value, param, ctx):
        try:
            value = int(value)
        except Exception:
            self.fail(f"Must be a number, got {value!r}.", param, ctx)

        if value <= 0:
            self.fail(f"Must be a positive non-zero number, got {value!r}.", param, ctx)

        return value


class SemanticVersionParamType(click.ParamType):
    name = "semantic_version"

    def convert(self, value, param, ctx):
        try:
            value = Version.parse(value)
        except Exception:
            self.fail(f"Must be a valid semantic version, got {value!r}.", param, ctx)

        return value


class SHA1ParamType(click.ParamType):
    name = "sha1"

    def convert(self, value, param, ctx):
        if not bool(re.fullmatch(r"[0-9a-f]{5,40}", value)):
            self.fail(f"Must be a valid SHA1, got {value!r}.", param, ctx)

        return value
