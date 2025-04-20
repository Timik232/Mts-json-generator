from typing import Dict, List, Optional


class SessionContext:
    """
    Хранит данные сессии: сообщения, собранные параметры, схема, состояние.
    """

    def __init__(self):
        self.messages: List[str] = []
        self.collected_params: Dict[str, any] = {}
        self.missing_fields: List[str] = []
        self.current_schema: Optional[dict] = None
        self.awaiting_clarification: bool = False

    def update_with_user(self, message: str):
        """Добавляет сообщение в сессию."""
        self.messages.append(message)

    def set_missing(self, fields: List[str]):
        """Устанавливает недостающие поля и состояние ожидания уточнения."""
        self.missing_fields = fields
        self.awaiting_clarification = bool(fields)

    def clear_missing(self):
        """Очищает недостающие поля и состояние ожидания уточнения."""
        self.missing_fields = []
        self.awaiting_clarification = False

    def set_schema(self, schema: dict):
        """Json-schema"""
        self.current_schema = schema

    def clear_session(self):
        """Очищает данные сессии."""
        self.messages.clear()
        self.collected_params.clear()
        self.missing_fields.clear()
        self.current_schema = None
        self.awaiting_clarification = False
