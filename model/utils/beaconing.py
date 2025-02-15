import inspect
import json
import logging
from datetime import datetime
from functools import wraps

from model.config import BEACON_LOCATION

formatter = logging.Formatter("%(message)s")

handler = logging.FileHandler(f"{BEACON_LOCATION}/beacon.log")
handler.setFormatter(formatter)

beacon_logger = logging.getLogger(__name__)
beacon_logger.setLevel(logging.INFO)
beacon_logger.addHandler(handler)


def beacon(func):
    @wraps(func)
    def with_beaconing(*args, **kwargs):
        time_ = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        full_arg_spec = inspect.getfullargspec(func)
        inputs_to_log = [*args]
        if len(args) < len(full_arg_spec.args):
            defaults_to_log = len(full_arg_spec.args) - len(args)
            inputs_to_log.extend(list(full_arg_spec.defaults[-defaults_to_log:]))
        inputs = {k: v for k, v in zip(full_arg_spec.args, inputs_to_log)}
        inputs.update(kwargs)
        response = func(*args, **kwargs)
        output = json.loads(response) if isinstance(response, str) else response
        beacon_logger.info(
            json.dumps({"time": time_, "inputs": inputs, "output": output})
        )
        return response

    return with_beaconing
