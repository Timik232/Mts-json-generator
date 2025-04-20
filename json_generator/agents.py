"""Файл с реализацией системы агентов для работы программы"""
import json
import logging
from typing import Annotated, Dict

from autogen import ConversableAgent, GroupChat, GroupChatManager
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from .constants import (
    API_URL,
    CLARIFIER_DESCRIPTION,
    CLARIFIER_TASK,
    CLARIFY_JSON_TASK,
    JSON_DESCRIPTION,
    MODEL_NAME,
    SYSTEM_CLARIFIER,
    SYSTEM_JSON_CREATOR,
)
from .logging_config import configure_logging
from .model_info import custom_model_info
from .private_api import SECRET_TOKEN
from .retrieval import SimpleRetrievalAgent
from .sessions import SessionContext
from .utils import ClarifierSchema, generate

configure_logging()


def get_assistant_text(response):
    """Получить текстовое сообщение от ассистента из ответа."""
    messages, _ = response
    return next((msg.content for msg in messages if msg.source == "assistant"), None)


# Инициализация LLM клиента
logging.debug("Инициализация OpenAIChatCompletionClient")


# Инициализация ретривера
vector_store = None  # TODO: заменить реальным векторным хранилищем с методом search
retriever = SimpleRetrievalAgent(
    name="doc_retriever", vector_store=vector_store, top_k=5
)
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
# register_function(
#     docs,
#     caller=clarification_agent,  # The assistant agent can suggest calls to the calculator.
#     executor=user_proxy,  # The user proxy agent can execute the calculator calls.
#     name="docs",  # By default, the function name is used as the tool name.
#     description="RAG retriever для поиска документации",  # A description of the tool.
# )
logging.info("Агенты schema_generator и clarifier готовы")


@user_proxy.register_for_execution()
@clarification_agent.register_for_llm(description="Получить документацию")
def retrieve_documents(
    query: Annotated[
        str,
        "Запрос к RAG системе для получения документации с указанием"
        "необходимой темы",
    ],
) -> str:
    return "Документы: для rest нужен параметр endpoint и surname"


group_chat = GroupChat(
    agents=[user_proxy, clarification_agent], messages=[], max_round=2
)
manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)


