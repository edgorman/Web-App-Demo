# Developer Environment Setup

<details style="padding-bottom: 10px;">
<summary>Metadata</summary>
<table style="width: 100%;">
<tr><th>Field</th><th>Value</th></tr>
<tr><td>Owner</td><td><a href="https://github.com/edgorman">edgorman</a></td></tr>
<tr><td>Date Created</td><td>2024-12-14</td></tr>
<tr><td>Last Updated</td><td>2024-12-14</td></tr>
</table>
</details>

If you are a new developer, follow this guide to setup your environment.

## Requirements

<!-- required actions before starting guide -->

## Instructions

1. Install a recent version of Python:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3
```

2. Install gcloud using the [instructions here](https://cloud.google.com/sdk/docs/install).

3. Create your gcloud account at [the console](https://console.cloud.google.com/).

4. Authorize your gcloud account locally:

```bash
gcloud auth application-default login --no-launch-browser
```

5. Install kubectl using gcloud:

```bash
gcloud components install kubectl
```

6. Install Terraform using the [instructions here](https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/install-cli).
