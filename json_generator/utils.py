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


class VacancySchema(BaseModel):
    """
    Pydantic-схема для структурированного ответа от модели Ollama.:
    title: VacancySchema
    """

    vacancy: str = Field(..., description="Название вакансии")
    percentage: int = Field(
        ..., description="Процент соответствия кандидата вакансии от 0 до 100"
    )
    explaining: str = Field(..., description="Описание соответствия кандидата вакансии")
    recommendations: str = Field(..., description="Рекомендации по улучшению навыков")


client = openai.OpenAI(base_url=f"{API_URL}/v1", api_key=SECRET_TOKEN)


def generate(
    input_data: Union[str, List[Dict[str, Any]]],
    system_prompt: str = "Ты ассистент для помощи пользователю.",
    json_schema: Optional[Dict] = None,
) -> str:
    """Генерирует ответ на основании введённых данных (текста или истории разговоров).

    Args:
        input_data (Union[str, List[Dict[str, Any]]]):
            Входные данные для генерации ответа. Может быть либо текстом (`prompt`),
            либо историей общения в виде списка сообщений (`messages`).
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
