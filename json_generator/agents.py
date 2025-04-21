"""Файл с реализацией системы агентов для работы программы"""
import json
import logging
import time
from typing import Annotated, Any, Dict, List

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

logging.debug("Инициализация OpenAIChatCompletionClient")

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
    is_termination_msg=lambda msg: isinstance(msg, dict)
    and msg.get("content") is not None
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
) -> str:
    """Получить документ json-schema из бд"""
    if isinstance(query, dict) and "query" in query:
        query = str(query["query"])
    query = str(query)
    answer = retriever.hybrid_search(query=query)
    docs = answer[0]["metadata"]["original_value"]
    return docs


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
        logging.info("полный ответ" + str(json_result))
        session.set_missing(json_result["missing"])
        for field, desc in json_result["mentioned_params"].items():
            session.add_collected_param(field, desc)
        if not json_result["can_generate_schema"]:
            # session.awaiting_clarification = True
            return {"message": json_result["message"], "json_schema": ""}
        else:
            try:
                print(session.bd_context)
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
                    + "В ответе должен быть только Json, без ``` и других подобных символов. Схема: "
                    + session.bd_context,
                    system_prompt=SYSTEM_JSON_CREATOR,
                    model=self.model_name,
                )
                left_trimmed = answer.lstrip().lstrip(lambda x: x != "{")
                right_trimmed = left_trimmed.rstrip().rstrip(lambda x: x != "}")

                final_result = right_trimmed.strip()
                answer = final_result
            return {"message": "Полученная схема", "json_schema": answer}

    def _detect_missing_params(self, session: SessionContext) -> str:
        """проверить, каких параметров не хватает или всех хватает"""
        chat_text = None
        history = session.get_messages()
        buf = history.copy()
        buf.append(CLARIFIER_TASK)
        msg = " ".join(buf)
        if session.bd_context == "":
            with Cache.disk() as cache:
                chat_result = user_proxy.initiate_chat(
                    clarification_agent,
                    message=msg,
                    max_turns=2,
                    summary_method="reflection_with_llm",
                    cache=cache,
                )

            chat_text = self._extract_content(chat_result)
        if session.awaiting_clarification:
            tool_extract = session.bd_context
        else:
            tool_extract = self._extract_tool_responses(chat_result)
        if session.awaiting_clarification:
            buf = history.copy()
            buf.append(session.get_collected_params_as_str())
            msg = "\n".join(buf)
            session.clear_missing()

        required_prompt = self.get_required_fields(
            tool_extract,
        )
        print(2)
        logging.info("required prompt " + required_prompt)
        session.update_with_bd_context(bd_context=tool_extract)
        prompt = CLARIFY_JSON_TASK + chat_text if chat_text else "" + required_prompt
        logging.info("MEssage for final solution " + prompt)
        raw_answer = generate(
            "Предыдущие сообщения пользователя и уже введённые поля: " + msg + prompt,
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
        logging.info("Content extraction")
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

    def _extract_tool_responses(self, chat_result: dict | Any) -> str:
        """Извлекает последний ответ от инструментов (tool responses) из истории чата"""
        logging.info("Tool response extraction")
        for msg in reversed(chat_result.chat_history):
            if msg.get("role") == "tool" and msg.get("tool_responses"):
                # Берем последний ответ из списка tool_responses
                last_response = msg["tool_responses"][-1]
                if last_response["content"] and last_response["content"].strip() != "":
                    answer = last_response["content"]
                    print(type(answer))
                    print("____________1___________")
                    print(answer)
                    try:
                        json.loads(answer)
                    except json.JSONDecodeError:
                        logging.error("Cant decode")
                    return answer
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

    def _generate_missing_params_prompt(self, required_fields: Dict) -> str:
        """
        Генерирует строку с описанием недостающих параметров на основе извлеченного контента.

        Args:
            required_fields: Список обязательных полей и их описаний

        Returns:
            Строка с форматированным списком параметров для заполнения
        """

        prompt_lines = ["Список необходимых параметров:"]
        for field, desc in required_fields.items():
            prompt_lines.append(f"- Поле: {field}")
            prompt_lines.append(f"  Описание: {desc}")

        return "\n".join(prompt_lines)

    def get_required_fields(self, schema: str) -> str:
        prompt = "Вот пример, как нужно выписать переменные."
        example = """type (обязательно) — тип Workflow (WF), например: complex, await_for_message, rest_call и др.
name (обязательно) — уникальное имя WF.
tenantId (опционально) — идентификатор системы, использующей WF.
version (опционально) — номер версии WF.
description (опционально) — короткое описание функциональности WF.
compiled (обязательно, если type равен 'complex')
start (обязательно) — уникальный идентификатор начальной активности (activity) в составе сложного WF.
activities (обязательно) — массив структурированных действий (активностей), выполняемых в рамках WF.
outputTemplate (опционально) — шаблон фильтрации выходных данных.
details (обязательно, если type не равен 'complex')*
inputValidateSchema (опционально) — JSON-схема для валидации входных данных.
outputValidateSchema (опционально) — JSON-схема для валидации выходных данных.
starters (обязательно) — параметры для инициирования выполнения WF.
sendToKafkaConfig (обязательно, если type равен 'send_to_kafka') — конфигурационные данные для интеграции с Apache Kafka.
sendToS3Config (обязательно, если type равен 'send_to_s3') — конфигурационные данные для взаимодействия с Amazon S3.
restCallConfig (обязательно, если type равен 'rest_call') — конфигурация для REST-запросов.
xsltTransformConfig (обязательно, если type равен 'xslt_transform') — конфигурация для трансформации XML/XSLT.
databaseCallConfig (обязательно, если type равен 'db_call') — конфигурация SQL-запросов к базам данных.
sendToRabbitmqConfig (обязательно, если type равен 'send_to_rabbitmq') — конфигурация для отправки сообщений в RabbitMQ.
awaitForMessageConfig (обязательно, если type равен 'await_for_message') — конфигурация ожиданий входящих сообщений.
sendToSapConfig (обязательно, если type равен 'send_to_sap') — конфигурация интеграционных соединений с системой SAP.
flowEditorConfig (опционально) — вспомогательная информация, предназначенная исключительно для визуального редактора и не оказывающая влияния на исполнение самого workflow."""
        prompt = (
            prompt + example + ". Тебе нужно из Json файла в таком же формате выписать"
            "все поля, которые отмечены required как обязательные вместе с их описанием. Json: "
            + schema
        )
        return self._generate_with_retry(
            prompt,
            system_prompt="Ты специалист по json схемам.",
            model=self.model_name,
        )

    def another_get_required_fields(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """
        Recursively extract all required fields from a JSON schema.

        Args:
            schema (Dict[str, Any]): The JSON schema containing definitions with nested parameters and subcomponents.

        Returns:
            Dict[str, str]: A mapping where keys are dot-separated paths to required fields,
                            and values are their descriptions.
        """
        logging.info("Starting extraction of required fields")
        required_fields: Dict[str, str] = {}

        def traverse(node: Any, path: List[str]):
            logging.debug(
                "Traversing path %s with node type %s", path, type(node).__name__
            )
            # Only process dictionaries
            if not isinstance(node, dict):
                logging.debug("Skipping non-dict node at %s: %r", path, node)
                return

            # Validate required and description
            if "required" in node and "description" in node:
                if node.get("required") is True:
                    field_path = ".".join(path)
                    required_fields[field_path] = node["description"]
                    logging.debug(
                        "Found required field: %s -> %s",
                        field_path,
                        node["description"],
                    )
                else:
                    logging.debug("Field at %s marked required=False", path)
            else:
                if "required" in node:
                    logging.warning("Node at %s missing description", path)
                if "description" in node:
                    logging.warning("Node at %s missing required flag", path)

            # Recurse into nested parameters and subcomponents
            for child_key in ("parameters", "subcomponents"):
                if child_key in node:
                    child_group = node[child_key]
                    if isinstance(child_group, dict):
                        logging.debug("Descending into '%s' at %s", child_key, path)
                        for name, child_node in child_group.items():
                            traverse(child_node, path + [name])
                    else:
                        logging.warning(
                            "Expected dict for '%s' at %s but got %s",
                            child_key,
                            path,
                            type(child_group).__name__,
                        )

        # Validate top-level schema
        if not isinstance(schema, dict):
            logging.error("Schema root is not a dict: %r", schema)
            raise ValueError("Schema must be a dictionary of definitions.")

        # Iterate top-level definitions
        for entry_name, entry_def in schema.items():
            logging.debug(
                "Processing top-level entry: %s (type: %s)",
                entry_name,
                type(entry_def).__name__,
            )
            if not isinstance(entry_def, dict):
                logging.warning("Skipping entry '%s': not a dict", entry_name)
                continue
            params = entry_def.get("parameters")
            if not isinstance(params, dict):
                logging.warning(
                    "Entry '%s' has no 'parameters' dict or it is not a dict (type: %s)",
                    entry_name,
                    type(params).__name__,
                )
                continue
            for name, param_node in params.items():
                traverse(param_node, [entry_name, name])

        logging.info(
            "Extraction complete: found %d required fields", len(required_fields)
        )
        return required_fields
