"""Файл с реализацией системы агентов для работы программы"""
import json
import logging
import time
from typing import Annotated, Any, Dict, Tuple

from autogen import Cache, ConversableAgent
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from .constants import (
    API_URL,
    CLARIFIER_DESCRIPTION,
    CLARIFIER_TASK,
    CLARIFY_JSON_TASK,
    JSON_DESCRIPTION,
    JSON_TASK,
    MODEL_NAME,
    SYSTEM_CLARIFIER,
    SYSTEM_CLARIFIER_WITHOUT_TERMINATE,
    SYSTEM_JSON_CREATOR,
)
from .logging_config import configure_logging
from .model_info import custom_model_info
from .retrieval import get_retriever
from .sessions import SessionContext
from .utils import SECRET_TOKEN, ClarifierSchema, generate

configure_logging()

# Инициализация LLM клиента
logging.debug("Инициализация OpenAIChatCompletionClient")

# Инициализация ретривера
retriever = get_retriever()
logging.debug("SimpleRetrievalAgent инициализирован")


model_client = OpenAIChatCompletionClient(
    model=MODEL_NAME,
    api_key=SECRET_TOKEN,
    base_url=API_URL,
    model_info=custom_model_info,
)
llm_config = {
    "config_list": [
        {
            "model": MODEL_NAME,
            "api_key": SECRET_TOKEN,
            "base_url": API_URL,
        }
    ],
    "timeout": 300,
}
# Инициализация агентов
schema_agent = AssistantAgent(
    name="schema_generator",
    system_message=SYSTEM_JSON_CREATOR,
    description=JSON_DESCRIPTION,
    model_client=model_client,
)

clarification_agent = ConversableAgent(
    name="clarifier",
    system_message=SYSTEM_CLARIFIER,
    description=CLARIFIER_DESCRIPTION,
    llm_config=llm_config,
)
user_proxy = ConversableAgent(
    name="User",
    llm_config=False,
    is_termination_msg=lambda msg: msg.get("content") is not None
    and "TERMINATE" in msg["content"],
    max_consecutive_auto_reply=10,
    human_input_mode="NEVER",
)


@user_proxy.register_for_execution()
@clarification_agent.register_for_llm(description="Получить json-документацию")
def retrieve_documents(
    query: Annotated[
        str,
        "Запрос к RAG системе для получения документации с указанием"
        "необходимой темы",
    ],
) -> Tuple[str, str]:
    """Получить документ json-schema из бд"""
    if isinstance(query, dict) and "query" in query:
        query = str(query["query"])
    query = str(query)
    answer = retriever.hybrid_search(query=query)
    key = answer[0]["metadata"]["original_key"]
    docs = answer[0]["metadata"]["original_value"]
    return key, docs


logging.info("Агенты schema_generator и clarifier готовы")


