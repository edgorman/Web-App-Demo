from repository.git import GitEventType, GitHandler
from scheduling.workflow import WorkflowSubmitHandler


class CICDEventUsecase:
    def __init__(
        self,
        git_handler: GitHandler,
        workflow_submit_handler: WorkflowSubmitHandler,
    ) -> None:
        """Initialise the CICD event usecase.

        Args:
            git_handler: The git repository handler
            workflow_submit_handler: The workflow submit handler
        """
        self.__git_handler = git_handler
        self.__workflow_submit_handler = workflow_submit_handler

    def run(self, start_commit: str, end_commit: str, event_type: GitEventType) -> None:
        """Get a list of changes between commits and trigger the relevant CICD workflows.

        Args:
            start_commit: the start commit to get changes from
            end_commit: the end commit to get changes until
            event_type: the type of CICD event to process
        """
        # Generate a list of files changed between commits
        try:
            files_changed = self.__git_handler.get_files_changed(
                start_commit, end_commit
            )
        except Exception as e:
            raise Exception(
                "Error occurred while getting files changed between commits"
            ) from e

        # Generate a set of files from the parent cicd folder to submit
        cicd_files = set()
        get_file_exceptions = []
        for file_changed in files_changed:
            try:
                cicd_files = self.__git_handler.get_cicd_files(file_changed, event_type)
                cicd_files.update(cicd_files)
            except Exception as e:
                get_file_exceptions.append(e)

        # Then, handle any exceptions when getting changed files
        if len(get_file_exceptions) > 0:
            raise ExceptionGroup(
                "Error(s) occurred while getting the parent cicd from changed files",
                get_file_exceptions,
            )

        # Submit each cicd file (even if a single submission fails)
        submit_workflow_exceptions = []
        for cicd_file in cicd_files:
            try:
                self.__workflow_submit_handler.submit(cicd_file)
            except Exception as e:
                submit_workflow_exceptions.append(e)

        # Finally, handle any exceptions when submitting workflows
        if len(submit_workflow_exceptions) > 0:
            raise ExceptionGroup(
                "Error(s) occurred while submitting workflows from parent cicd",
                submit_workflow_exceptions,
            )
