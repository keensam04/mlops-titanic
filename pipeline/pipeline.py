"""Minimal pipeline.py file to demonstrate a simple kubeflow DAG which to mimic the ML-Lifecycle"""
import kfp
from kfp import dsl


def adhoc(base_image="python:3.10-slim-bullseye", **kwargs):
    """Helper utility to create sny adhoc components for the dag"""
    def _adhoc(func):
        return kfp.components.create_component_from_func(
            func, base_image=base_image, **kwargs
        )

    return _adhoc


@adhoc()
def status_op(name: str, status: str):
    """Dummy method to send pipeline status to the configured channel.
    In this example, it's STDOUT. In practice, it is usually a notification to Slack or email etc"""
    print(f"workflow={name} status={status}")


# Custom components (We will explore what each one does in a bit)
# Each of these components can be thought of a node in a DAG (Directed Acyclic Graph)
seed_op = kfp.components.load_component("pipeline/components/seed/seed.yaml")

# Minimal Pre-processing fo the underlying raw dataset
preprocessing_op = kfp.components.load_component(
    "pipeline/components/pre-processing/pre-processing.yaml"
)

# Train a minimal ML Model
training_op = kfp.components.load_component("pipeline/components/train/train.yaml")


# Pipeline Definition (i.e Create the DAg structure for your custom pipeline)
@dsl.pipeline()
def pipeline(
    bucket: str = "mybucket",
    param_path: str = "param.json",
    train_path: str = "train.csv",
    test_path: str = "test.csv",
    processed_train_path: str = "train.pickle",
    model_path: str = "model.json",
):
    notify_finished = status_op(name="{{workflow.name}}", status="{{workflow.status}}")

    with dsl.ExitHandler(notify_finished):
        status = status_op(name="{{workflow.name}}", status="Started")

        # Seed runs after status
        seed = seed_op(bucket, param_path, train_path, test_path).after(status)

        # preprocess runs after seed
        preprocess = preprocessing_op(
            bucket, train_path, test_path, processed_train_path
        ).after(seed)

        # training  runs after preprocess
        training_op(bucket, processed_train_path, param_path, model_path).after(
            preprocess
        )
