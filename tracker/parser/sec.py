# SEC Webpage Parser Class File

from abc import abstractmethod

import requests

from tracker.parser import WebpageParser, ResponseError


class SECParser(WebpageParser):
    """
    SEC Webpage Parser Class.
    Base class for other SEC Webpage Parser Classes.
    """

    def __init__(self, name: str, url: str = None):
        """
        SEC Webpage Parser Class Constructor
        """

        super().__init__(name=name, url=url)

        # TODO: Add logging

    def set_url(self, url: str) -> None:
        """
        Set the Parser URL

        :param url: New Parser URL
        """

        # Delete the previous cached webpage HTML text
        if url != self.url:
            self.response = None
            self.webpage = None
            self.content_type = None
            self.soup = None

            # Update url
            self.url = url

    def get_webpage(self, *args, **kwargs) -> str:
        """
        Get the webpage HTML text

        :return: Webpage HTML text

        Notes
        -----
        This method caches the webpage HTML texts in self.webpage.
        Uses Chrome User-Agent header.
        """

        # TODO: Add Rate Limiting

        # User-Agent is required to access SEC website. Use the latest Chrome on Windows 10 User Agent.
        # Otherwise, it will return 'Your Request Originates from an Undeclared Automated Tool' and no data.
        headers = self.header_chrome_user_agent

        response = requests.get(self.url, headers=headers)

        # Cache Response
        self.response = response

        # Get the content type of the response
        self.content_type = response.headers['Content-Type']

        # Check if response is successful
        if response.status_code != 200:
            raise ResponseError(f'Response Error: {response.status_code} - {response.reason}')

        self.webpage = response.text

        return response.text

    @abstractmethod
    def parse(self, *args, **kwargs):
        """
        Parse the webpage HTML text
        """
