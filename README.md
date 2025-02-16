# mlops-titanic
A demo of basic ML Ops using Titanic dataset

## Setup

### Python
The code in the repo has been written in python and tested with v3.10. Follow the instructions [here](https://docs.python.org/3.10/using/index.html) to setup python in the local machine. If you already have another version of python installed, it is recommended to use [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#usage) to manage different python versions.

### kfp sdk
[Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/legacy-v1/introduction/) is a platform for building and deploying portable, scalable machine learning workflows based on Docker containers within the Kubeflow project.
In order to ensure a fresh environment, create a new virtual environment using the following command. Run the command in the project root
```bash
python3.10 -m venv .venv
```
Let's activate the environment that we just created. 

For Mac or Linux,
```bash
source .venv/bin/activate
```
For Windows,
```bash
.\.venv\Scripts\activate
```
Let's install the required packages through the following command
```bash
pip install -r pipeline/requirements.txt
```

The above should enable the `dsl-compile` command. Run the following command to validate
```bash
dsl-compile --help
```

### Rancher Desktop
Rancher Desktop is an open-source application that provides all the essentials to work with containers and Kubernetes on the desktop. More details [here](https://rancherdesktop.io/). It is an alternative to Docker Desktop which is proprietary.

Install the v1.16.0 of Rancher Desktop application using the appropriate OS specific installers. Check the requirement and installation steps for your OS [here](https://docs.rancherdesktop.io/1.16/getting-started/installation).

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
Argo is an open-source project created by **Intuit**. It is a collection of open source tools for Kubernetes to run workflows, manage clusters, and do GitOps right. Learn more [here](https://argoproj.github.io/)

Argo workflows is the container-native workflow engine for orchestrating parallel jobs on Kubernetes. Learn more [here](https://argo-workflows.readthedocs.io/en/latest/).

Install argo workflow using the below instructions. Refer to the [installation section on quick-start page](https://argo-workflows.readthedocs.io/en/latest/quick-start/#install-argo-workflows) for more details.

1. Use the following argo workflow version to spin up the workflow cluster

   For Mac or Linux,
   ```bash
   ARGO_WORKFLOWS_VERSION="v3.6.2"
   ```
   For Windows,
    ```bash
   $ARGO_WORKFLOWS_VERSION="v3.6.2"
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

## How to run this repo?

The below assumes that we're in the base directory of the repo after git cloning
- `docker-compose up -d`
  - This command will use `docker-compose.yml` to bring up [localstack](https://github.com/localstack/localstack) and [MLFlow server](https://mlflow.org/docs/latest/tracking/server.html) 
  - What is LocalStack? 
    - With LocalStack, you can run your AWS applications or S3 (in our case) entirely on your local machine without connecting to a remote cloud provider!
  - What is MLFlow?
    - MLFlow tracking server is a stand-alone HTTP server that serves multiple REST API endpoints for tracking runs/experiments.

- In a separate terminal session, we next run the build script
   - This will build the docker images for each component in the sample pipeline
   - It also creates the pipeline.yaml file
  
  For Mac or linux,
  ```bash
  sh build.sh
  ```
  For Windows,
  ```bash
  ./build.bat
  ```

- Navigate to [Argo Workflows](https://localhost:2746) in browser and submit the pipeline
   - Click on `SUBMIT NEW WORKFLOW` button in the top left corner of the screen
   - Select the `Edit using full workflow options`
   - Upload the pipeline manifest file using the `UPLOAD FILE` button
     - Navigate to the project folder and select `pipeline.yaml` file generate in the prior step
   - Click on `+ CREATE` button 
   - Wait for teh workflow to complete its execution

- Run the inference server
  - ```bash
     docker run -p 8090:8090 mlops-titanic/inference:1.0 --bucket mybucket --model-path model.json
     ```

- Test the inference endpoint
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
