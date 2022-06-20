# SEC EDGAR Screener
# https://www.sec.gov/edgar/search/#


from urllib.parse import urlencode

import pandas as pd

from baseurls import SEC_EDGAR
from tracker.parser import EdgarParser


class EdgarScreener:
    """
    EDGAR Screener

    Filters:
    Phrase: Document Word or Phrase,
    Name: Individual or Company Name or Ticker,
    CIK: Company or Individual,
    Form: Filing Form Type,

    Note Implemented:
    Filed Date Range,
    Filed From,
    Filed To.
    """

    def __init__(self, name: str):
        """
        EDGAR Screener Constructor

        :param name: Screener Name
        """

        self.name: str = name

        self.url: str = SEC_EDGAR

        # Screener Filters
        self.filters: dict[str, str | list | None] = {
            'q': None,
            'dateRange': None,
            'category': None,
            'ciks': None,
            'entityName': None,
            'page': None,
            'from': None,
            'startdt': None,
            'enddt': None,
            'forms': None
        }

        # Initialize Edgar Parser
        self.parser = EdgarParser(self.name, self.filters)

        # Caches
        self.filings: pd.DataFrame | None = None

    def get_filings(self) -> pd.DataFrame:
        """
        Get Filings Search Results

        :return: Filings DataFrame
        """

        # Get and parse data of filtered search results
        filings: pd.DataFrame = self.parser.parse()

        # Cache filings
        self.filings = filings

        return filings

    def build_url(self) -> str:
        """
        Build SEC Edgar Search URL with filters

        :return: URL
        """

        # Get filter params and remove if filter is None
        params = dict((k, v) for k, v in self.filters.items() if v is not None)

        # Convert ciks from list to comma-seperated string
        if 'ciks' in params and isinstance(params['ciks'], list):
            params.update({'ciks': ','.join(params['ciks'])})

        # Encode params and combine with base url
        url = SEC_EDGAR + urlencode(params)

        # Replace + with %2520
        url = url.replace('+', '%2520')

        # Replace %22 and %22%2520 with %2522
        # Only applies to q, not sure how to only look within q
        url = url.replace('%22', '%2522')
        url = url.replace('%22%2520', '%2522')

        # Replace %2C with %252C
        # Only applies to forms, not sure how to only look within forms
        url = url.replace('%2C', '%252C')

        # Cache url
        self.url = url

        return url

    # region add filters

    def filter_ciks(self, ciks: str | int | list[str | int]) -> list[str] | None:
        """
        Add CIKs Filter

        :param ciks: CIKs to filter
        :return: Old ciks that got replaced, or None
        """

        # Format ciks input into list of string. Format to 10 digits with zfill.
        # int -> list[str]
        if isinstance(ciks, int):
            ciks = [str(ciks).zfill(10)]

        # str -> list[str]
        elif isinstance(ciks, str):
            ciks = [ciks.zfill(10)]

        # list[*] to list[str]
        elif isinstance(ciks, list):
            ciks = [str(cik).zfill(10) for cik in ciks]

        # Format all ciks to 10
        _ciks = ciks
        ciks = []
        for cik in _ciks:
            if len(cik) < 10:
                cik = cik.zfill(10)
            elif len(cik) > 10:
                cik = cik[-10:]

            ciks.append(cik)

        # Check if filter is already applied
        if self.filters['ciks'] is not None:
            # Get old ciks
            old_ciks = self.filters['ciks']

            # Update filter with ciks converted to comma-seperated-string
            self.filters['ciks'] = ciks

            return old_ciks

        # Apply filter
        else:
            # Update filter with ciks converted to comma-seperated-string
            self.filters['ciks'] = ciks

        return None

    def filter_filing_types(self, types: str | int | list[str, int]) -> list[str] | None:
        """
        Add Filing Form Types Filter

        :param types: Form Types to filter
        :return: Old types that got replaced, or None
        """

        # Format types input into list of string
        # int -> list[str]
        if isinstance(types, int):
            types = [str(types).upper()]

        # str -> list[str]
        elif isinstance(types, str):
            types = [types.upper()]

        # list[*] to list[str]
        elif isinstance(types, list):
            types = [str(form_type).upper() for form_type in types]

        # Check if filter is already applied
        if self.filters['forms'] is not None:
            # Get old forms
            old_forms = self.filters['forms']

            # Update filter with types converted to comma-seperated-string
            self.filters['forms'] = ','.join(types)
            self.filters['category'] = 'custom'

            return old_forms

        # Apply filter
        else:
            # Update filter with types converted to comma-seperated-string
            self.filters['forms'] = ','.join(types)
            self.filters['category'] = 'custom'

        return None

    def filter_name(self, name: str) -> str | None:
        """
        Add Filter: Company name, ticker, or individual's name

        :param name: Company name, ticker, CIK number or individual's name
        :return: Old name that got replaced, or None
        """

        if self.filters['entityName'] is not None:
            # Get old name that will be replaced
            old_name: str = self.filters['entityName']

            # Update filter with phrase
            self.filters['entityName'] = name

            return old_name

        else:
            self.filters['entityName'] = name

        return None

    def filter_phrase(self, phrase: str) -> str | None:
        """
        Add Filter: Document word or phrase

        :param phrase: Word or Phrase to Filter
        :return: Old phrase that got replaced, or None
        """

        if self.filters['q'] is not None:
            # Get old phrase that will be replaced
            old_phrase: str = self.filters['q']

            # Update filter with phrase
            self.filters['q'] = phrase

            return old_phrase

        else:
            self.filters['q'] = phrase

        return None

    # endregion add filters

    # region remove filters

    def remove_filter_ciks(self) -> bool:
        """
        Remove Filer: CIKs
        :return: True if filter was removed, False if filter is None
        """

        if self.filters['ciks'] is not None:
            self.filters['ciks'] = None
            return True

        # Filter is already None
        return False

    def remove_filter_filing_types(self) -> bool:
        """
        Remove Filter: Filing Type
        :return: True if filter was removed, False if filter is None
        """

        if self.filters['forms'] is not None:
            self.filters['forms'] = None
            self.filters['category'] = None
            return True

        # Filter is already None
        return False

    def remove_filter_name(self) -> bool:
        """
        Remove Filter: Company name, ticker, or individual's name
        :return: True if filter was removed, False if filter is None
        """

        if self.filters['entityName'] is not None:
            self.filters['entityName'] = None
            return True

        # Filter is already None
        return False

    def remove_filter_phrase(self) -> bool:
        """
        Remove Filter: Document word or phrase
        :return: True if filter was removed, False if filter is None
        """

        if self.filters['q'] is not None:
            self.filters['q'] = None
            return True

        # Filter is already None
        return False

    # endregion remove filters
