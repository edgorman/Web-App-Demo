# First Time Project Setup

<details style="padding-bottom: 10px;">
<summary>Metadata</summary>
<table style="width: 100%;">
<tr><th>Field</th><th>Value</th></tr>
<tr><td>Owner</td><td><a href="https://github.com/edgorman">edgorman</a></td></tr>
<tr><td>Date Created</td><td>2024-12-14</td></tr>
<tr><td>Last Updated</td><td>2024-12-14</td></tr>
</table>
</details>

This guide serves as notes while setting up the repository and connected services to implement fully-automated infrastructure as code (IAC) for the first time.

## Requirements

1. Setup your developer environment by following [this guide](./0001-developer-environment-setup.md).

## Instructions

### GitHub

1. Create your repo, if you haven't already.

2. Create a `main` and `develop` branch.

3. Add branch protection rules to GitHub to protect `main` and `develop`.

### Google Cloud Platform

1. With your google account, create a dev and prod GCP project [here](https://console.cloud.google.com/projectcreate).

2. For each dev and prod project, setup the env variable and configure the :

    ```bash
    gcloud config set project your-project-name
    ```

3. Enable the following APIs (note, these can take a while to apply):

    ```bash
    gcloud services enable \
      cloudresourcemanager.googleapis.com \
      iam.googleapis.com \
      compute.googleapis.com \
      container.googleapis.com
    ```

3. Create a service account for executing Terraform configuration:

    ```bash
    gcloud iam service-accounts create terraform-executor \
      --project $(gcloud config get project) \
      --display-name="Terraform Executor"
    ```

4. Grant the service account permissions to provision:

    ```bash
    gcloud projects add-iam-policy-binding $(gcloud config get project) \
      --member="serviceAccount:terraform-executor@$(gcloud config get project).iam.gserviceaccount.com" \
      --role="roles/container.admin"
    ```

5. Create and download the key file for the new service account:

    ```bash
    gcloud iam service-accounts keys create terraform-executor-$(gcloud config get project).key \
      --iam-account="terraform-executor@$(gcloud config get project).iam.gserviceaccount.com"
    ```

### Terraform Cloud

1. Create an account [here](https://app.terraform.io/app/organizations).

2. Create an organization [here](https://app.terraform.io/app/organizations/new).

3. Create a project under your new organization.

4. Create a dev and prod workspace under the project, selecting the "API" driven option for each.

5. Add the following variables to each workspace:

    > | Key | Value | Category | HCL | Sensitive |
    > | --- | ----- | -------- | --- | --------- |
    > | environment | develop/production | terraform | false | false
    > | gcp_project_name | your-project-name | terraform | false | true
    > | gcp_project_region | your-project-region | terraform | false | true
    > | gcp_project_zone | your-project-zone | terraform | false | true
    > | GOOGLE_CREDENTIALS | cat terraform-executor-$(gcloud config get project).key \| tr -d "\n" | environment | false | true

6. Login into your cloud account by running the following:

    ```bash
    terraform login
    ```

7. After creating a token during the last step, save it locally:

    ```bash
    echo your-key-here >> terraform-cloud.key
    ```

### Initialise Terraform

1. Change to the terraform subdirectory:

    ```
    cd core/terraform
    ```

2. Create the following environment variables in your terminal:

    ```
    export TF_CLOUD_HOSTNAME=app.terraform.io
    export TF_CLOUD_ORGANIZATION=web-app-demo
    export TF_CLOUD_PROJECT=web-app-demo
    export TF_WORKSPACE=dev
    ```

3. Initialise and plan the Terraform configuration by running:

    ```
    terraform init
    terraform plan
    ```
  
4. If there are no errors, you may apply the configuration:

    ```
    terraform apply
    ```

### ArgoCD 

1. setup the argocd server

### CICD

1. create cicd workflows

### Webhooks

1. trigger cicd workflows from github

### Pull-Request

1. 

cicd will use dev.tfvars for dev deployment and prod.tfvars for prod deployment
can use multiple tf vars per domain?
