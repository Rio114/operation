from logging import INFO, FileHandler, Formatter, StreamHandler, getLogger


def get_module_logger(modname):
    logger = getLogger(modname)
    if not logger.hasHandlers():
        logger_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        handler = StreamHandler()
        handler.setFormatter(Formatter(logger_format))
        logger.addHandler(handler)
        logger.setLevel(INFO)

        file_handler = FileHandler("ichimoku_trade.log", "a")
        file_handler.setLevel(INFO)
        file_handler.setFormatter(Formatter(logger_format))
        logger.addHandler(file_handler)
    return logger
