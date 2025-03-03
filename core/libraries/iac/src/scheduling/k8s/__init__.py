from config import K8sWorkflowSubmitHandlerConfig

from .__workflow import K8sWorkflowSubmitHandler


def new_k8s_workflow_submit_handler(
    config: K8sWorkflowSubmitHandlerConfig,
) -> K8sWorkflowSubmitHandler:
    return K8sWorkflowSubmitHandler(config)
