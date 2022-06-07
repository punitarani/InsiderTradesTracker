# SEC Filing Parser

import pandas as pd
import requests

from tracker.parser import WebpageParser, ResponseError


class SECFilingParser(WebpageParser):
    """
    SEC Filing Parser Class.
    """

    def __init__(self, name: str, url: str):
        """
        FilingParser Class Constructor.

        :param name: Name of the filing parser.
        :param url: URL of the SEC filing.
        """

        super().__init__(name, url)

        # Caches
        self.data: pd.DataFrame = pd.DataFrame()

    def get_webpage(self, *args, **kwargs) -> str:
        """
        Get the webpage HTML text

        :return: Webpage HTML text

        Notes
        -----
        This method caches the webpage HTML texts in self.webpage.
        Uses Chrome User-Agent header.
        """

        # User-Agent is required to access SEC website. Use the latest Chrome on Windows 10 User Agent.
        # Otherwise, it will return 'Your Request Originates from an Undeclared Automated Tool' and no data.
        headers = self.header_chrome_user_agent

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

        # Check if the soup is Cached. If not cached, get the soup before parsing
        if self.soup is None:
            self.get_soup()

        # Get table from soup
        table = self.soup.find('table', {'class': 'tableFile'})

        # Get document links from table
        links = table.find_all('a')

        # Parse document links
        links = ["https://www.sec.gov/" + link.get('href') for link in links]

        # Convert table to DataFrame
        df = pd.read_html(str(table))[0]

        # Add link column to DataFrame
        df['Link'] = links

        # Cache the data
        self.data = df

        return df

    def get_document_url(self, prefer_xml: bool = True) -> str | None:
        """
        Get the Document URL from webpage.

        :param prefer_xml: Prefer XML document over HTML document.
        :return: Document URL

        Notes:
        -----
        Default is to prefer XML document over HTML document.
        If XML document is not found, HTML document is returned.
        """

        # Check if the soup is Cached. If not cached, get the soup before parsing
        if self.soup is None:
            self.get_soup()

        # Get form from soup. Element is <div id="formName">
        form_data = self.soup.find('div', {'id': 'formName'}).text
        form_type = form_data.split('Form ')[1].split(' -')[0] if 'Form' in form_data else None

        # Get table from soup
        table = self.soup.find('table', {'class': 'tableFile'})

        links = dict()
        doc_types = list()

        for row in table.find_all('tr')[1:]:
            row_data = row.find_all('td')
            _document = row_data[2].text.split('.')[-1]
            _type = row_data[3].text

            if _type == form_type or form_type is None:
                _link = "https://www.sec.gov" + row_data[2].find('a').get('href').strip()
                links.update({_document: _link})
                doc_types.append(_document)

        if not links:
            return None

        else:
            if prefer_xml and 'xml' in doc_types:
                return links['xml']
            elif 'html' in doc_types:
                return links['html']
            elif 'htm' in doc_types:
                return links['htm']
            else:
                return links['xml']
