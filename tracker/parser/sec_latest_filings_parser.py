# SEC Latest Filings Parser
# https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent

from datetime import datetime
from xml.etree import ElementTree

import pandas as pd
import requests
from lxml import etree

from baseurls import SEC_LATEST_FILINGS
from tracker.parser import SECParser, ResponseError


class SECFilingsParser(SECParser):
    """
    SEC Latest Filings Parser Class
    """

    def __init__(self, name: str, url: str = None):
        """
        SEC Filings Parser Class Constructor

        :param name: Parser Name
        :param url: Parser URL
        """

        super().__init__(name, url)

        # Use the latest SEC Filings URL from baseurls.py to get the latest SEC Filings
        if url is None:
            self.url = SEC_LATEST_FILINGS

            # TODO: Add logging
            print(f'{self.name} URL is not set. Using default URL: {self.url}')

        self.filings: pd.DataFrame = pd.DataFrame()

    def parse(self) -> pd.DataFrame:
        """
        Parse the SEC Filings into DataFrame

        :return: Filings DataFrame
        """

        # Initialize DataFrame
        filing_cols = ['acc', 'form_type', 'title', 'date_time', 'link']
        filings = pd.DataFrame(columns=filing_cols)

        # Check if webpage HTML text is cached. If not, get webpage first.
        if self.webpage is None:
            self.get_webpage()

        data: ElementTree = etree.fromstring(self.webpage.encode('utf-8'))

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
            filings = pd.concat([filings, pd.DataFrame({'acc': [acc_no], 'form_type': [form_type], 'title': [title],
                                                        'date_time': [date_time], 'link': [link]})])

        # Set acc as index
        filings.set_index('acc', inplace=True)

        # Cache the filings DataFrame
        self.filings = filings

        return filings
