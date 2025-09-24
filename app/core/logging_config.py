import logging
import os
import sys
from loguru import logger
from app.core.config import settings

# --- КОД ПЕРЕХВАТЧИКА (добавьте этот класс) ---
class InterceptHandler(logging.Handler):
    """
    Класс-обработчик, который перехватывает сообщения из стандартного logging
    и направляет их в loguru.
    """
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
# --- КОНЕЦ КОДА ПЕРЕХВАТЧИКА ---


def setup_logger():
    """
    Настраивает и конфигурирует логгер loguru для нашего проекта.
    """
    log_level = (settings.log_level or "INFO").upper()
    # 1. Удаляем стандартный обработчик, чтобы избежать дублирования логов
    logger.remove()

    # 2. Добавляем новый обработчик для красивого вывода в консоль
    #    - Уровень: INFO и выше (чтобы не загромождать консоль)
    #    - Цветной вывод: colorize=True
    #    - Понятный формат: показывает время, уровень, имя файла и сообщение
    logger.add(
        sys.stderr,  # Вывод в консоль
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    )

    # 3. Добавляем обработчик для записи всех сообщений в файл
    #    - Уровень: DEBUG и выше (для полной информации при отладке)
    #    - Автоматическая ротация: новый файл каждые 10 MB
    #    - Сжатие старых логов в zip-архивы
    try:
        os.makedirs("logs", exist_ok=True)
        logger.add(
            "logs/debug.log",  # Путь к файлу логов
            level=log_level,
            rotation="10 MB",
            compression="zip",
            enqueue=True,      # Делает запись асинхронной и безопасной для потоков
            format="{time} {level} {message}",
        )
    except Exception:
        # Если не удалось создать файл/директорию логов — продолжаем только с консольным выводом
        pass

    # Перехватываем стандартный logging и популярные логгеры веб-стека в loguru
    if getattr(settings, "intercept_handler_logging", True):
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
        for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "gunicorn", "gunicorn.error", "gunicorn.access", "sqlalchemy"):
            logger_ = logging.getLogger(name)
            logger_.handlers = [InterceptHandler()]
            logger_.propagate = True

    logger.info("✅ Логгер Loguru успешно настроен!")
    return logger

"""Экспортируемый логгер проекта (инициализируется при импортировании модуля)."""
logger = setup_logger()