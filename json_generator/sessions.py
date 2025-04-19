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
        self.messages.append(message)

    def set_missing(self, fields: List[str]):
        self.missing_fields = fields
        self.awaiting_clarification = bool(fields)

    def clear_missing(self):
        self.missing_fields = []
        self.awaiting_clarification = False

    def set_schema(self, schema: dict):
        self.current_schema = schema
