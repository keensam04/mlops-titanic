import numpy as np

from model.config import REQUIRED_FIELDS


def _process_value(value, type_):
    if type_ == "int8":
        return np.int8(value)
    elif type_ == "float16":
        return np.float16(value)
    return np.nan


def validate_input(json_payload: dict, features: dict[str, str]) -> dict:
    """
    If input is valid, then "input_valid" variable should be True
    If input is NOT valid, "input_valid" variable should be False
    Error variable should be a string that describes the problem if there is one.
    """
    res = {}
    validated_input = []
    error = ""

    # This loop validates json fields and types as specified in the REQUIRED_FIELDS dictionary in config.py
    for field, type_ in REQUIRED_FIELDS.items():
        if field not in json_payload:
            error += f"{field} is missing. "
        else:
            if not isinstance(json_payload[field], type_):
                error += f"{field} type should be {type_}, but it's {type(json_payload[field])}. "
            else:
                res[field] = json_payload[field]

    for field, type_ in features.items():
        try:
            if field not in json_payload:
                if "_" in field:
                    field_, value_ = field.split("_")
                    if value_ == "Unknown":
                        validated_input.append(_process_value(0, type_))
                    elif field_ in json_payload:
                        value = _process_value(json_payload[field_] == value_, type_)
                        validated_input.append(value)
                    else:
                        error_ = f"{field_} is missing. "
                        if error_ not in error:
                            error += error_
                else:
                    error += f"{field} is missing. "
            else:
                value = _process_value(json_payload[field], type_)
                validated_input.append(value)
        except ValueError:
            error += f"{field} type should be {type_}, but it's {type(json_payload[field])}. "

    # The output format is a dictionary that should contain:
    # all REQUIRED_FIELDS
    # input - validated input as array
    # error - a string explaining the issue with the input. None if input is valid.
    if error:
        res["error"] = error
    if len(validated_input) == len(features):
        res["input"] = np.array(validated_input).reshape(1, -1)
    return res
