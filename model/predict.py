import json
import os
import pickle
import time
import traceback
from functools import lru_cache

import mlflow

from model.config import MODEL_FILES_LOCATION
from model.utils.logging import build_response, get_logger, log_response
from model.utils.validation import validate_input

logger = get_logger(__name__)


def init():
    """
    warm-up: this runs when the machine first starts and prepares the model for inference
    """
    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    logger.info(f"mlflow_tracking_uri={mlflow_tracking_uri}")
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    load_model()


@lru_cache()
def load_model():
    """
    LRU cache will save the function return values in cache memory.
    This way they aren't re-computed or loaded into memory each time the function is called.
    Returns:
        model object
    """

    # load your model here. Note: variable MODEL_FILES_LOCATION is defined in config file
    model_config = json.load((MODEL_FILES_LOCATION / "model.json").open())
    logger.info("location=%s model_config=%s", MODEL_FILES_LOCATION, model_config)
    path = f"""runs:/{model_config["run"]}/model"""
    model = mlflow.pyfunc.load_model(path)
    logger.info(f"loaded model from path {path}")

    return model, model_config["features"]


def predict(json_payload):
    start_time = time.time()
    output_dict = dict(data={}, error=None)

    try:
        # Make sure input is valid
        model, features = load_model()
        input_validation_result = validate_input(json_payload, features)

        # if input validation fails
        if "error" in input_validation_result:
            output_dict.update({"error": input_validation_result.pop("error")})
        # this will only run if input is valid
        else:
            input = input_validation_result.pop("input")
            prediction = model.predict(input)
            output_dict["data"].update({"SurvivalChance": prediction[0][0]})
        output_dict["data"].update(input_validation_result)

    # If we get here, it means we hit an exception
    except Exception as e:
        # NOTE: the error message will show UNENCRYPTED in Splunk, do not log any sensitive information
        log_response({"error": traceback.format_exc()})
        output_dict.update({"error": f"Error in predict: {repr(e)}. See logs."})

    finally:
        output_dict["metadata"] = {"execution_time": (time.time() - start_time) * 1000}
        response_dict = build_response(output_dict)
        log_response(response_dict)
        return json.dumps(response_dict)
