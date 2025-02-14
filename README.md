# mlops-titanic
A demo of basic ML Ops using titanic dataset

## Setup

### Install Rancher Desktop
Rancher Desktop is an open-source application that provides all the essentials to work with containers and Kubernetes on the desktop. More details [here](https://rancherdesktop.io/). It is an alternative to Docker Desktop which is proprietary.

Install the v1.16.0 of Rancher Desktop application using the appropriate OS specific installers from [here](https://github.com/rancher-sandbox/rancher-desktop/releases/tag/v1.16.0)

Refer to the below screenshot for first-time configuration.
- Enable Kubernetes (use the latest stable version).
- Use the `dockerd (moby)` container engine which comes with docker cli.
- Opt for automatic path configuration
<img width="408" alt="rancher_local_conf" src="https://github.com/user-attachments/assets/8f8fa3dc-be22-421d-92e1-31a2eef0d7c1" />
   
### Argo Workflows
Argo is an open-source project created by Intuit. It is a collection of open source tools for Kubernetes to run workflows, manage clusters, and do GitOps right. Learn more [here](https://argoproj.github.io/)

Argo workflows is the container-native workflow engine for orchestrating parallel jobs on Kubernetes. Learn more [here](https://argo-workflows.readthedocs.io/en/latest/).

Install argo workflow using the below instructions. Refer to the [installation section on quick-start page](https://argo-workflows.readthedocs.io/en/latest/quick-start/#install-argo-workflows) for more details.

1. Use the following argo workflow version to spin up the workflow cluster
   ```
   ARGO_WORKFLOWS_VERSION="v3.6.2"
   ```
2. Apply the quick start manifest
   ```
   kubectl create namespace argo
   kubectl apply -n argo -f "https://github.com/argoproj/argo-workflows/releases/download/${ARGO_WORKFLOWS_VERSION}/quick-start-minimal.yaml"
   ```
3. Configure port forwarding to access the UI:
   ```
   kubectl -n argo port-forward service/argo-server 2746:2746
   ```
4. Open the link in browser (Note that it's `https` not *~http~*)
   - https://localhost:2746.
