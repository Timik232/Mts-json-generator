""" Файл для вспомогательных функций и классов"""
import logging
import os
from typing import Any, Dict, List, Optional, Union

import openai
from openai import OpenAIError
from pydantic import BaseModel, Field

from .constants import API_URL, MODEL_NAME

try:
    from .private_api import SECRET_TOKEN
except ImportError:
    SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "")

if SECRET_TOKEN == "":
    raise ValueError(
        "SECRET_TOKEN is not set. Please set it as an environment variable."
    )


class ClarifierSchema(BaseModel):
    """
    Pydantic-схема для агента по уточнению недостающих полей.:
    title: ClarifierSchema
    """

    missing: List[str] = Field(
        ...,
        description="Список пропущенных полей для генерации. Может быть "
        "пустым, если все поля присутствуют.",
    )
    mentioned_params: List[Dict[str, Any]] = Field(
        ...,
        description="Список полей, которые"
        " были заполнены в сообщении пользователя. ",
    )
    can_generate_schema: bool = Field(
        ...,
        description="Может ли сгенерировать схему"
        "или отсутствует информация для"
        "необходимых полей. True значит, что"
        "может сгенерировать схему.",
    )
    message: str = Field(
        ...,
        description="Сообщение от агента для пользователя"
        "просьбой учтонить информацию по недостающим полям.",
    )


client = openai.OpenAI(base_url=f"{API_URL}/v1", api_key=SECRET_TOKEN)

FUNCTION_DEFINITIONS = [
    {
        "name": "retrieve_documents",
        "description": "Выполняет поиск в системе RAG и возвращает список релевантных документов",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Текст запроса для поиска"},
                "top_k": {
                    "type": "integer",
                    "description": "Максимальное число документов для возвращения",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    }
]


def generate(
    input_data: Union[str, List[Dict[str, Any]]],
    model: str = MODEL_NAME,
    system_prompt: str = "Ты ассистент для помощи пользователю.",
    json_schema: Optional[Dict] = None,
) -> str:
    """Генерирует ответ на основании введённых данных (текста или истории разговоров).

    Args:
        input_data (Union[str, List[Dict[str, Any]]]):
            Входные данные для генерации ответа. Может быть либо текстом (`prompt`),
            либо историей общения в виде списка сообщений (`messages`).
        model (str): название модели
        system_prompt (str):
            Системный промпт для модели
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
            {"role": "system", "content": system_prompt},
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
                model=model,
            )
        else:
            response = client.chat.completions.create(
                messages=request_messages,
                model=MODEL_NAME,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "clarifierschema",
                        "schema": json_schema,
                        "strict": True,
                    },
                },
            )
        answer = response.choices[0].message.content
        return answer
    except OpenAIError as e:
        return f"Произошла ошибка при обращении к API: {str(e)}"
