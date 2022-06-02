# SEC Filings Parser

import requests

from src.parsers.WebpageParser import WebpageParser, ResponseError


class SECFilingsParser(WebpageParser):
    def __init__(self, name: str, url: str):
        """
        SEC Filings Parser Class Constructor

        :param name: Parser Name
        :param url: Parser URL
        """

        super().__init__(name, url)

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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/102.0.5005.63 Safari/537.36 '
        }

        response = requests.get(self.url, headers=headers)

        # Check if response is successful
        if response.status_code != 200:
            raise ResponseError(f'Response Error: {response.status_code} - {response.reason}')

        self.webpage = response.text
        return response.text
