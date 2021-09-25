from os import path
from logging.handlers import RotatingFileHandler
from logging import DEBUG as LogDebug, Formatter as LogFormatter


def register_logger(app, filename):
    filepath = path.join("logs", filename)
    logs_formatter = LogFormatter("%(asctime)s|#|%(message)s")
    logs_handler = RotatingFileHandler(filepath, maxBytes=1048576, backupCount=5)
    logs_handler.setLevel(LogDebug)
    logs_handler.setFormatter(logs_formatter)
    app.logger.addHandler(logs_handler)
    app.logger.setLevel(LogDebug)
