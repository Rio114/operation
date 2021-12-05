from logging import DEBUG, INFO, FileHandler, Formatter, StreamHandler, getLogger

from app.config import Config


def get_module_logger(modname):
    config = Config()
    logger = getLogger(modname)
    logger_level = DEBUG
    if not logger.hasHandlers():
        logger_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        handler = StreamHandler()
        handler.setFormatter(Formatter(logger_format))
        logger.addHandler(handler)
        logger.setLevel(logger_level)

        file_handler = FileHandler(config.LOGFILE, "a")
        file_handler.setLevel(logger_level)
        file_handler.setFormatter(Formatter(logger_format))
        logger.addHandler(file_handler)

    return logger
