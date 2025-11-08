import os

ENVIRONMENT_VARIABLES = {"GITHUB_REPOSITORY_URL": "url"}


def pytest_configure(config):
    os.environ.update(ENVIRONMENT_VARIABLES)


def pytest_unconfigure(config):
    for variable in ENVIRONMENT_VARIABLES.keys():
        del os.environ[variable]
