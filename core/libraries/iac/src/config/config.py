from decouple import config


class GitHubGitHandlerConfig:
    ACCESS_TOKEN = config("GITHUB_ACCESS_TOKEN")


class K8sWorkflowSubmitHandlerConfig:
    SERVICE_ACCOUNT_KEY = config("K8S_SERVICE_ACCOUNT_KEY")
