"""
SEC Latest Filings Screener
https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent
"""


from urllib.parse import urlencode

import pandas as pd

from baseurls import SEC_LATEST_FILINGS
from tracker.parser.sec_latest_filings_parser import SECFilingsParser


class SECFilingsScreener:
    """
    SEC Latest Filings Screener Class
    """

    def __init__(self,
                 name: str,
                 count: int = 100,
                 company: str | None = None,
                 cik: str | None = None,
                 form: str | None = None,
                 owner: str | None = None):
        """
        SEC Filings Screener Class Constructor

        :param name: Screener Name
        """

        self.name: str = name
        self.base_url: str = SEC_LATEST_FILINGS

        # Filter Conditions
        self.company: str | None = company
        self.cik: str | None = cik
        self.form: str | None = form
        self.owner: str | None = owner
        self.count: int = self.set_entries_count(count)

        # Build the URL
        self.url: str = self.build_url()

        # Parser
        self.parser: SECFilingsParser = SECFilingsParser(self.name, self.url)
        self.filings: pd.DataFrame = pd.DataFrame()

    def filter_company(self, company: str | None) -> str | None:
        """
        Filter the company name

        :param company: Company Name
        """

        self.company = company

        return self.company

    def filter_cik(self, cik: str | None) -> str | None:
        """
        Filter the company CIK

        :param cik: Company Identification Number
        """

        self.cik = cik

        return self.cik

    def filter_form(self, form: str | None) -> str | None:
        """
        Filter the form type

        :param form: Form Type
        """

        self.form = form

        return self.form

    def filter_owner(self, include: bool = True, only: bool = False) -> str:
        """
        Filter the ownership

        :param include: True to include, False to exclude
        :param only: True to only

        NOTE: only takes precedence over include
        """

        if only:
            self.owner = 'only'
        elif include:
            self.owner = 'include'
        else:
            self.owner = 'exclude'

        return self.owner

    def set_entries_count(self, count: int) -> int:
        """
        Set the entries

        :param count: Entries Count [10, 20, 40, 80, 100]

        Note: Rounds to closest lower accepted count.
        """

        # Match the count to the acceptable count
        if count not in [10, 20, 40, 80, 100]:
            # Check lower bound
            if count < 20:
                count = 10

            # Round to the nearest acceptable count
            elif count < 40:
                count = 20

            elif count < 80:
                count = 40

            elif count < 100:
                count = 80

            # Cap to upper bound
            else:
                count = 100

        self.count = count

        return count

    def build_url(self, override_count: int | None = None, start_count: int | None = None) -> str:
        """
        Build the URL

        :param override_count: Override the count
        :param start_count: Start count (for pagination)
        """

        url = self.base_url

        # Create params dict
        params = {
            'count': override_count if override_count is not None else self.count,
            'company': self.company,
            'CIK': self.cik,
            'type': self.form,
            'owner': self.owner,
            'start': start_count
        }

        # Remove None value parameters
        params = {k: v for k, v in params.items() if v is not None}

        # Add the URL parameters
        url += "&" + urlencode(params)

        # Cache the URL
        self.url = url

        return url

    def get_url(self) -> str:
        """
        Get the URL and cache it both locally and in the parser.

        :return: URL
        """

        self.build_url()

        # Update the parser URL
        self.parser.set_url(self.url)

        return self.url

    def get_filings(self) -> pd.DataFrame:
        """
        Get the filings

        :return: Filings
        """

        # Build URL to get the filings
        self.get_url()

        # Get the filings and parse to a dataframe
        filings = self.parser.parse()

        # Remove duplicates by index
        filings = filings[~filings.index.duplicated(keep='first')]

        # Filter the filings by the form type
        if self.form is not None:
            filings = filings[filings['form_type'] == self.form]

        # Cache the filings
        self.filings = filings

        return self.filings

    def get_filings_until(self, accession_number: str, max_count: int = 2000) -> pd.DataFrame:
        """
        Get Filings until filing with accession number is found before max_count.

        :param accession_number: SEC Filing Accession Number (required) (Format: ##########-##-######)
        :param max_count: Maximum filings to get (default and max is 2000)
        :return: Filings (pd.DataFrame)

        Notes
        -----
        If the accession number is not found, the filings will be returned up to the max_count.
        Does include the filing with given accession number in the returned dataframe.
        """

        # Check max_count bound
        max_count = min(abs(max_count), 2000)

        # Set count to 100 (Max allowed by SEC per request)
        count: int = 100
        start: int = 0
        found: bool = False

        # Initialize the filings dataframe
        filings: pd.DataFrame = pd.DataFrame()

        # Cache last index
        last_index: str = ""

        # Loop until we find the filing, or we reach the max count
        while not found and start < max_count:
            # Build URL to get the filings
            self.build_url(override_count=count, start_count=start)

            # Get the filings and parse to a dataframe
            df = self.parser.parse()

            # Remove duplicates by index
            df = df[~df.index.duplicated(keep='first')]

            # Check if the filing was found
            try:
                df = df.loc[:accession_number]
                found = True
            except (pd.errors.InvalidIndexError, KeyError):
                pass

            # Append the dataframe to the filings
            if filings.empty:
                filings = df
                last_index = df.iloc[-1].index

            else:
                # Trim df to the last index to avoid duplicates
                try:
                    df = df.loc[last_index:]
                except (pd.errors.InvalidIndexError, KeyError):
                    pass

                filings = pd.concat([filings, df], ignore_index=False, sort=False, axis=0)

            # Increment the start count
            start += count

        return filings
