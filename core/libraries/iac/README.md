# iac

Infrastructure as code library for the Web App Demo.

## Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you haven't already.

Then create your virtual environment by running:

```bash
make init-extras
```

## Usage

To run the cli manually, run:

```bash
iac --help
```

This will display a useful help message for each command group.

## Contribute

In general you should follow the [contributing guide](../../../docs/CONTRIBUTING.md) at the root of this repository - this section is for specific instructions in this subdirectory.

### Testing

```bash
make test
```

### Linting

```bash
make lint
```

### Packages

To add core packages (i.e. those required to run the library), run:

```bash
uv add <package>
```

To remove a package, run:

```bash
uv remove <package>
```

To add a package to a group (e.g. lint/test), run:

```bash
uv add <package> --optional <group>

# e.g. adding pytest to the optional dependency group "test"
uv add pytest --optional test
```
