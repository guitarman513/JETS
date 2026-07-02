import logging
import sys

logger = logging.getLogger("JETS")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-7s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s"
)

handler.setFormatter(formatter)

logger.addHandler(handler)