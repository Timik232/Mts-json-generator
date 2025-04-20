"""Файл с реализацией системы агентов для работы программы"""
import json
import logging
from typing import Annotated, Any, Dict

from autogen import Cache, ConversableAgent, GroupChat, GroupChatManager
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
# register_function(
#     docs,
#     caller=clarification_agent,  # The assistant agent can suggest calls to the calculator.
#     executor=user_proxy,  # The user proxy agent can execute the calculator calls.
#     name="docs",  # By default, the function name is used as the tool name.
#     description="RAG retriever для поиска документации",  # A description of the tool.
# )


@user_proxy.register_for_execution()
@clarification_agent.register_for_llm(description="Получить json-документацию")
def retrieve_documents(
    query: Annotated[
        str,
        "Запрос к RAG системе для получения документации с указанием"
        "необходимой темы",
    ],
) -> str:
    if isinstance(query, dict) and "query" in query:
        query = str(query["query"])
    query = str(query)
    answer = retriever.hybrid_search(query=query)
    docs = [doc["content"] for doc in answer]
    return "\n".join(docs)


group_chat = GroupChat(
    agents=[user_proxy, clarification_agent], messages=[], max_round=4
)
manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)
logging.info("Агенты schema_generator и clarifier готовы")


class ChatManager:
    """Менеджер чата, осуществляющий управление"""

    def __init__(self):
        self.sessions: Dict[str, SessionContext] = {}
        logging.info("ChatManager создан")
        self.model_name = "gemma-3-27b-it"

    async def handle_message(self, session_id: str, message: str) -> Dict[str, Any]:
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
        if not json_result["can_generate_schema"]:
            return {"message": json_result["message"], "json_schema": ""}
        else:
            try:
                answer = (
                    generate(
                        JSON_TASK + " ".join(session.get_messages()),
                        system_prompt=SYSTEM_JSON_CREATOR,
                        model=self.model_name,
                        json_schema=json.loads(session.bd_context),
                    ),
                )
            except Exception:
                logging.warning("Json schema не валидна")
                answer = generate(
                    JSON_TASK + " ".join(session.get_messages()),
                    system_prompt=SYSTEM_JSON_CREATOR,
                    model=self.model_name,
                )
            return {"message": "Полученная схема", "json_schema": answer}

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

    def _detect_missing_params(self, session: SessionContext) -> str:
        history = session.get_messages()
        history.append(CLARIFIER_TASK)
        history = " ".join(history)
        with Cache.disk() as cache:
            chat_result = user_proxy.initiate_chat(
                clarification_agent,
                message=history,
                max_turns=4,
                summary_method="reflection_with_llm",
                cache=cache,
            )

        chat_text = self._extract_content(chat_result)
        session.update_with_bd_context(self._extract_tool_responses(chat_result)[0])
        prompt = CLARIFY_JSON_TASK + chat_text
        raw_answer = generate(
            prompt,
            model=self.model_name,
            system_prompt=SYSTEM_CLARIFIER_WITHOUT_TERMINATE,
            json_schema=ClarifierSchema.model_json_schema(),
        )

        return raw_answer

    def _extract_summary(self, task_result: dict | Any) -> str:
        return task_result.summary

    def _extract_content(self, task_result: dict | Any) -> str:
        """
        Извлекает содержимое из сообщения ассистента
        """
        history = []

        for msg in task_result.chat_history:
            entry = []

            # Базовая информация
            role = msg.get("role", "unknown")
            name = msg.get("name", "unknown")
            content = msg.get("content")

            # Заголовок сообщения
            header = f"[{role.upper()}"
            if name and name != role:
                header += f" ({name})"
            header += "]"

            # Обработка разных типов сообщений
            if role == "assistant" and msg.get("tool_calls"):
                for call in msg["tool_calls"]:
                    func = call["function"]
                    entry.append(f"{header} CALL {func['name']}: {func['arguments']}")

            elif role == "tool" and msg.get("tool_responses"):
                for response in msg["tool_responses"]:
                    entry.append(f"{header} RESPONSE: {response['content']}")

            elif content:
                entry.append(f"{header}: {content.strip()}")

            if entry:
                history.extend(entry)

        return "\n".join(history)

    def _extract_tool_responses(self, chat_result: dict | Any) -> str:
        """Извлекает все ответы от инструментов (tool responses) из истории чата"""
        for msg in reversed(chat_result.chat_history):
            if msg.get("role") == "tool" and msg.get("tool_responses"):
                # Берем последний ответ из списка tool_responses
                last_response = msg["tool_responses"][-1]
                print("__________________")
                print(last_response["content"])
                return last_response["content"]
        return ""
