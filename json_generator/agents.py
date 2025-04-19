import json
import logging
from typing import Any, Dict, List

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from .logging_config import configure_logging
from .model_info import custom_model_info
from .private_api import SECRET_TOKEN
from .retrieval import SimpleRetrievalAgent
from .sessions import SessionContext
from .utils import API_URL, MODEL_NAME

configure_logging()

# Инициализация LLM клиента
logging.debug("Инициализация OpenAIChatCompletionClient")
model_client = OpenAIChatCompletionClient(
    model=MODEL_NAME,
    api_key=SECRET_TOKEN,
    base_url=API_URL,
    model_info=custom_model_info,
)

# Инициализация ретривера
vector_store = None  # TODO: заменить реальным векторным хранилищем с методом search
retriever = SimpleRetrievalAgent(
    name="doc_retriever", vector_store=vector_store, top_k=5
)
logging.debug("SimpleRetrievalAgent инициализирован")

# Инициализация агентов
schema_agent = AssistantAgent(name="schema_generator", model_client=model_client)
clarification_agent = AssistantAgent(name="clarifier", model_client=model_client)
logging.info("Агенты schema_generator и clarifier готовы")


class ChatManager:
    def __init__(self):
        self.sessions: Dict[str, SessionContext] = {}
        logging.info("ChatManager создан")

    async def handle_message(self, session_id: str, message: str) -> str:
        logging.debug(f"handle_message: session_id={session_id}, message={message}")
        session = self.sessions.setdefault(session_id, SessionContext())
        session.update_with_user(message)

        # 1. Если ждём уточнения
        if session.awaiting_clarification:
            logging.info("Обработка уточнения от пользователя")
            # TODO: реализовать парсинг уточнения и обновление session.collected_params
            session.clear_missing()
            return await self._generate_schema(session)

        # 2. Проверяем недостающие параметры
        missing = self._detect_missing_params(session)
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
        docs: List[str] = (
            retriever.retrieve("wf/definition spec") if vector_store else []
        )
        logging.debug(f"Retrieved docs: {docs}")
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

    def _detect_missing_params(self, session: SessionContext) -> List[str]:
        required = ["url", "method", "authentication"]
        missing = [f for f in required if f not in session.collected_params]
        logging.debug(f"_detect_missing_params returned: {missing}")
        return missing

    def _extract_content(self, task_result: Any) -> str:
        """
        Извлекает текстовое содержание из TaskResult: ищет последнее TextMessage.
        """
        for msg in reversed(task_result.messages):
            if isinstance(msg, TextMessage) and msg.content:
                return msg.content
        logging.warning(
            "Не найден TextMessage в TaskResult, возвращаем str(task_result)"
        )
        return str(task_result)
