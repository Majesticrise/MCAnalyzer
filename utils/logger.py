import logging
import sys

def setup_logger(level="INFO"):
    logger = logging.getLogger("MCAnalyzer")
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(level)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s", datefmt="%H:%M:%S")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger