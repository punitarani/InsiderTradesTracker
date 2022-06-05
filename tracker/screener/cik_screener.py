# CIK Screener Class File

from pathlib import Path

import pandas as pd

from defs import DATA_DIR_PATH
from tracker.parsers.webpage_parser import WebpageParser, ResponseError

from copy import deepcopy


class CIKScreener:
    """
    CIK Screener Class
    """

    def __init__(self):
        # Lookup Data
        self.lookup_url: str = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"
        self.lookup_df: pd.DataFrame = pd.DataFrame()
        self.lookup_source_from_url: bool | None = None  # True if lookup_df loaded from URL, False if from Parquet file

        # Save Data
        self.save_path: Path = DATA_DIR_PATH.joinpath("cik_lookup.parquet")

        # Parser
        self.parser: WebpageParser = WebpageParser("cik-lookup-data", self.lookup_url)

    def _get_parser(self) -> WebpageParser:
        """
        Get the Parser

        :return: Parser object (WebpageParser)
        """

        return self.parser

    # region Get, Load, and Save lookup_df methods

    def get_lookup_df(self) -> pd.DataFrame | None:
        """
        Get the CIK Lookup DataFrame

        :return: CIK Lookup DataFrame (pd.DataFrame) or None if not loaded

        Note
        ----
        If the CIK Lookup DataFrame is not cached, it will try to load it from a Parquet file.
        If the Parquet file does not exist, it will try to load it from a URL.
        """

        if self.lookup_df.empty:
            try:
                self._load_lookup_df_from_parquet()

            except FileNotFoundError:
                self._get_lookup_df_from_url()
                self._save_lookup_df_to_parquet()

        return self.lookup_df

    def _get_lookup_df_from_url(self) -> pd.DataFrame | None:
        # User-Agent is required to access SEC website. Use the latest Chrome on Windows 10 User Agent.
        # Otherwise, it will return 'Your Request Originates from an Undeclared Automated Tool' and no data.
        headers = self.parser.header_chrome_user_agent

        try:
            self.parser.get_webpage(headers=headers)
        except ResponseError:
            print(f"Failed to get {self.lookup_url}.")
            return

        data = self.parser.webpage.split("\n")

        # Create DataFrame from the data
        df = pd.DataFrame(data, columns=["company"])

        # Split last 12 characters of company name to get CIK
        df["cik"] = df["company"].str[-11:-1]

        # Update company column to remove CIK
        df["company"] = df["company"].str[:-12]

        # Cache lookup_df
        self.lookup_df = df
        self.lookup_source_from_url = True

        return df

    def _save_lookup_df_to_parquet(self) -> bool:
        """
        Save the CIK Lookup DataFrame to a Parquet file

        :return: True if successful, False otherwise
        """

        try:
            self.lookup_df.to_parquet(self.save_path)
            return True
        except Exception as e:
            print(e)
            print(f"Failed to save {self.save_path}.")

        return False

    def _load_lookup_df_from_parquet(self) -> pd.DataFrame | None:
        """
        Load the CIK Lookup DataFrame from a Parquet file

        :return: CIK Lookup DataFrame (pd.DataFrame) or None if not loaded
        """

        try:
            lookup_df = pd.read_parquet(self.save_path)

            # Cache lookup_df
            self.lookup_df = lookup_df
            self.lookup_source_from_url = False

            return lookup_df

        except Exception as e:
            print(e)
            print(f"Failed to load {self.save_path}.")

        return None

    # endregion

    # region Get CIK/Company methods

    def filter_cik(self, cik: str | int) -> pd.DataFrame:
        """
        Filter the CIK Lookup DataFrame by CIK.
        Can return multiple rows if the CIK is not unique or if CIK has multiple companies names.

        :param cik: CIK (str or int)
        :return: DataFrame matching the CIK (pd.DataFrame)

        Note
        ----
        Formats CIK to 10 Characters.
            If CIK is not 10 characters, it will be padded with 0s.
            If CIK is longer than 10 characters, it will be truncated.

        Uses df.str.contains() method.
            Filter if cik is present is lookup_df.cik.
            If cik is not present, it will return an empty DataFrame.
        """

        # Get lookup_df if it is not cached
        self.get_lookup_df()

        # Create a copy of lookup_df to avoid modifying the original
        df = deepcopy(self.lookup_df)

        # Convert cik to string
        cik = str(cik)

        # Format cik to have 10 characters
        if len(cik) > 10:
            cik = cik[-10:]
        else:
            cik = cik.zfill(10)

        # Filter lookup_df by CIK
        df = df[df['cik'].str.contains(cik)]

        # Alternate method to filter lookup_df by CIK
        # Filter using query
        # df.query("cik == @cik", inplace=True)

        return df

    def filter_company(self, company: str) -> pd.DataFrame:
        """
        Filter the CIK Lookup DataFrame by Company Name.
        Can return multiple rows if the Company Name is not unique or if Company Name has multiple CIKs.

        :param company: Company Name (str)
        :return: DataFrame matching the Company Name (pd.DataFrame)
        """

        # Get lookup_df if it is not cached
        self.get_lookup_df()

        # Create a copy of lookup_df to avoid modifying the original
        df = deepcopy(self.lookup_df)

        # Make company upper case
        company = company.upper()

        # Filter lookup_df by Company Name
        df = df[df['company'].str.contains(company)]

        return df

    # endregion
