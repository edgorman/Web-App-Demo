from repository.git import GitEventType, GitHandler
from scheduling.workflow import WorkflowSubmitHandler

from .__event import CICDEventUsecase


class ReleaseUsecase(CICDEventUsecase):
    def __init__(
        self,
        git_handler: GitHandler,
        workflow_submit_handler: WorkflowSubmitHandler,
    ) -> None:
        super().__init__(git_handler, workflow_submit_handler)

    def run(self, version: str) -> None:
        """Run the CICD event usecase for a release event.

        Args:
            version: the release version to get changes from
        """
        try:
            start_commit = self._git_handler.get_previous_release_commit(version)
        except Exception as e:
            raise Exception(f"Could not get the previous commit from release event: {str(e)}")

        super().run(start_commit, version, GitEventType.RELEASE)
