import kfp
from kfp import dsl


def adhoc(base_image="python:3.10-slim-bullseye", **kwargs):
    def _adhoc(func):
        return kfp.components.create_component_from_func(
            func, base_image=base_image, **kwargs
        )

    return _adhoc


@adhoc()
def status_op(name: str, status: str):
    print(f"workflow={name} status={status}")


# Custom components
seed_op = kfp.components.load_component("pipeline/components/seed/seed.yaml")
preprocessing_op = kfp.components.load_component(
    "pipeline/components/pre-processing/pre-processing.yaml"
)
training_op = kfp.components.load_component("pipeline/components/train/train.yaml")


# Pipeline
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
        seed = seed_op(bucket, param_path, train_path, test_path).after(status)
        preprocess = preprocessing_op(
            bucket, train_path, test_path, processed_train_path
        ).after(seed)
        training_op(bucket, processed_train_path, param_path, model_path).after(
            preprocess
        )
