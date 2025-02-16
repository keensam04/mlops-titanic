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

**Mac/Linux**
```bash
source .venv/bin/activate
```
**Windows**
```bat
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

1. Apply the quick start manifest
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
   kubectl apply -n argo -f "https://github.com/argoproj/argo-workflows/releases/download/v3.6.2/quick-start-minimal.yaml"
   ```
2. Configure port forwarding to access the UI:
   ```bash
   kubectl -n argo port-forward service/argo-server 2746:2746
   ```
> [!NOTE]  
> It takes sometime for the `service/argo-server` to get started. The above port-forwarding command will fail until the server is up and running. Wait and retry in sometime in case of pod state shows as `PENDING`
3. Open the link in browser (Note that it's `https` not *~http~*)
   - https://localhost:2746.

## How to run this project?
> [!IMPORTANT]  
> The below assumes that we're in the base directory of the repo after git cloning
- Bring up the [localstack](https://github.com/localstack/localstack) and [MLflow](#mlflow) servers. This command uses `docker-compose.yml`
  ```bash
  docker-compose up -d
  ```
> [!NOTE]
> With LocalStack, you can run your AWS services (Amazon S3 in our case) entirely on your local machine without connecting to a remote cloud provider!

- In a separate terminal session, we next run the build script
  - This will build the docker images for each component in the sample pipeline
  - It also creates the pipeline.yaml file
  
  **Mac/Linux**
  ```bash
  sh build.sh
  ```
  **Windows**
  ```bat
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
  ```bash
  docker run -v ./beacon:/var/beacon -p 8090:8090 mlops-titanic/inference:1.0 --bucket mybucket --model-path model.json
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

## Key concepts
### Docker
Let’s simplify Docker by comparing it to a concept you might already be familiar with—apps on your phone!

Imagine you have several different apps on your phone: games, social media, and photo editors. Each of these apps runs in its own separate space and doesn't interfere with the others. They come with everything they need to run, such as specific settings, libraries, and code.

Now, picture that you need to run different pieces of software on a computer for a project, but each piece of software needs different settings and dependencies (the libraries and tools it needs to work). Traditionally, setting up each piece of software could be quite complex and time-consuming. Imagine trying to make sure all your apps on your phone work correctly without using the app store and having to manually set up everything they need!

This is where Docker comes in. Docker is like a technology that allows you to package each piece of software, along with everything it needs to run (called "dependencies"), into a "container." Each container is sort of like an app on your phone—it includes everything required, so it runs the same way no matter where you put it. These containers can run on any computer that has Docker installed, just like your apps can run on any phone that has the necessary operating system.

Here's why this is really cool:

**Consistency:** Just like you know an app from the app store will run on any phone, a Docker container ensures the software runs the same way everywhere.
**Isolation:** Each container is separate from the others, so if one has a problem, it doesn’t affect the others—just like one app crashing doesn’t usually crash your whole phone.
**Easy Sharing:** You can share these containers with others easily, ensuring they get the exact same setup and can run the software without any hassle.
So, think of Docker as a way to create neat, organized, and self-contained "boxes" for your software and all its parts. It's a bit like creating apps for a computer, but for any kind of software and without worrying about compatibility issues.

Learn more from [here](https://docs.docker.com/get-started/docker-overview/)

> [!NOTE]
> [Docker Compose](https://docs.docker.com/compose/) is a tool that helps you easily manage and run multi-container Docker applications by defining all your containers and their settings in a single docker-compose.yml file.

### Kubernetes
Docker as explained above is like putting your applications into neat, self-contained "containers" so they can run consistently anywhere. Now, think of Kubernetes as the smart system that manages all those containers when you have lots of them running on many different computers.

Imagine you're in charge of a fleet of robots, each carrying out important tasks. Each robot is a Docker container, prepped with everything it needs to do its job. But when you have hundreds or thousands of robots, it gets really tricky to keep track of them all, make sure they're working properly, fix them when they break, and send more robots to a place if needed.

Kubernetes is like an advanced control center for managing this fleet of robots:
|          | With Docker only | With Kubernetes |
|----------|------------------|-----------------|
| Deployment and Scaling   | You manually start each container. If you need more copies of an application, you start more containers yourself. | You define your desired state (like how many replicas of a container you need) in a configuration file. Kubernetes handles starting those containers and maintaining the desired number, automatically adding more if necessary, just like deploying more robots to a busy area. |
| Self-Healing             | If a container (robot) stops working, you need to notice it and restart it yourself. | It continuously monitors the health of containers. If one fails, it automatically restarts it or replaces it, ensuring everything keeps running smoothly. |
| Load Balancing           | You have to figure out how to distribute incoming traffic to your containers. | It automatically balances the load, making sure that traffic is evenly spread across all instances of your application, preventing overload on any single container. |
| Configuration Management | Managing environment variables and configurations for many containers can get tricky. | You can use ConfigMaps and Secrets to manage configuration details and sensitive information in a scalable and secure way. |
| Updates and Rollbacks    | Updating an application means stopping containers and starting new ones, potentially causing downtime. | It provides tools for rolling updates, meaning you can update applications with zero-downtime. If something goes wrong, Kubernetes can roll back to the previous version automatically. |

In summary, if Docker is like packaging your apps into neat containers, Kubernetes is the sophisticated system that deploys, manages, scales, and maintains those containers across a cluster of machines. It handles all the heavy lifting of ensuring your applications run smoothly and are always available to users.

So, Kubernetes is essentially the best friend of Docker, making containerized applications easy to manage at scale. Learn more [here](https://kubernetes.io/docs/home/).

### Kubeflow
Think of Kubeflow as the specialized version of Kubernetes but designed specifically for managing machine learning (ML) workflows. Let’s break it down step by step.

Building, training, and deploying machine learning models involves a lot of steps and different tools. You usually need to:
1. **Collect and preprocess data:** Making sure your data is ready and suitable for your machine learning model.
2. **Train models:** Running intensive computations to teach your models from data.
3. **Evaluate models:** Testing the model to see how well it performs.
4. **Deploy models:** Making the trained model available for real-world use.
Managing all these steps manually can be complex, especially when you want to ensure scalability, reproducibility, and easy collaboration among team members.

Kubeflow is like a friend to Kubernetes that focuses on making these machine learning workflows more manageable and efficient:
|                        | Kubernetes | Kubeflow |
|------------------------|------------|----------|
| Pipeline Orchestration | Handles general application deployment and scaling. | Specifically orchestrates end-to-end machine learning pipelines, such as data preprocessing, model training, and evaluation. It allows you to define these pipelines using a set of steps that can be automatically executed. |
| Reproducibility        | Ensures that your applications run smoothly but doesn’t specialize in ML-specific setup. | By containerizing every step of the ML pipeline and running them on Kubernetes, you ensure that every experiment is reproducible. Kubeflow makes it easy for anyone to run the same experiment with the same results. |
| Scalability            | Naturally provides scalability for containerized applications. | Utilizes Kubernetes’ scalability to handle large datasets and complex machine learning models, making it easy to scale your ML workflows up or down depending on the workload. |
| Model Serving          | Can serve applications but isn’t designed specifically for serving ML models. | Provides specialized components for serving ML models, allowing you to deploy models and create predictions at scale with efficiency. |
| Hyperparameter Tuning  | You’d have to set up everything manually for hyperparameter tuning. | Includes tools to automate the search for the best parameters for your ML models, making the process much easier. |

Let's put it into a concrete example:
| Without Kubeflow | With Kubeflow |
|------------------|---------------|
| You'd need to set up separate processes for data processing in one container, model training in another, a database to store your results, and a web server to serve your model. You'd manage coordination, scaling, and monitoring all these components manually. | You set up an end-to-end pipeline where data preprocessing, model training, evaluation, and serving are all defined as stages. Kubeflow handles the coordination, running each step, scaling as needed, and providing consistent, reproducible results. |

In a nutshell, Kubeflow makes it easier to deploy, manage, and scale machine learning workflows on Kubernetes. It takes advantage of Kubernetes' strengths in running containerized applications and adds ML-specific components to make the entire process— from data preparation and model training to deployment and serving— more streamlined and manageable.

So, think of Kubeflow as a helpful tool that builds on Kubernetes to make the complex world of machine learning more straightforward and organized! Learn more [here](https://www.kubeflow.org/docs/started/introduction/)

### Argo workflows
Argo Workflows is a powerful tool for automating and managing complex workflows on Kubernetes. It’s versatile and can be used for an array of tasks across different domains. It's like having an upgraded project manager who makes sure every task is done in the right order, efficiently, and reliably.

Key Features of Argo Workflows
1. Workflow Automation:
   - **What:** Automates the execution of a series of tasks in a specific order.
   - **How:** You define these tasks and their order in a file (usually a YAML file). Each task often runs in its own Docker container.
   - **Why:** To ensure tasks run correctly every time without manual intervention.
2. Directed Acyclic Graph (DAG):
   - **What:** Specifies the order of tasks and their dependencies.
   - **How:** Ensures tasks that depend on each other are executed in the right sequence.
   - **Why:** To manage complex workflows where some tasks can run simultaneously, while others need to wait for previous tasks to complete.
3. Parallel Task Execution:
   - **What:** Allows multiple tasks to run at the same time if they don’t depend on each other.
   - **How:** Optimizes efficiency and speeds up workflow execution.
   - **Why:** To save time and resources by making sure all tasks that can run at the same time do so.
4. Error Handling and Retry:
   - **What:** Automatically retries tasks that fail and handles errors.
   - **How:** Makes sure workflows are resilient and less likely to break due to minor issues.
   - **Why:** To provide stability and robustness to your workflows.

#### Similarities Between Kubeflow and Argo Workflows
- **Kubernetes Integration:** Both use Kubernetes to orchestrate and manage containerized tasks.
- **Workflow Management:** Both allow you to define workflows as a series of steps (or tasks) that are executed in a specified order.
- **Scalability:** Both leverage Kubernetes' ability to scale, ensuring workflows can handle varying loads efficiently.
- **Automation:** Both emphasize automating processes to reduce manual interventions.

#### Differences Between Kubeflow and Argo Workflows
|                | Kubeflow | Argo Workflows |
|----------------|----------|----------------|
| Primary Purpose | Built specifically for machine learning (ML) workflows. It includes components tailored for data preprocessing, model training, hyperparameter tuning, evaluation, and serving ML models. | A general-purpose workflow automation tool. It can handle a wide range of tasks beyond ML, including data processing, CI/CD pipelines, and other automation tasks. |
| Specialized Components | Offers ML-specific tools and integrations, such as TensorFlow training operators and serving components. | Provides a generic framework for defining and running any kind of workflow without built-in ML-specific features. |
| Use Cases | Best for end-to-end machine learning projects where you need to preprocess data, train models, evaluate them, and deploy for predictions. | Best for diverse applications, such as automating repetitive tasks, running data processing jobs, managing CI/CD pipelines, and more. |
| User Focus | Primarily targets data scientists and ML engineers who need to manage all the steps in an ML pipeline. | Targets DevOps engineers, data engineers, and developers who need to automate a broad set of tasks. |

### S3
We can understand Amazon S3 by thinking of it as an online, cloud-based extension of the file system on an operating system (OS). Here's how it compares and works:

Comparing File Systems
|           | OS File System | Amazon S3 |
| Folders and Files | You have directories (or folders) and files. Directories contain files and can also contain other directories. | Instead of directories and files, you have buckets and objects. A bucket is like a top-level directory, and objects are like files stored inside the bucket. Unlike traditional file systems, buckets do not nest, but you can simulate directories within a bucket using prefixes. |
| Accessing Files | Access files through the file explorer or terminal, using paths like C:/Documents/Project/file.txt. | Access objects using URLs, like https://s3.amazonaws.com/my-bucket/my-folder/my-file.txt, or through the AWS Management Console, command line, or SDKs. |

**Key Concepts in Amazon S3**
1. Buckets:
   - **What:** A bucket is the container where you store your data (objects).
   - **Similar To:** Think of it as a top-level folder or root directory in an OS file system.
   - **Unique Aspect:** Each bucket must have a unique name across the entire S3 system.
2. Objects:
   - **What:** Objects are the data files you store in a bucket. Each object consists of the data itself and metadata (information about the data).
   - **Similar To:** The files in your OS file system.
   - **Unique Aspect:** Each object is identified by a unique key (which acts like a filename) within the bucket.
3. Keys and Prefixes:
   - **What:** The key is the unique identifier for an object within a bucket. Prefixes are used to simulate folders.
   - **Similar To:** The file path in your OS file system.
   - **Example:** If an object key is `projects/science/experiment.txt`, `projects` and `science` are prefixes, making it seem as if the object is in a folder structure.
4. Storage Classes:
   - **What:** Different storage classes offer varying costs, availability, and durability.
   - **Example Classes:** Standard, Infrequent Access, Glacier (for long-term archival).
   - **Why:** To optimize cost based on how frequently you need to access the data.

**Operations in S3**
|                           | OS File System | Amazon S3 |
|---------------------------|----------------|-----------|
| Creating a Bucket         | Create a new directory. | You create a new bucket using the AWS Management Console, AWS CLI, or an SDK. |
| Uploading an Object       | Save a file into a directory. | You upload an object to a bucket, specifying the key (essentially the path and name). |
| Setting Permissions       | Set read/write permissions for files and directories. | Set permissions for who can view or modify objects. You can make objects public or restrict access using AWS Identity and Access Management (IAM) policies. |
| Accessing and Downloading | Open a file in an application or copy it to another location. | Access objects using URLs, or download them using the console, CLI, or programmatically. |
> [!NOTE]
> [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html) is the AWS SDK for Python to create, configure, and manage AWS services, such as Amazon S3.

### MLflow
Imagine you're working on a big science project with lots of experiments. You have to track each experiment, note down what changes you made, and see how those changes affected your results. MLflow is like a super-organized notebook and assistant specifically for machine learning projects.

Key Features of MLflow
1. Experiment Tracking
   - **What:** Keeps a record of all your experiments, including the data you used, the model settings, and the results.
   - **Why:** Helps you understand what changes led to better results, so you can easily replicate successful experiments.
2. Models Registry
   - **What:** A place to store and manage different versions of your machine learning models.
   - **Why:** Allows you to keep track of various versions and easily switch between them, ensuring you always know which model is the best.
3. Project Management
   - **What:** Lets you organize your code and dependencies into a standard format.
   - **Why:** Makes it easier to share your work with others and ensures your project runs smoothly on different computers.
4. Deployment
   - **What:** Helps you deploy your trained models to production environments so they can be used for making predictions.
   - **Why:** Simplifies the process of putting your models into action, making them available for real-world use.

Why Use MLflow?
1. **Organization:** Keeps all your experiments, models, and code well-organized.
2. **Reproducibility:** Makes it easy to replicate and verify results.
3. **Collaboration:** Simplifies sharing your work with others.
4. **Deployment:** Eases the process of turning your models into useful applications.

MLflow is like a powerful assistant for your machine learning projects, helping you track experiments, manage models, organize your project, and deploy your work, all in one place. It makes working on and sharing your machine learning experiments much easier and more effective. Learn more [here](https://mlflow.org/docs/latest/index.html)
