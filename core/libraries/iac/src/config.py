from decouple import config


class GitHubGitHandlerConfig:
    GITHUB_REPOSITORY_URL = config("GITHUB_REPOSITORY_URL")


class K8sWorkflowSubmitHandlerConfig:
    SERVICE_ACCOUNT_KEY = config("K8S_SERVICE_ACCOUNT_KEY")
