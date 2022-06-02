# SEC Filings Parser

from datetime import datetime
from xml.etree import ElementTree

import pandas as pd
import requests
from lxml import etree

from baseurls import SEC_LATEST_FILINGS_URL
from src.parsers.WebpageParser import WebpageParser, ResponseError


class SECFilingsParser(WebpageParser):
    def __init__(self, name: str, url: str = None):
        """
        SEC Filings Parser Class Constructor

        :param name: Parser Name
        :param url: Parser URL
        """

        super().__init__(name, url)

        # Use the latest SEC Filings URL from baseurls.py to get the latest SEC Filings
        if url is None:
            self.url = SEC_LATEST_FILINGS_URL

            # TODO: Add logging
            print(f'{self.name} URL is not set. Using default URL: {self.url}')

        self.filings: pd.DataFrame = pd.DataFrame()

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

        # Get the content type of the response
        self.content_type = response.headers['Content-Type']

        # Check if response is successful
        if response.status_code != 200:
            raise ResponseError(f'Response Error: {response.status_code} - {response.reason}')

        self.webpage = response.text

        return response.text

    def parse(self) -> pd.DataFrame:
        """
        Parse the SEC Filings into DataFrame

        :return: Filings DataFrame
        """

        # Initialize DataFrame
        filing_cols = ['acc', 'type', 'title', 'date_time', 'link']
        filings = pd.DataFrame(columns=filing_cols)

        data: ElementTree = etree.fromstring(self.get_webpage().encode('utf-8'))

        # Iterate through entries
        entries = data.findall('{http://www.w3.org/2005/Atom}entry')

        for entry in entries:
            namespaces = {'atom': 'http://www.w3.org/2005/Atom'}

            # Get filing title
            title = entry.xpath('atom:title/text()', namespaces=namespaces)[0]

            # Get filing documents link
            link = entry.xpath('atom:link/@href', namespaces=namespaces)[0]

            # Summary
            # entry.xpath('atom:summary/text()', namespaces=namespaces)[0]

            # Get Filing Date Time
            date_time = datetime.strptime(entry.xpath('atom:updated/text()', namespaces=namespaces)[0][:-6],
                                          '%Y-%m-%dT%H:%M:%S')

            # Get form type
            form_type = entry.xpath('atom:category/@term', namespaces=namespaces)[0]

            # Get Accession Number
            acc_no = entry.xpath('atom:id/text()', namespaces=namespaces)[0].split('=')[-1]

            # Update DataFrame
            filings = pd.concat([filings, pd.DataFrame({'acc': [acc_no], 'type': [form_type], 'title': [title],
                                                        'date_time': [date_time], 'link': [link]})])

        # Set acc as index
        filings.set_index('acc', inplace=True)

        # Cache the filings DataFrame
        self.filings = filings

        return filings
