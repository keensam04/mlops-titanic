import argparse
import io
import os

import boto3
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

parser = argparse.ArgumentParser()
parser.add_argument("--bucket", help="s3 bucket to use")
parser.add_argument("--train-path", help="path of the training csv file")
parser.add_argument("--test-path", help="path of the test csv file")
parser.add_argument(
    "--processed-train-path", help="path to dump the training pickle file"
)


def replace_ext(fp, ext):
    return os.path.splitext(fp)[0] + (ext if ext.startswith(ext) else f".{ext}")


def describe(df):
    nrows = len(df)
    df_ret = pd.DataFrame()
    df_ret["feature"] = df.columns
    df_ret["dtype"] = df.dtypes.values

    # null
    df_ret["null_count"] = df.isnull().sum().values
    df_ret["non_null_count"] = df.notnull().sum().values

    # numeric features
    numeric = df.select_dtypes(
        ["int8", "int16", "int32", "int64", "float16", "float32", "float64"]
    )
    df_ret["max"] = df_ret["feature"].map(numeric.max())
    df_ret["min"] = df_ret["feature"].map(numeric.min())
    df_ret["mean"] = df_ret["feature"].map(numeric.mean())
    df_ret["median"] = df_ret["feature"].map(numeric.median())
    df_ret["std"] = df_ret["feature"].map(numeric.std())

    for col in df.columns:
        val_counts = df[col].value_counts(dropna=False)
        top_vals = val_counts.index.tolist()
        df_ret.loc[df_ret["feature"] == col, "unique_count"] = len(top_vals)
        df_ret.loc[df_ret["feature"] == col, "top_value"] = top_vals[0]
        df_ret.loc[df_ret["feature"] == col, "top5_values"] = ", ".join(
            map(lambda x: str(x), top_vals[:5])
        )
        df_ret.loc[df_ret["feature"] == col, "top_value_ratio"] = (
            val_counts.values[0] / nrows
        )

    df_ret["distinct"] = (df_ret["unique_count"] == nrows).astype(int)

    return df_ret


def reduce_mem_usage(df, verbose=True):
    numerics = ["int16", "int32", "int64", "float16", "float32", "float64"]
    start_mem = df.memory_usage().sum() / 1024**2
    for col in df.columns:
        col_type = df[col].dtypes
        if col_type in numerics:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type).startswith("int"):
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            else:
                if (
                    c_min > np.finfo(np.float16).min
                    and c_max < np.finfo(np.float16).max
                ):
                    df[col] = df[col].astype(np.float16)
                elif (
                    c_min > np.finfo(np.float32).min
                    and c_max < np.finfo(np.float32).max
                ):
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)

    end_mem = df.memory_usage().sum() / 1024**2
    if verbose:
        print(
            "Memory usage decreased to {:.2f} Mb ({:.1f}% reduction)".format(
                end_mem, 100 * (start_mem - end_mem) / start_mem
            )
        )


def pre_processing(train: pd.DataFrame, test: pd.DataFrame):
    cols_to_drop = ["Cabin", "Name", "PassengerId", "Ticket"]
    train.drop(cols_to_drop, axis=1, inplace=True)
    test.drop(cols_to_drop, axis=1, inplace=True)

    # fill unknown because label encoder can't accept nan
    train["Embarked"] = train["Embarked"].fillna("Unknown")
    test["Embarked"] = test["Embarked"].fillna("Unknown")

    merged = pd.concat((train, test), axis=0).reset_index(drop=True)

    # impute numerical columns
    train["Fare"] = train["Fare"].fillna(merged["Fare"].mean())
    test["Fare"] = test["Fare"].fillna(merged["Fare"].mean())
    train["Age"] = train["Age"].fillna(merged["Age"].mean())
    test["Age"] = test["Age"].fillna(merged["Age"].mean())

    for col in train.columns:
        if train[col].dtype == "object":
            le = LabelEncoder()
            ohe = OneHotEncoder()

            # fit both encoders with merged data
            le.fit(merged[col])
            merged[col] = le.transform(merged[col])
            new_cols = ["{}_{}".format(col, c) for c in le.classes_]
            ohe.fit(merged[[col]])

            # encode train data
            train[col] = le.transform(train[col])
            ohe_array = ohe.transform(train[[col]]).toarray().astype(int)
            train[new_cols] = pd.DataFrame(ohe_array)
            train.pop(col)

            # encode test data
            test[col] = le.transform(test[col])
            ohe_array = ohe.transform(test[[col]]).toarray().astype(int)
            test[new_cols] = pd.DataFrame(ohe_array)
            test.pop(col)

            # normal label encoding
            # le = LabelEncoder()
            # le.fit(list(train[col].astype(str).values) + list(test[col].astype(str).values))
            # train[col] = le.transform(train[col].astype(str).values)
            # test[col] = le.transform(test[col].astype(str).values)

            # count encoding
            # train[col + '_freq'] = train[col].map(merged[col].value_counts(dropna=False))
            # test[col + '_freq'] = test[col].map(merged[col].value_counts(dropna=False))


def main():
    args = vars(parser.parse_args())
    print("Pre processing started!")

    localstack_url = os.getenv("LOCALSTACK_URI")
    s3 = boto3.client("s3", endpoint_url=localstack_url)

    bucket = args["bucket"]

    train_obj = s3.get_object(Bucket=bucket, Key=args["train_path"])
    train = pd.read_csv(io.BytesIO(train_obj["Body"].read()))
    print(f"""Train data read from Bucket={bucket} Key={args["train_path"]}""")

    test_obj = s3.get_object(Bucket=bucket, Key=args["test_path"])
    test = pd.read_csv(io.BytesIO(test_obj["Body"].read()))
    print(f"""Test data read from Bucket={bucket} Key={args["test_path"]}""")

    pre_processing(train, test)
    print(f"""Training data processed""")

    reduce_mem_usage(train)
    print(f"""Training data optimized""")

    pickle_buffer = io.BytesIO()
    train.to_pickle(pickle_buffer)
    s3.put_object(
        Body=pickle_buffer.getvalue(),
        Bucket=bucket,
        Key=args["processed_train_path"],
    )
    print(
        f"""Processed training data file dumped to Bucket={bucket} Key={args["processed_train_path"]}"""
    )

    print("Pre processing done!")


if __name__ == "__main__":
    main()
