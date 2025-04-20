import os

from .constants import API_URL, MODEL_NAME
from .generator import autogen_test
from .logging_config import configure_logging
from .utils import ClarifierSchema, generate

try:
    from .private_api import SECRET_TOKEN
except ImportError:
    SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "")
if not SECRET_TOKEN:
    import logging

    logging.warning(
        "SECRET_TOKEN not found in private_api or environment variables. API calls may fail."
    )

__all__ = [
    "generate",
    "API_URL",
    "MODEL_NAME",
    "configure_logging",
    "autogen_test",
    "SECRET_TOKEN",
    "ClarifierSchema",
]
