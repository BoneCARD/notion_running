import logging
from logging.handlers import RotatingFileHandler


class Logger:
    """
    Custom logger: all logs will be sent to the logs directory
    """
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level=logging.DEBUG)
        self.logger.propagate = False

        # 设置输出格式
        output_format = logging.Formatter("%(asctime)s - %(filename)s[%(lineno)d] - %(thread)d - %(levelname)s - %(name)s: %(message)s")

        # 设置控制台输出 handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level=logging.INFO)
        stream_handler.setFormatter(output_format)

        file_handler = RotatingFileHandler('%s/%s.log' % ('logs', name), encoding="utf-8", maxBytes=104857600, backupCount=10)
        file_handler.setLevel(level=logging.INFO)
        file_handler.setFormatter(output_format)

        # 添加 handler
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)
