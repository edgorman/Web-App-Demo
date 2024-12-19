terraform {
  cloud {
    # hostname = <-- filled in via env variable `TF_CLOUD_HOSTNAME`
    # organiszation = <-- filled in via env variable `TF_CLOUD_ORGANIZATION`
    workspaces {
      # workspace = <-- filled in via env variable `TF_WORKSPACE`
      # project = <-- filled in via env variable `TF_CLOUD_PROJECT`
    }
  }
}
