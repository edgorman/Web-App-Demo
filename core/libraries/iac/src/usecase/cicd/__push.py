from repository.git import GitEventType, GitHandler
from scheduling.workflow import WorkflowSubmitHandler

from .__event import CICDEventUsecase


class PushUsecase(CICDEventUsecase):
    def __init__(
        self,
        git_handler: GitHandler,
        workflow_submit_handler: WorkflowSubmitHandler,
    ) -> None:
        super().__init__(git_handler, workflow_submit_handler)

    def run(self, commit: str, branch: str) -> None:
        """Run the CICD event usecase for a push event.

        Args:
            commit: the push commit to get changes from
            branch: the branch the push was made to
        """
        try:
            start_commit = self._git_handler.get_previous_push_commit(commit, branch)
        except Exception as e:
            raise Exception(f"Couldn't get the start commit from push event: {str(e)}")

        super().run(start_commit, commit, GitEventType.PUSH)
