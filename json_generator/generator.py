"""
Пример использования AutoGen с собственным URL-эндпоинтом API.
"""

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from model_info import custom_model_info

from .private_api import SECRET_TOKEN
from .utils import API_URL, MODEL_NAME


async def autogen_test():
    model_client = OpenAIChatCompletionClient(
        model=MODEL_NAME,
        api_key=SECRET_TOKEN,
        base_url=API_URL,
        model_info=custom_model_info,
    )

    assistant = AssistantAgent(name="assistant", model_client=model_client)

    response = await assistant.run(task="Скажи познакомься на русском")
    print("Ответ агента:", response)

    await model_client.close()
