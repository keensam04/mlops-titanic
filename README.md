# mlops-titanic
A demo of basic ML Ops using titanic dataset

## Setup
### Python
The code in the repo has been written in python and tested with v3.10. Follow the instructions [here](https://docs.python.org/3.10/using/index.html) to setup python in the local machine. If you already have another version of python installed, it is recommended to use [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#usage) to manage different python versions.

### kfp sdk
Kubeflow Pipelines is a platform for building and deploying portable, scalable machine learning workflows based on Docker containers within the Kubeflow project.
In order to ensure a fresh environment, create a new virtual environment using the following command. Run the command in the project root
```bash
python3.10 -m venv .venv
```
```bash
source .venv/bin/activate
```
```bash
pip install -r pipeline/requirements.txt
```
This should enable the `dsl-compile` command. Run the following command to validate
```bash
dsl-compile --help
```

### Rancher Desktop
Rancher Desktop is an open-source application that provides all the essentials to work with containers and Kubernetes on the desktop. More details [here](https://rancherdesktop.io/). It is an alternative to Docker Desktop which is proprietary.

Install the v1.16.0 of Rancher Desktop application using the appropriate OS specific installers from [here](https://github.com/rancher-sandbox/rancher-desktop/releases/tag/v1.16.0)

Refer to the below screenshot for first-time configuration.
- Enable Kubernetes (use the latest stable version).
- Use the `dockerd (moby)` container engine which comes with docker cli.
- Opt for automatic path configuration
  
  <img width="408" alt="rancher_local_conf" src="https://github.com/user-attachments/assets/8f8fa3dc-be22-421d-92e1-31a2eef0d7c1" />

#### Validation
Validate that the installation is successful by testing the following commands
```bash
docker --version
```
```bash
docker-compose --version
```
```bash
kubectl version
```

### Argo Workflows
Argo is an open-source project created by Intuit. It is a collection of open source tools for Kubernetes to run workflows, manage clusters, and do GitOps right. Learn more [here](https://argoproj.github.io/)

Argo workflows is the container-native workflow engine for orchestrating parallel jobs on Kubernetes. Learn more [here](https://argo-workflows.readthedocs.io/en/latest/).

Install argo workflow using the below instructions. Refer to the [installation section on quick-start page](https://argo-workflows.readthedocs.io/en/latest/quick-start/#install-argo-workflows) for more details.

1. Use the following argo workflow version to spin up the workflow cluster
   ```bash
   ARGO_WORKFLOWS_VERSION="v3.6.2"
   ```
2. Apply the quick start manifest
   ```bash
   kubectl create namespace argo
   ```
   ```bash
   kubectl -n argo create sa pipeline-runner
   ```
   ```bash
   kubectl create clusterrolebinding pipelinerunnerbinding --clusterrole=cluster-admin --serviceaccount=argo:pipeline-runner
   ```
   ```bash
   kubectl apply -n argo -f "https://github.com/argoproj/argo-workflows/releases/download/${ARGO_WORKFLOWS_VERSION}/quick-start-minimal.yaml"
   ```
3. Configure port forwarding to access the UI:
   ```bash
   kubectl -n argo port-forward service/argo-server 2746:2746
   ```
4. Open the link in browser (Note that it's `https` not *~http~*)
   - https://localhost:2746.

## Run
1. Run the build script
   ```bash
   ./build.sh
   ```
2. Navigate to [argo workflows](https://localhost:2746) in browser and submit the pipeline
   
   - Click on `+ SUBMIT NEW WORKFLOW` button in the top left corner of the screen
   - Select the `Edit using full workflow options`
   - Upload the pipeline manifest file using the `UPLOAD FILE` button
     
     - Navigate to the project folder and select `pipeline.yaml` file
   - Click on `+ CREATE` button 
   
3. Run the inference server
   ```bash
   docker run -p 8090:8090 mlops-titanic/inference:1.0 --bucket mybucket --model-path model.json
   ```
4. Test the inference endpoint
   ```bash
   curl --location 'http://localhost:8090/predict' \
   --header 'Content-Type: application/json' \
   --data '{
     "PassengerId": 892,
     "Name": "Kelly, Mr. James",
     "Pclass": 3,
     "Age": 34.5,
     "SibSp": 0,
     "Parch": 0,
     "Fare": 7.8292,
     "Sex": "male",
     "Embarked": "Q"
   }'
   ```
