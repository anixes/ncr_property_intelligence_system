import os
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file if it exists
load_dotenv()

# Paths
PROJ_ROOT = Path(__file__).resolve().parents[1]
logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")

DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

MODELS_DIR = PROJ_ROOT / "models"

REPORTS_DIR = PROJ_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# MLflow
# Use file:/// URI so MLflow behaves consistently across OS.
# Override via environment variable for Docker / CI environments.
_default_tracking_uri = (PROJ_ROOT / "mlruns").resolve().as_uri()  # file:///...
MLFLOW_TRACKING_URI: str = os.environ.get("MLFLOW_TRACKING_URI", _default_tracking_uri)
MLFLOW_EXPERIMENT_NAME: str = "ncr-property-price"
MLFLOW_MODEL_NAME: str = "property-price-estimator"

# If tqdm is installed, configure loguru with tqdm.write
# https://github.com/Delgan/loguru/issues/135
try:
    from tqdm import tqdm

    logger.remove(0)
    logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)
except ModuleNotFoundError:
    pass
