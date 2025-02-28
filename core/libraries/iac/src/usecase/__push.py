from repository.git import GIT_HEAD_IDENTIFIER, GitEventType, GitHandler
from scheduling.workflow import WorkflowSubmitHandler
from usecase.__cicd_event import CICDEventUsecase


class PushUsecase(CICDEventUsecase):
    def __init__(
        self,
        git_handler: GitHandler,
        workflow_submit_handler: WorkflowSubmitHandler,
    ) -> None:
        super().__init__(git_handler, workflow_submit_handler)

    def run(self, commit: str) -> None:
        """Run the CICD event usecase for a push event.

        Args:
            commit: the push commit to get changes from
        """
        try:
            start_commit = self.__git_handler.get_previous_push(GIT_HEAD_IDENTIFIER)
        except Exception as e:
            raise Exception("Couldn't get the start commit from the push event") from e

        super().run(start_commit, commit, GitEventType.PUSH)
