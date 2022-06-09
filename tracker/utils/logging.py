# Logging Class File

import logging
import sys
from pathlib import Path

from defs import LOG_DIR_PATH

loggers: dict[str, logging.Logger] = dict()


class Logger:
    """
    Custom Logging Class
    """

    def __init__(self,
                 name: str,
                 file_handler: bool = True,
                 stream_handler: bool = True,
                 level: int = logging.DEBUG) -> None:
        """
        Logger Class Constructor

        :param name: Logger name
        :param file_handler: Add File Handler
        :param stream_handler: Add Stream Handler
        :param level: Logging level
        """

        # Params
        self.name: str = name
        self.add_file_handler: bool = file_handler
        self.add_stream_handler: bool = stream_handler
        self.level: int = level

        # Get root name if name is child
        self.root_name = self.name.split('.')[0]

        # Define log filename path
        self.filename: Path = LOG_DIR_PATH.joinpath(f"{self.root_name}.log")
        self.__create_log_file()

        # Define Format
        self.format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self.formatter: logging.Formatter = logging.Formatter(self.format)

        # Get logger
        self._logger: logging.Logger = self.get_logger()

    def get_logger(self) -> logging.Logger:
        """
        Get the logger
        """

        # Check if logger already exists
        if self.name in loggers:
            logger = loggers[self.name]
            logger.info(f"Getting logger: {self.name}")

        # Create logger
        else:
            logger = self.__create_logger()
            logger.info(f"Creating logger: {self.name}")

            # Cache logger
            loggers[self.name] = logger
            logger.info(f"Caching logger: {self.name}")

        return logger

    def set_level(self, level: int) -> int:
        """
        Set Logger Level

        :param level: Logging Level
        :return: Logging Level
        """

        self.level = level
        self._logger.setLevel(self.level)
        self._logger.info(f"Setting logger level: {self.level}")

        return self._logger.level

    def __create_logger(self) -> logging.Logger:
        """
        Create the logger and add handlers
        """

        # Create logger
        logger = logging.getLogger(self.name)

        # Do not propagate to root logger
        logger.propagate = False

        # Define logger level
        logger.setLevel(self.level)

        # Add File and Stream Handlers
        self.__add_handlers(logger)

        return logger

    def __add_handlers(self, logger: logging.Logger) -> None:
        """
        Add File and Stream Handlers

        :param logger: Logger object
        :return None
        """

        # Get all handlers already added to logger
        _file_handlers = [handler for handler in logger.handlers if isinstance(handler, logging.FileHandler)]
        _stream_handlers = [handler for handler in logger.handlers if isinstance(handler, logging.StreamHandler)]

        # Add File Handler if not already added and requested
        if self.add_file_handler and len(_file_handlers) == 0:
            logger.addHandler(self.__create_file_handler())

        # Add Stream Handler if not already added and requested
        if self.add_stream_handler and len(_stream_handlers) == 0:
            logger.addHandler(self.__create_stream_handler())

    def __create_file_handler(self) -> logging.FileHandler:
        """
        Create File Handler

        :return: File Handler Object
        """

        file_handler = logging.FileHandler(filename=self.filename)
        file_handler.setLevel(self.level)
        file_handler.setFormatter(self.formatter)

        return file_handler

    def __create_stream_handler(self) -> logging.StreamHandler:
        """
        Create Stream Handler

        :return: Stream Handler Object
        """

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(self.level)
        stream_handler.setFormatter(self.formatter)

        return stream_handler

    def __create_log_file(self) -> None:
        """
        Create Log File
        """

        # Check if logs directory exists
        if not LOG_DIR_PATH.exists():
            LOG_DIR_PATH.mkdir()

        # Check if log file exists
        if not self.filename.exists():
            self.filename.touch()
