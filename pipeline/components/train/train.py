import argparse
import io
import json
import os
import warnings
from collections import defaultdict

import boto3
import lightgbm
import lightgbm as lgbm
import mlflow
import numpy as np
import pandas as pd
import plot_funcs as pf
from ensemble_model import EnsembleModel
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold
from utils import print_devider

parser = argparse.ArgumentParser()
parser.add_argument("--bucket", help="s3 bucket to use")
parser.add_argument("--processed-train-path", help="path of the training pickle file")
parser.add_argument("--param-path", help="path of the training param file")
parser.add_argument("--model-path", help="path to dump the training output")


def divide_by_sum(x):
    return x / x.sum()


def get_scores(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred),
        "recall": recall_score(y_true, y_pred),
        "f1": f1_score(y_true, y_pred),
    }


def log_plot(args, plot_func, fp):
    if not isinstance(args, (tuple)):
        args = (args,)

    plot_func(*args, fp)
    mlflow.log_artifact(fp)
    os.remove(fp)
    print(f"Logged {fp}")


def train_model(X, y, params):
    fold_params = params["fold"]
    model_params = params["model"]
    fit_params = params.get("fit", {})

    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    mlflow.tracking.set_tracking_uri(mlflow_tracking_uri)

    # set mlflow experiment
    exp_path = params["experiment"]["path"]
    try:
        mlflow.create_experiment(exp_path)
    except (mlflow.exceptions.RestException, mlflow.exceptions.MlflowException):
        print("The specified experiment ({}) already exists.".format(exp_path))

    mlflow.set_experiment(exp_path)

    early_stopping_rounds = fold_params.pop("early_stopping_rounds")
    skf = StratifiedKFold(**fold_params)
    models = []
    metrics = []

    y_proba = np.zeros(len(X))
    y_pred = np.zeros(len(X))

    feature_importances_split = np.zeros(X.shape[1])
    feature_importances_gain = np.zeros(X.shape[1])

    scores = defaultdict(int)

    with mlflow.start_run() as run:
        corr = pd.concat((X, y), axis=1).corr()
        log_plot(corr, pf.corr_matrix, "correlation_matrix.png")
        log_plot(y.value_counts(), pf.label_share, "label_share.png")

        for fold_no, (idx_train, idx_valid) in enumerate(skf.split(X, y)):
            print_devider(f"Fold: {fold_no}")

            X_train, X_valid = X.iloc[idx_train, :], X.iloc[idx_valid, :]
            y_train, y_valid = y.iloc[idx_train], y.iloc[idx_valid]

            # train model
            model = lgbm.LGBMClassifier(**model_params)
            model.fit(
                X_train,
                y_train,
                eval_set=[(X_valid, y_valid)],
                eval_names=["valid"],
                callbacks=[
                    lightgbm.early_stopping(stopping_rounds=early_stopping_rounds)
                ],
            )
            metrics.append(
                {
                    "name": model.metric,
                    "values": model.evals_result_["valid"][model.metric],
                    "best_iteration": model.best_iteration_,
                }
            )
            models.append(model)

            # feature importance
            feature_importances_split += (
                divide_by_sum(
                    model.booster_.feature_importance(importance_type="split")
                )
                / skf.n_splits
            )
            feature_importances_gain += (
                divide_by_sum(model.booster_.feature_importance(importance_type="gain"))
                / skf.n_splits
            )

            # predict
            y_valid_proba = model.predict_proba(
                X_valid, num_iteration=model.best_iteration_
            )[:, 1]
            y_valid_pred = model.predict(X_valid, num_iteration=model.best_iteration_)
            y_proba[idx_valid] = y_valid_proba
            y_pred[idx_valid] = y_valid_pred

            # evaluate
            scores_valid = get_scores(y_valid, y_valid_pred)

            mlflow.log_metrics(
                {
                    **scores_valid,
                    "best_iteration": model.best_iteration_,
                },
                step=fold_no,
            )

            print("\nScores")
            print(scores_valid)

            # record scores
            for k, v in scores_valid.items():
                scores[k] += v / skf.n_splits

        # log training parameters
        mlflow.log_params(
            {
                **fold_params,
                **model_params,
                **fit_params,
                "cv": skf.__class__.__name__,
                "model": model.__class__.__name__,
            }
        )

        print_devider("Saving plots")

        # scores
        log_plot(scores, pf.scores, "scores.png")

        # feature importance
        features = np.array(model.booster_.feature_name())
        log_plot(
            (features, feature_importances_split, "Feature Importance: split"),
            pf.feature_importance,
            "feature_importance_split.png",
        )
        log_plot(
            (features, feature_importances_gain, "Feature Importance: gain"),
            pf.feature_importance,
            "feature_importance_gain.png",
        )

        # metric history
        log_plot(metrics, pf.metric, "metric_history.png")

        # confusion matrix
        cm = confusion_matrix(y, y_pred)
        log_plot(cm, pf.confusion_matrix, "confusion_matrix.png")

        # roc curve
        fpr, tpr, _ = roc_curve(y, y_proba)
        roc_auc = roc_auc_score(y, y_pred)
        log_plot((fpr, tpr, roc_auc), pf.roc_curve, "roc_curve.png")

        # precision-recall curve
        pre, rec, _ = precision_recall_curve(y, y_proba)
        pr_auc = average_precision_score(y, y_pred)
        log_plot((pre, rec, pr_auc), pf.pr_curve, "pr_curve.png")

        ensemble_model = EnsembleModel(models)
        mlflow.pyfunc.log_model(
            "model", python_model=ensemble_model, pip_requirements=["numpy"]
        )

    return run.info.experiment_id, run.info.run_uuid


def train(df: pd.DataFrame, params: dict):
    warnings.filterwarnings("ignore")
    print("Running training")

    target = params.pop("data").get("target")
    X = df.drop(target, axis=1)
    y = df[target]

    experiment_id, run_uuid = train_model(X, y, params)
    training_output = {
        "experiment": experiment_id,
        "run": run_uuid,
        "features": X.dtypes.astype("str").to_dict(),
    }
    return training_output


def main():
    args = vars(parser.parse_args())
    print("Training started!")

    localstack_url = os.getenv("LOCALSTACK_URI")
    s3 = boto3.client("s3", endpoint_url=localstack_url)

    bucket = args["bucket"]

    train_obj = s3.get_object(Bucket=bucket, Key=args["processed_train_path"])
    df = pd.read_pickle(io.BytesIO(train_obj["Body"].read()))
    print(
        f"""Processed training data read from Bucket={bucket} Key={args["processed_train_path"]}"""
    )

    param_obj = s3.get_object(Bucket=bucket, Key=args["param_path"])
    params = param_obj["Body"].read().decode()
    print(f"""Read training params from Bucket={bucket} Key={args["param_path"]}""")
    print(params)

    training_output = train(df, json.loads(params))
    model_json = json.dumps(training_output)
    s3.put_object(
        Body=model_json,
        Bucket=bucket,
        Key=args["model_path"],
    )
    print(f"""Model file dumped to Bucket={bucket} Key={args["model_path"]}""")
    print(model_json)

    print("Training done!")


if __name__ == "__main__":
    main()
