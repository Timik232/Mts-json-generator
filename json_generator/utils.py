import logging
import os
from typing import Any, Dict, List, Optional, Union

import openai
from openai import OpenAIError

from .private_api import SECRET_TOKEN

API_URL = os.environ.get("API_URL", "https://api.gpt.mws.ru")
MODEL_NAME = os.environ.get("MODEL_NAME", "gemma-3-27b-it")
SYSTEM_PROMPT = "Тебе нужно создать Json схему"

client = openai.OpenAI(base_url=f"{API_URL}/v1", api_key=SECRET_TOKEN)


def generate(
    input_data: Union[str, List[Dict[str, Any]]], json_schema: Optional[Dict] = None
) -> str:
    """Генерирует ответ на основании введённых данных (текста или истории разговоров).

    Args:
        input_data (Union[str, List[Dict[str, Any]]]):
            Входные данные для генерации ответа. Может быть либо текстом (`prompt`),
            либо историей общения в виде списка сообщений (`messages`).
        json_schema (Optional[Dict]):
            Json-схема для форматирования ответа. Если не указана, то не используется.

    Raises:
        TypeError: Возникает, если тип данных не поддерживается.
        OpenAIError: Исключение, возникающее при проблемах взаимодействия с API OpenAI.

    Returns:
        str: Генерируемый ответ модели или сообщение об ошибке.
    """
    if isinstance(input_data, str):
        request_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": input_data},
        ]
    elif isinstance(input_data, list):
        request_messages = input_data
    else:
        error_msg = "Неверный тип данных. Должен быть string или list of dictionaries."
        logging.error(error_msg)
        raise TypeError(error_msg)

    try:
        if json_schema is None:
            response = client.chat.completions.create(
                messages=request_messages,
                model=MODEL_NAME,
            )
        else:
            response = client.chat.completions.create(
                messages=request_messages,
                model=MODEL_NAME,
                response_format={
                    "type": "json_schema",
                    "json_schema": json_schema,
                },
            )
        answer = response.choices[0].message.content
        return answer
    except OpenAIError as e:
        return f"Произошла ошибка при обращении к API: {str(e)}"
