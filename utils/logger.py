import logging
import sys

logger_name = 'DAG_worker'
formatter = logging.Formatter(
    '[%(asctime)s] %(name)s [%(levelname)s] [%(processName)s (PID: %(process)s)]' +
    ' {%(filename)s:%(lineno)d:%(funcName)s} - %(message)s')


def get_file_handler(logfile='./logs/app.log', debug=False):
    from logging.handlers import RotatingFileHandler

    handler = RotatingFileHandler(logfile, maxBytes=104857600, backupCount=10)
    handler.setLevel(logging.DEBUG if debug else logging.INFO)
    handler.setFormatter(formatter)

    return handler


def get_std_handler(debug=True):
    from logging import StreamHandler

    handler = StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if debug else logging.INFO)
    handler.setFormatter(formatter)

    return handler


def get_logger(handler):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger


def get_file_logger(logfile='./logs/app.log', debug=False):
    return get_logger(get_file_handler(logfile=logfile, debug=debug))


def get_std_logger(debug=True):
    return get_logger(get_std_handler(debug=debug))


def get_local_logger(name):
    return logging.getLogger(logger_name + '.' + name)


def get_null_logger():
    return get_file_logger(logfile='/dev/null')

