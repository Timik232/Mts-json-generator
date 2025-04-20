"""Конфиг модели для autogen, по умолчанию gemma-3-27b-it"""
from autogen_ext.models.openai._model_info import ModelFamily, ModelInfo

from .constants import (
    COMPLETION_TOKENS,
    CONTEXT_TOKENS,
    FUNCTION_CALLING,
    JSON_OUTPUT,
    MODEL_NAME,
    VISION,
)

custom_model_info = ModelInfo(
    name=MODEL_NAME,
    family=ModelFamily.UNKNOWN,
    context_tokens=CONTEXT_TOKENS,
    completion_tokens=COMPLETION_TOKENS,
    json_output=JSON_OUTPUT,
    vision=VISION,
    function_calling=FUNCTION_CALLING,
)
