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

        # Chrome User-Agent header
        self.header_chrome_user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                                                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                       'Chrome/102.0.5005.63 Safari/537.36 '}

        # Caches
        self.response: requests.Response | None = None  # Response object
        self.webpage: str | None = None  # Webpage HTML text (requests.get.text)
        self.content_type: str | None = None  # requests.get.headers['Content-Type']
        self.soup: bs | None = None  # BeautifulSoup object of webpage

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

        # Cache the response object
        self.response = response

        # Get the content type of the response
        self.content_type = response.headers['Content-Type']

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
