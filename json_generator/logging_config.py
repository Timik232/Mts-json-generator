"""Файл для настройки ведения журнала с цветным выводом."""
import logging
from logging import Formatter, LogRecord, StreamHandler
from typing import Dict

LOG_COLORS: Dict[str, str] = {
    "DEBUG": "#4b8bf5",  # Light blue
    "INFO": "#2ecc71",  # Green
    "WARNING": "#f1c40f",  # Yellow
    "ERROR": "#e74c3c",  # Red
    "CRITICAL": "#8b0000",  # Dark red
}
RESET_COLOR = "\x1b[0m"


def hex_to_ansi(hex_color: str) -> str:
    """Конвертирует HEX-код цвета в ANSI escape-последовательность.

    Args:
        hex_color (str): HEX-код цвета в формате '#RRGGBB'

    Returns:
        str: ANSI escape-последовательность для цвета или пустая строка при ошибке
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return ""

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except ValueError:
        return ""

    return f"\x1b[38;2;{r};{g};{b}m"


class ColoredFormatter(Formatter):
    """Кастомный форматтер для добавления цветов в логи с помощью ANSI-кодов.
    Цвета определяются на основе уровня логирования в соответствии с LOG_COLORS."""

    def format(self, record: LogRecord) -> str:
        """Форматирует запись лога с добавлением цветовых кодов.

        Args:
            record (LogRecord): Запись лога для форматирования

        Returns:
            str: Отформатированное сообщение с цветовыми кодами
        """
        message = super().format(record)
        if isinstance(message, bytes):
            message = message.decode("utf-8", "replace")
        color_code = hex_to_ansi(LOG_COLORS.get(record.levelname, ""))
        return f"{color_code}{message}{RESET_COLOR}"


def configure_logging(level: int = logging.INFO) -> None:
    """Настраивает корневой логгер с обработчиком цветного вывода.

    Args:
        level (int): Уровень логирования (logging.INFO или logging.DEBUG).
            По умолчанию: logging.INFO.

    Raises:
        ValueError: Если указан недопустимый уровень логирования

    Примечание:
        Поддерживаются только уровни logging.INFO и logging.DEBUG
    """
    if level != logging.INFO and level != logging.DEBUG:
        raise ValueError("You can use only logging.INFO or logging.DEBUG")
    handler = StreamHandler()
    handler.setFormatter(
        ColoredFormatter(
            fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    )

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(handler)
