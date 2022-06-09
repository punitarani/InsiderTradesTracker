# Webpage Parser Parent Class File

import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup as bs

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
        self.header_chrome_user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                                                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                       'Chrome/102.0.5005.63 Safari/537.36 '}

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
            raise ResponseError(error_msg)

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

    def __init__(self, message: str, status_code: int = None):
        """
        Response Error Constructor

        :param message: Response Error Message
        """

        self.message = message
        self.status_code = status_code
        super().__init__(message)
