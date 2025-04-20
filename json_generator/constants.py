"""Файл для констант"""
import os

API_URL = os.environ.get("API_URL", "https://api.gpt.mws.ru")
MODEL_NAME = os.environ.get("MODEL_NAME", "gemma-3-27b-it")
SYSTEM_JSON_CREATOR = (
    "Используя документацию и json-shema,"
    "тебе нужно создать Json схему. Ответ должен"
    "содержать только json-схему без дополнительных комментариев."
)
JSON_DESCRIPTION = "Бот создаёт Json-схему на основе предоставленной документации."
SYSTEM_CLARIFIER = (
    "Тебе нужно составить запрос для агента для создания схемы, но "
    "для этого необходимо уточнить недостающие поля."
    "Если все необходимые поля уже есть, то сообщи об"
    "этом."
)
CLARIFIER_DESCRIPTION = "Бот уточняет недостающие поля для создания Json-схемы."
CONTEXT_TOKENS = 131072
COMPLETION_TOKENS = 131072
JSON_OUTPUT = True
VISION = True
FUNCTION_CALLING = True
