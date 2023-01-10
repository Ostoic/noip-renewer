"""Logging module"""

import logging
import loguru

logging.basicConfig(level="INFO")


def configure_log(logger):
    logger.configure()


configure_log(loguru.logger)
