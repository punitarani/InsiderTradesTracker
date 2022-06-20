# SEC EDGAR Parser
# https://www.sec.gov/edgar/search/#/

import json
import logging

import pandas as pd
import requests

from baseurls import SEC_EDGAR_FTS
from common import Logger
from tracker.parser import SECParser, ResponseError
from tracker.utils import RateLimit


# Define Edgar Logger
EdgarLogger: Logger = Logger('edgar')
logger: logging.Logger = EdgarLogger.get_logger()


class EdgarParser(SECParser):
    """
    SEC Edgar Parser
    """

    def __init__(self, name: str, filters: dict):
        """
        SEC Edgar Parser Constructor

        :param name: Webpage Name
        :param filters: Search Filters
        """

        super().__init__(name=name)

        # Params
        self.filters: dict = filters
        self.webpage: dict | None = None  # Redefine webpage to dict instead of str attr

        # Cache
        self.results: pd.DataFrame | None = None
        self.results_count: int | None = None

        # Delete irrelevant inherited attributes
        if hasattr(self, 'url'):
            delattr(self, 'url')

    @RateLimit(limit=10, period=1, max_wait=15, logger=logger)
    def get_webpage(self, *args, **kwargs) -> dict:
        """
        Get the search results data

        :return: Search Results Data

        Notes:
            The EDGAR Full Test Search(FTS) Engine uses a different POST filters to get response with results.
        """

        # Build Header
        headers: dict = {
            'User-Agent': self._get_user_agent()
        }

        # Build Payload
        payload: dict = self.filters

        # Post and Get response
        response = requests.post(url=SEC_EDGAR_FTS,
                                 json=payload,
                                 headers=headers)

        # Check if response is successful
        if response.status_code != 200:
            error_msg = f'Response Error: {response.status_code} - {response.reason}'
            self.logger.error(error_msg)
            raise ResponseError(message=error_msg, response=response)

        # Get data from response
        return_data: dict = json.loads(response.text)

        # Cache return data
        self.webpage = return_data

        return return_data

    def parse(self, force_refresh: bool = True) -> pd.DataFrame:
        """
        Parse the search results

        :param force_refresh: Re-download the webpage data
        :return: Search Results Table

        Notes:
            Results Table Columns: ['index', 'type', 'id', 'score', 'source', 'sort']

            index: 'edgar_file'. 
            type: '_doc'. 
            id: '<acc_no>:<file_name.format>'.
            source: dict(['ciks', 'period_ending', 'root_form', 'file_num', 'display_names', 'xsl',
                                    'sequence', 'file_date', 'biz_states', 'sics', 'form', 'adsh', 'film_num',
                                    'biz_locations', 'file_type', 'file_description', 'inc_states', 'items']).
        """

        # Check if webpage data is cached. If not, get webpage first.
        if self.webpage is None or force_refresh:
            self.get_webpage()

        # Results count
        try:
            self.results_count = self.webpage['hits']['total']['value']
        except KeyError:
            self.results_count = None

        # Get filings data
        data = self.webpage['hits']['hits']

        # Create DataFrame from data
        results = pd.DataFrame.from_records(data=data)

        # Rename columns to not include '_' prefix
        cols_rename = {col: col[1:] if col.startswith('_') else col for col in results.columns.tolist()}
        results.rename(columns=cols_rename, inplace=True)

        # Cache results
        self.results = results

        return results

    # Irrelevant Inherited Methods
    def set_url(self, url: None = None) -> AttributeError:
        """
        DO NOT USE.
        """
        return AttributeError('EdgarParser.set_url() should not be used.')
