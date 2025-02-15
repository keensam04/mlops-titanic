import logging
import sys

from flask import request

from model.config import FIELDS_TO_NOT_LOG, MODEL_NAME, MODEL_VERSION


class TidLoggingFormatter(logging.Formatter):
    """
    Class to add tid to log messages.
    """

    def format(self, record):
        # Runtime error will occur if not in a request context
        try:
            record.tid = request.headers.get("tid", "-")
        except RuntimeError as e:
            print(f"Failed parsing the X-Amzn-SageMaker-Custom-Attributes Header: {e}")
            record.tid = "-"
        return super().format(record)


def get_logger(logger_name, level=logging.INFO):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)

    formatter = TidLoggingFormatter(
        fmt="%(asctime)s.%(msecs)03d - %(levelname)s - %(module)s: %(message)s tid=%(tid)s"
    )

    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


logger = logging.getLogger("logging")


def build_response(output_dict: dict) -> dict:
    """
    This function builds the model response in preparation for logging and output.
    By default, model name and version will be logged along with prediction and execution time.
    You can add any additional KEY+VALUE pairs in the response dict.
    """

    response_dict = {
        "model": MODEL_NAME,
        "version": MODEL_VERSION,
    }

    output_dict["metadata"].update(response_dict)

    return output_dict


def log_response(response_dict: dict):
    """
    This function logs the output dict, sans any fields listed in "FIELDS_NOT_TO_LOG".
    **** NOTE: LOGS ARE NOT ENCRYPTED! do not send any PII ****
    """

    if FIELDS_TO_NOT_LOG:
        for unwanted_key in FIELDS_TO_NOT_LOG:
            response_dict.pop(unwanted_key, None)

    if "error" in response_dict.keys():
        logger.error(response_dict)
    else:
        logger.info(response_dict)