class ChatManager:
    """Менеджер чата, осуществляющий управление"""

    def __init__(self):
        self.sessions: Dict[str, SessionContext] = {}
        logging.info("ChatManager создан")
        self.model_name = "gemma-3-27b-it"
        self.max_api_retries = 3
        self.retry_delay = 1

    def clear_messages(self, session_id: str):
        """Очистить сообщения в памяти сессии"""
        try:
            session = self.sessions.setdefault(session_id, SessionContext())
            session.clear_session()
            return True
        except Exception:
            return False

    async def handle_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Обработчик сообщений"""
        session = self.sessions.setdefault(session_id, SessionContext())
        session.update_with_user(message)
        result = self._detect_missing_params(session)
        try:
            json_result = json.loads(result)
        except json.JSONDecodeError:
            logging.error("Ошибка конвертации в Json")
            return {
                "message": "Произошла внутренняя ошибка, попробуйте снова",
                "json_schema": "",
            }
        session.set_missing(json_result["missing"])
        for i in json_result["mentioned_params"]:
            session.add_collected_param(i[0], i[1])
        if not json_result["can_generate_schema"]:
            session.awaiting_clarification = True
            return {"message": json_result["message"], "json_schema": ""}
        else:
            try:
                answer = self._generate_with_retry(  # Изменено на метод с retry
                    JSON_TASK + " ".join(session.get_messages()),
                    system_prompt=SYSTEM_JSON_CREATOR,
                    model=self.model_name,
                    json_schema=json.loads(session.bd_context),
                )
            except Exception:
                logging.warning("Json schema не валидна")
                answer = self._generate_with_retry(  # Изменено на метод с retry
                    JSON_TASK
                    + " ".join(session.get_messages())
                    + "Схема: "
                    + session.bd_context,
                    system_prompt=SYSTEM_JSON_CREATOR,
                    model=self.model_name,
                )
            return {"message": "Полученная схема", "json_schema": answer}

    def _detect_missing_params(self, session: SessionContext) -> str:
        """проверить, каких параметров не хватает или всех хватает"""
        history = session.get_messages()
        history.append(CLARIFIER_TASK)
        history = " ".join(history)
        with Cache.disk() as cache:
            chat_result = user_proxy.initiate_chat(
                clarification_agent,
                message=history,
                max_turns=2,
                summary_method="reflection_with_llm",
                cache=cache,
            )

        chat_text = self._extract_content(chat_result)
        tool_extract = self._extract_tool_responses(chat_result)
        required_field = self.get_required_fields(
            parameters=json.loads(tool_extract[1]),
            parent_path="",
        )
        required_prompt = self._generate_missing_params_prompt(
            required_fields=required_field,
        )
        session.update_with_bd_context(
            bd_context=tool_extract[1], model_type=tool_extract[0]
        )
        prompt = (
            CLARIFY_JSON_TASK
            + "рассматриваем составляющую  "
            + tool_extract[0]
            + " для workflow. "
            + chat_text
            + required_prompt
        )
        raw_answer = generate(
            prompt,
            model=self.model_name,
            system_prompt=SYSTEM_CLARIFIER_WITHOUT_TERMINATE,
            json_schema=ClarifierSchema.model_json_schema(),
        )

        return raw_answer

    def _extract_summary(self, task_result: dict | Any) -> str:
        """извлечь пересказ чата"""
        return task_result.summary

    def _extract_content(self, task_result: dict | Any) -> str:
        """
        Извлекает содержимое из сообщения ассистента, пропуская инструменты (tool calls/responses)
        """
        history = []

        for msg in task_result.chat_history:
            # Пропускаем системные сообщения и сообщения от инструментов
            if msg.get("role") in ["tool", "system"]:
                continue

            entry = []
            role = msg.get("role", "unknown")
            name = msg.get("name", "unknown")
            content = msg.get("content")

            # Формируем заголовок
            header = f"[{role.upper()}"
            if name and name != role:
                header += f" ({name})"
            header += "]"

            # Добавляем только текстовый контент
            if content and content.strip():
                entry.append(f"{header}: {content.strip()}")

            if entry:
                history.extend(entry)

        return "\n".join(history)

    # def _extract_content(self, task_result: dict | Any) -> str:
    #     """
    #     Извлекает содержимое из сообщения ассистента
    #     """
    #     history = []
    #
    #     for msg in task_result.chat_history:
    #         entry = []
    #
    #         # Базовая информация
    #         role = msg.get("role", "unknown")
    #         name = msg.get("name", "unknown")
    #         content = msg.get("content")
    #
    #         # Заголовок сообщения
    #         header = f"[{role.upper()}"
    #         if name and name != role:
    #             header += f" ({name})"
    #         header += "]"
    #
    #         # Обработка разных типов сообщений
    #         if role == "assistant" and msg.get("tool_calls"):
    #             for call in msg["tool_calls"]:
    #                 func = call["function"]
    #                 entry.append(f"{header} CALL {func['name']}: {func['arguments']}")
    #
    #         elif role == "tool" and msg.get("tool_responses"):
    #             for response in msg["tool_responses"]:
    #                 entry.append(f"{header} RESPONSE: {response['content']}")
    #
    #         elif content:
    #             entry.append(f"{header}: {content.strip()}")
    #
    #         if entry:
    #             history.extend(entry)
    #
    #     return "\n".join(history)

    def _extract_tool_responses(self, chat_result: dict | Any) -> str:
        """Извлекает последний ответ от инструментов (tool responses) из истории чата"""
        for msg in reversed(chat_result.chat_history):
            if msg.get("role") == "tool" and msg.get("tool_responses"):
                # Берем последний ответ из списка tool_responses
                last_response = msg["tool_responses"][-1]
                if last_response["content"] and last_response["content"].strip() != "":
                    print("____________1___________")
                    print(last_response["content"])
                    try:
                        json.loads(last_response["content"][1])
                    except json.JSONDecodeError:
                        logging.error("Cant decode")
                    return last_response["content"]
        return ""

    def _generate_with_retry(self, *args, **kwargs) -> Any:
        """
        Повторяет вызов API с задержкой при ошибках.

        Args:
            *args: Аргументы для функции generate
            **kwargs: Ключевые аргументы для функции generate

        Returns:
            Результат выполнения generate()

        Raises:
            Exception: Если все попытки подключения исчерпаны
        """
        for attempt in range(self.max_api_retries):
            try:
                return generate(*args, **kwargs)
            except Exception as e:
                if attempt < self.max_api_retries - 1:
                    logging.warning(
                        f"Ошибка API (попытка {attempt + 1}): {str(e)}. Повтор через {self.retry_delay}с"
                    )
                    time.sleep(self.retry_delay)
                else:
                    logging.error("Все попытки подключения к API исчерпаны")
                    raise

    def _generate_missing_params_prompt(self, required_fields: list) -> str:
        """
        Генерирует строку с описанием недостающих параметров на основе извлеченного контента.

        Args:
            required_fields: Список обязательных полей и их описаний

        Returns:
            Строка с форматированным списком параметров для заполнения
        """

        prompt_lines = ["Список необходимых параметров:"]
        for field, desc in required_fields:
            prompt_lines.append(f"- Поле: {field}")
            prompt_lines.append(f"  Описание: {desc}")

        return "\n".join(prompt_lines)

    def get_required_fields(self, parameters, parent_path=""):
        required = []
        for param, config in parameters.items():
            current_path = f"{parent_path}.{param}" if parent_path else param

            # Проверяем, является ли текущий параметр обязательным
            if config.get("required", False):
                description = config.get("description", "No description")
                required.append((current_path, description))

            # Рекурсивно проверяем подкомпоненты
            if "subcomponents" in config:
                sub_required = self.get_required_fields(
                    config["subcomponents"], current_path
                )
                required.extend(sub_required)

        return required
