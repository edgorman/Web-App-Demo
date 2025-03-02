from cli.__context import Context
from config.config import GitHubGitHandlerConfig, K8sWorkflowSubmitHandlerConfig
from repository.git import GitHandler
from repository.github import new_github_git_handler
from scheduling.k8s import new_k8s_workflow_submit_handler
from scheduling.workflow import WorkflowSubmitHandler

from .__pull_request import PullRequestUsecase
from .__push import PushUsecase
from .__release import ReleaseUsecase


def __init_handlers() -> tuple[GitHandler, WorkflowSubmitHandler]:
    git_handler = new_github_git_handler(GitHubGitHandlerConfig())
    workflow_submit_handler = new_k8s_workflow_submit_handler(K8sWorkflowSubmitHandlerConfig())

    return git_handler, workflow_submit_handler


def new_pull_request_usecase(ctx: Context) -> PullRequestUsecase:
    try:
        git_handler, workflow_submit_handler = __init_handlers()
    except Exception as e:
        raise Exception("Error initialising handlers for pull request usecase") from e

    return PullRequestUsecase(git_handler, workflow_submit_handler)


def new_push_usecase(ctx: Context) -> PushUsecase:
    try:
        git_handler, workflow_submit_handler = __init_handlers()
    except Exception as e:
        raise Exception("Error initialising handlers for push usecase") from e

    return PushUsecase(git_handler, workflow_submit_handler)


def new_release_usecase(ctx: Context) -> ReleaseUsecase:
    try:
        git_handler, workflow_submit_handler = __init_handlers()
    except Exception as e:
        raise Exception("Error initialising handlers for release usecase") from e

    return ReleaseUsecase(git_handler, workflow_submit_handler)
