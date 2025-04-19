from autogen_ext.models.openai._model_info import ModelFamily, ModelInfo

custom_model_info = ModelInfo(
    name="gemma3-27b-it",
    family=ModelFamily.UNKNOWN,
    context_tokens=131072,
    completion_tokens=131072,
    json_output=True,
    vision=True,
    function_calling=True,
)
