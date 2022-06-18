# Webpage Parser Parent Class File

import logging
import uuid
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup as bs

from defs import LOG_DIR_PATH
from tracker.utils import Logger

# Define logger
WebpageLogger = Logger('webpage')
logger = WebpageLogger.get_logger()


class WebpageParser:
    """
    Webpage Parser Class
    """

    def __init__(self, name: str, url: str):
        """
        Form Parser Parent Class Constructor

        :param name: Form Name
        :param url: Form URL
        """

        self.name: str = name
        self.url: str = url

        # Logging
        self.logger: logging.Logger = logger

        # Chrome User-Agent header
        self.chrome_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                                 'Chrome/102.0.5005.63 Safari/537.36'
        self.header_chrome_user_agent = {'User-Agent': self.chrome_user_agent}

        # Caches
        self.response: requests.Response | None = None  # Response object
        self.response_dt: datetime | None = None  # Response datetime
        self.webpage: str | None = None  # Webpage HTML text (requests.get.text)
        self.content_type: str | None = None  # requests.get.headers['Content-Type']
        self.soup: bs | None = None  # BeautifulSoup object of webpage

    def __repr__(self) -> str:
        """
        :return: Form Parser Parent Class Representation
        """

        return f'{self.name} Parser for {self.url}.'

    def get_webpage(self, headers: dict = None) -> str:
        """
        Get the webpage HTML text

        :param headers: HTTP header
        :return: Webpage HTML text

        Notes
        -----
        This method caches the webpage HTML texts in self.webpage.
        """

        # Default headers
        headers = {} if headers is None else headers

        # Get the webpage HTML text
        self.logger.debug(f'Getting {self.name} webpage from {self.url}')
        response = requests.get(self.url, headers=headers)

        # Cache the response object
        self.response = response
        self.response_dt = datetime.now()

        # Get the content type of the response
        self.content_type = response.headers['Content-Type']

        # Check if response is successful
        if response.status_code != 200:
            error_msg = f'Response Error: {response.status_code} - {response.reason}'
            self.logger.error(error_msg)
            raise ResponseError(message=error_msg, response=response)

        self.webpage = response.text
        return response.text

    def get_soup(self) -> bs:
        """
        Get the BeautifulSoup object of the webpage HTML text

        :return: BeautifulSoup object of webpage HTML text

        Notes
        -----
        This method caches the BeautifulSoup object in self.soup.
        """

        # Check if webpage HTML text is cached. If not, get webpage first.
        if self.webpage is None:
            self.get_webpage()

        # User appropriate parser. Default is lxml.
        parser = 'xml' if 'xml' in self.content_type else 'lxml'

        # Parse the webpage contents
        self.soup = bs(self.webpage, parser)

        return self.soup


class ResponseError(Exception):
    """
    Response Error
    """

    def __init__(self, message: str,
                 status_code: int = None,
                 response: requests.Response | None = None,
                 logger: logging.Logger | None = None):
        """
        Response Error Constructor

        :param message: Response Error Message to Log
        :param status_code (optional): Status Code of the Response
        :param response (optional): Log the response to file if provided
        :param logger (optional): Logger to log messages to
        """

        self.message = message
        self.status_code = status_code
        self.response: requests.Response | None = response
        self.content: response.text | None = response.text if response is not None else None

        self.logger: logging.Logger = logger

        # Save response to file
        if self.response is not None:
            # Generate random file name hash
            resp_file: Path = LOG_DIR_PATH.joinpath("response", f"{uuid.uuid4().hex}.txt")

            try:
                # Create file
                LOG_DIR_PATH.joinpath("response").mkdir(parents=True, exist_ok=True)
                resp_file.touch()

                # Save to file
                with open(resp_file, 'w') as file_obj:
                    file_obj.write(self.content)

                # Add file_name to message
                message += f". Saved to file {resp_file.name}."

            except Exception as err:
                self.logger.error(f"Error: {err}. Failed to save {message} to file: {resp_file.name}.")

        # Call super
        super().__init__(message)
