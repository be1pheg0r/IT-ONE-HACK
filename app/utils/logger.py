import logging


def setup_logger(logger_name: str, level: int = logging.DEBUG) -> logging.Logger:

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(level)

        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        logger.addHandler(ch)

    return logger