# Webpage Parser Parent Class File

import requests
from bs4 import BeautifulSoup as bs


class WebpageParser:
    """
    Form Parser Parent Class
    """
    def __init__(self, name: str, url: str):
        """
        Form Parser Parent Class Constructor

        :param name: Form Name
        :param url: Form URL
        """

        self.name = name
        self.url = url

        # Caches
        self.webpage: str | None = None     # Webpage HTML text (requests.get.text)
        self.soup: bs | None = None         # BeautifulSoup object of webpage

    def __repr__(self) -> str:
        """
        :return: Form Parser Parent Class Representation
        """

        return f'{self.name} Parser for {self.url}.\n'

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
        response = requests.get(self.url, headers=headers)

        # Check if response is successful
        if response.status_code != 200:
            raise ResponseError(f'Response Error: {response.status_code} - {response.reason}')

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

        # Get website type: HTML or XML
        website_type = self.url.split('.')[-1]

        # User appropriate parser. Default is lxml.
        parser = 'xml' if website_type == 'xml' else 'lxml'

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
