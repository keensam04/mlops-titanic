from pathlib import Path

from model import __version__

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

MODEL_VERSION = __version__
MODEL_NAME = "mlops-titanic"

# Required field names and types
# This structure will be checked for as part of input validation
REQUIRED_FIELDS = {"PassengerId": int, "Name": str}

# When deployed in docker, model files are mounted to opt/ml/model
sm_path = Path("/opt/ml/model")
if sm_path and sm_path.exists():
    MODEL_FILES_LOCATION = sm_path
else:
    with pkg_resources.path("model", "predict.py") as p:
        MODEL_FILES_LOCATION = p.parent / "model_files"


# If you have any output fields with PII, or that you prefer not to log, list them here as set of strings:
FIELDS_TO_NOT_LOG = None
