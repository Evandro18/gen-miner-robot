# Create simple logger for the module
import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
import os
import sys

from src.infra.core.config import Envs

_logger_cache: dict[str, Logger] = {}

LOGGER_FILE = 'logs/logs.log'

def initialize_logger(logger_name: str):
    global _logger_cache
    logger = None
    if logger_name in _logger_cache.keys():
        return _logger_cache[logger_name]
    
    formatter = logging.Formatter('{"time": "%(asctime)s", "filename": "%(filename)s", "funcName": "%(funcName)s", "levelname": "%(levelname)s", "message": "%(message)s"}')
    logger_file_max_bytes = 5 * 1024 * 1024
    logger_file_backup_count = 5
    
    directory = os.path.dirname(os.path.abspath(path=str(LOGGER_FILE)))
    if not os.path.exists(directory):
        os.mkdir(directory)
    
    original_factory = logging.getLogRecordFactory()
    
    def record_factory(*args, **kwargs):
        record = original_factory(*args, **kwargs)
        record.funcName = record.funcName
        record.filename = record.filename
        return record
    
    logging.setLogRecordFactory(record_factory)
    
    file_handler = RotatingFileHandler(
        filename=os.path.abspath(path=str(LOGGER_FILE)),
        maxBytes=logger_file_max_bytes,
        backupCount=logger_file_backup_count,
        mode='a',
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    
    if Envs.FASTAPI_DEBUG:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    _logger_cache[logger_name] = logger
    return logger

Log = initialize_logger(__name__)
