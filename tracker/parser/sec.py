# SEC Webpage Parser Class File

import logging
from datetime import datetime

import requests

import config
from tracker.parser import WebpageParser, ResponseError
from tracker.utils import RateLimit, Logger

# Define logger
SECLogger: Logger = Logger('sec')
logger: logging.Logger = SECLogger.get_logger()


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

        self.logger = logger

    def set_url(self, url: str) -> None:
        """
        Set the Parser URL

        :param url: New Parser URL
        """

        # Delete the previous cached webpage HTML text
        if url != self.url:
            self.response = None
            self.response_dt = None
            self.webpage = None
            self.content_type = None
            self.soup = None

            # Update url
            self.url = url

    def _get_user_agent(self) -> str:
        """
        User-Agent is required to access SEC website.
        Otherwise, it will return 'Your Request Originates from an Undeclared Automated Tool' and no data.
        1. Try to use recommended header: 'Sample Company Name AdminContact@<sample company domain>.com'
        2. If missing data from config file, mock Chrome web browser header.

        :return: User-Agent for header
        """

        # Check if required config values are available.
        if config.NAME is not None and config.EMAIL is not None:
            return f'{config.NAME} {config.EMAIL}'

        # If missing config values, use Chrome user agent (NOT RECOMMENDED).
        else:
            return self.chrome_user_agent

    @RateLimit(limit=10, period=1, max_wait=15, logger=logger)
    def get_webpage(self, *args, **kwargs) -> str:
        """
        Get the webpage HTML text

        :return: Webpage HTML text

        Notes
        -----
        This method caches the webpage HTML texts in self.webpage.
        Follows guidelines: https://www.sec.gov/os/accessing-edgar-data.
        """

        """      
        Notes:
            User-Agent: Sample Company Name AdminContact@<sample company domain>.com
            Accept-Encoding: gzip, deflate
            Host: www.sec.gov
        """
        headers: dict = {
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov',
            'User-Agent': self._get_user_agent()
        }

        # Get the webpage HTML text
        self.logger.debug(f'Getting {self.name} webpage from {self.url}')
        response = requests.get(self.url, headers=headers)

        # Cache Response
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