class ChatManager:
    """Менеджер чата, осуществляющий управление"""

    def __init__(self):
        self.sessions: Dict[str, SessionContext] = {}
        logging.info("ChatManager создан")

    async def handle_message(self, session_id: str, message: str) -> str:
        session = self.sessions.setdefault(session_id, SessionContext())
        session.update_with_user(message)
        print(1)
        result = await self._detect_missing_params(session)
        print(result)

    async def deprecated_handle_message(self, session_id: str, message: str) -> str:
        logging.debug(f"handle_message: session_id={session_id}, message={message}")
        session = self.sessions.setdefault(session_id, SessionContext())
        session.update_with_user(message)
        if len(session) == 1:
            bd_context = await self._retrieve(message)
            session.update_with_bd_context(bd_context)
            task_result = await self._detect_missing_params(bd_context, session)
            generated = self._extract_content(task_result)
            print(generated)
            return "1"
        # 1. Если ждём уточнения
        if session.awaiting_clarification:
            logging.info("Обработка уточнения от пользователя")
            # TODO: реализовать парсинг уточнения и обновление session.collected_params
            session.clear_missing()
            return await self._generate_schema(session)

        # 2. Проверяем недостающие параметры
        missing = self._detect_missing_params(message, session)
        if missing:
            session.set_missing(missing)
            prompt = (
                f"Пожалуйста, уточните следующие поля для схемы: {', '.join(missing)}."
            )
            logging.info(f"Недостающие поля: {missing}")
            task_result = await clarification_agent.run(task=prompt)
            content = self._extract_content(task_result)
            logging.debug(f"ClarificationAgent ответил: {content}")
            return content

        # 3. Генерация схемы
        if session.current_schema is None:
            logging.info("Генерация новой схемы")
            return await self._generate_schema(session)

        # 4. Модификация
        logging.info("Модификация существующей схемы")
        prompt = (
            f"Измени текущую JSON-схему: {json.dumps(session.current_schema)} "
            f"в соответствии с: {message}"
        )
        task_result = await schema_agent.run(task=prompt)
        updated = self._extract_content(task_result)
        logging.debug(f"SchemaAgent ответил: {updated}")
        try:
            session.set_schema(json.loads(updated))
            logging.info("Схема успешно обновлена в контексте сессии")
        except json.JSONDecodeError:
            logging.error("Не удалось распарсить ответ SchemaAgent как JSON")
        return updated

    async def _generate_schema(self, session: SessionContext) -> str:
        logging.info("Выполняется _generate_schema")
        # docs: List[str] = (
        #     retriever.retrieve("wf/definition spec") if vector_store else []
        # )
        # logging.debug(f"Retrieved docs: {docs}")
        docs = session.bd_context
        params = session.collected_params
        prompt = (
            "На основе следующих документов:\n"
            f"{docs}\n"
            "и параметров: "
            + json.dumps(params)
            + " сформируй JSON-схему definition.json для интеграции."
        )
        task_result = await schema_agent.run(task=prompt)
        generated = self._extract_content(task_result)
        logging.debug(f"Generated schema: {generated}")
        try:
            session.set_schema(json.loads(generated))
            logging.info("Схема сохранена в контексте сессии")
        except json.JSONDecodeError:
            logging.error("Ответ агента не является валидным JSON")
        return generated

    async def _retrieve(self, message: str) -> str:
        logging.info("Выполняется _retrieve")
        # task_result = await retriever.run(task=message)
        task_result = "Документация, json схема"
        logging.debug(f"Retrieved docs: {task_result}")
        return task_result

    async def _detect_missing_params(self, session: SessionContext) -> str:
        history = session.get_messages()
        history.append(CLARIFIER_TASK)
        history = " ".join(history)
        print(history)
        chat_result = user_proxy.initiate_chat(
            clarification_agent,
            message=history,
            max_turns=2,
            summary_method="reflection_with_llm",
        )
        print(chat_result)
        chat_text = self._extract_content(chat_result)
        prompt = CLARIFY_JSON_TASK + chat_text
        json_answer = generate(
            prompt,
            system_prompt=SYSTEM_CLARIFIER,
            json_schema=ClarifierSchema.model_json_schema(),
        )
        return json_answer
        # return missing

    def _extract_content(self, task_result: TextMessage | dict | str) -> str:
        """
        Извлекает содержимое из сообщения ассистента
        """

        def _extract_content(self, task_result: TextMessage | dict | str) -> str:
            """
            Извлекает содержимое из сообщения ассистента
            """
            # Обработка строкового ввода
            if isinstance(task_result, str):
                return task_result.strip()

            content = ""
            chat_history = []

            # Извлечение chat_history из различных структур
            try:
                if hasattr(task_result, "chat_history"):
                    chat_history = getattr(task_result, "chat_history", [])
                elif isinstance(task_result, dict):
                    chat_history = task_result.get("chat_history", [])
            except Exception as e:
                logging.error(f"Error extracting chat history: {e}")

            # Поиск последнего сообщения ассистента с контентом
            for message in reversed(chat_history):
                if message.get("role") == "assistant":
                    # Берем первое непустое содержимое (даже если есть tool_calls)
                    content = message.get("content")
                    if content and content.strip().lower() != "none":
                        return content.strip()

            # Fallback: поиск в других структурах данных
            if isinstance(task_result, dict):
                # Проверка вложенных структур response/choices
                response = task_result.get("response", {})
                for choice in response.get("choices", []):
                    msg = choice.get("message", {})
                    if msg.get("role") == "assistant":
                        content = msg.get("content", "").strip()
                        if content and content != "None":
                            return content

                # Проверка прямого поля messages
                for message in task_result.get("messages", []):
                    if message.get("role") == "assistant":
                        content = message.get("content", "").strip()
                        if content:
                            return content

            # Проверка атрибута content у объекта
            if hasattr(task_result, "content"):
                content = getattr(task_result, "content", "")
                if content:
                    return content.strip()

            # Гарантированный возврат непустой строки
            return content.strip() if content else "No content found"
