# Form 4 Parser Class File

from xml.etree import ElementTree

import numpy as np
import pandas as pd
from lxml import etree

from tracker.parsers.sec_filings_parser import SECFilingsParser


class Form4Parser(SECFilingsParser):
    def __init__(self, name: str, url: str):
        """
        Form 4 Parser Class Constructor

        :param name: Form Name
        :param url: Form URL
        """

        super().__init__(name, url)

        # Parsed DataFrames
        self.issuer_table: pd.DataFrame = pd.DataFrame()
        self.owner_table: pd.DataFrame = pd.DataFrame()
        self.non_derivative_table: pd.DataFrame = pd.DataFrame()
        self.derivative_table: pd.DataFrame = pd.DataFrame()

        self.filings = AttributeError('Form 4 does not have filings.')

        self.fields: dict = {
            "ownershipDocument": {
                "issuer": {
                    "issuerCik": {},
                    "issuerName": {},
                    "issuerTradingSymbol": {}
                },
                "reportingOwner": {
                    "reportingOwnerId": {
                        "rptOwnerCik": {},
                        "rptOwnerName": {}
                    },
                    "reportingOwnerAddress": {},
                    "reportingOwnerRelationship": {
                        "isDirector": {},
                        "isOfficer": {},
                        "isTenPercentOwner": {},
                        "isOther": {},
                        "officerTitle": {}
                    }
                },
                "nonDerivativeTable": {
                    "nonDerivativeTransaction": {
                        "securityTitle": {},
                        "transactionDate": {},
                        "transactionCoding": {},
                        "transactionTimeliness": {},
                        "transactionAmounts": {
                            "transactionShares": {},
                            "transactionPricePerShare": {},
                            "transactionAcquiredDisposedCode": {}
                        },
                        "postTransactionAmounts": {
                            "sharesOwnedFollowingTransaction": {}
                        },
                        "ownershipNature": {
                            "directOrIndirectOwnership": {},
                            "natureOfOwnership": {}
                        }
                    },
                    "nonDerivativeHolding": {
                        "securityTitle": {},
                        "postTransactionAmounts": {
                            "sharesOwnedFollowingTransaction": {}
                        },
                        "ownershipNature": {
                            "directOrIndirectOwnership": {},
                            "natureOfOwnership": {}
                        }
                    }
                },
                "derivativeTable": {
                    "derivativeTransaction": {
                        "securityTitle": {},
                        "conversionOrExercisePrice": {},
                        "transactionDate": {},
                        "transactionCoding": {},
                        "transactionTimeliness": {},
                        "transactionAmounts": {
                            "transactionShares": {},
                            "transactionPricePerShare": {},
                            "transactionAcquiredDisposedCode": {}
                        },
                        "exerciseDate": {},
                        "expirationDate": {},
                        "underlyingSecurity": {
                            "underlyingSecurityTitle": {},
                            "underlyingSecurityShares": {}
                        },
                        "postTransactionAmounts": {
                            "sharesOwnedFollowingTransaction": {}
                        },
                        "ownershipNature": {
                            "directOrIndirectOwnership": {},
                            "natureOfOwnership": {}
                        }
                    },
                    "derivativeHolding": {
                        "securityTitle": {},
                        "conversionOrExercisePrice": {},
                        "exerciseDate": {},
                        "expirationDate": {},
                        "underlyingSecurity": {
                            "underlyingSecurityTitle": {},
                            "underlyingSecurityShares": {}
                        },
                        "postTransactionAmounts": {
                            "sharesOwnedFollowingTransaction": {}
                        },
                        "ownershipNature": {
                            "directOrIndirectOwnership": {},
                            "natureOfOwnership": {}
                        }
                    }
                },
                "footnotes": {},
                "ownerSignature": {}
            }
        }

    def parse(self) -> list[pd.DataFrame]:
        """
        Parse document and organize data into dataframe

        :return: [self.non_derivative_table, self.derivative_table]
        """

        # Check if webpage HTML text is cached. If not, get webpage first.
        if self.webpage is None:
            self.get_webpage()

        # Parse XML
        data = etree.fromstring(self.webpage)

        # Fields that can be parsed into DataFrames
        parsable_fields = ['issuer', 'reportingOwner', 'nonDerivativeTable', 'derivativeTable']

        # All top-level fields in XML data
        all_fields = data.findall('./')

        # Data Fields to Parse
        fields = [field.tag for field in all_fields if field.tag in parsable_fields]

        # Parse Issuer
        if 'issuer' in fields:
            self.issuer_table = self._parse_issuer(data.find('./issuer'))

        # Parse Reporting Owner
        if 'reportingOwner' in fields:
            self.owner_table = self._parse_owner(data.find('./reportingOwner'))

        # Parse Non-Derivative Table
        if 'nonDerivativeTable' in fields:
            self.non_derivative_table = self._parse_non_derivative_table(data.find('./nonDerivativeTable'))

        # Parse Derivative Table
        if 'derivativeTable' in fields:
            self.derivative_table = self._parse_derivative_table(data.find('./derivativeTable'))

        return [self.non_derivative_table, self.derivative_table]

    @staticmethod
    def _parse_issuer(issuer: ElementTree.Element) -> pd.DataFrame:
        """
        Parse Issuer XML Data.

        :param issuer: Issuer XML Data
        :return: Parsed Issuer DataFrame
        """

        # Fields to Parse
        issuer_fields = ['issuerCik', 'issuerName', 'issuerTradingSymbol']

        # Initialize Data Dictionary
        issuer_data = dict()

        # Iterate through fields and get data from XML
        for field in issuer_fields:
            data = issuer.find(f'./{field}').text
            issuer_data.update({field: data})

        # Create DataFrame from Data Dictionary
        issuer_df = pd.DataFrame.from_dict(issuer_data, orient='index')

        # Replace None with np.nan
        issuer_df = issuer_df.fillna(np.nan)

        return issuer_df

    @staticmethod
    def _parse_owner(owner: ElementTree.Element) -> pd.DataFrame:
        """
        Parse Reporting Owner XML Data.

        :param owner: Reporting Owner XML Data
        :return: Parsed Reporting Owner DataFrame
        """

        # Fields to Parse
        owner_fields = ['reportingOwnerId', 'reportingOwnerAddress', 'reportingOwnerRelationship']

        # Initialize Data Dictionary
        owner_data = dict()

        # Iterate through fields and get data from XML
        for field in owner_fields:
            data = owner.find(f'./{field}')

            # Iterate through subfields and get data from XML
            for sub_field in data.findall('./'):
                sub_data = sub_field.text
                owner_data.update({f"{field[14:]}.{sub_field.tag.split('rptOwner')[-1]}": sub_data})

        # Create DataFrame from Data Dictionary
        owner_df = pd.DataFrame.from_dict(owner_data, orient='index')

        # Replace None with np.nan
        owner_df = owner_df.fillna(np.nan)

        return owner_df

    @staticmethod
    def _parse_non_derivative_table(non_derivative_table: ElementTree.Element) -> pd.DataFrame:
        """
        Parse Non-Derivative Table XML Data.
        Note: non-derivative is common stock, preferred stock, and other stock

        :param non_derivative_table: Non-Derivative Table XML Data
        :return: Parsed Non-Derivative Table DataFrame
        """

        transaction_fields = [
            'securityTitle', 'transactionDate', 'deemedExecutionDate', 'transactionCoding',
            'transactionTimeliness', 'transactionAmounts', 'postTransactionAmounts', 'ownershipNature'
        ]

        # Initialize Data Dictionary: Stores {count: transaction_data}
        transactions_dict = dict()
        count: int = 1

        # Iterate through transactions
        for transaction in non_derivative_table.findall('./'):
            # Initialize Transaction Data Dictionary
            transaction_data = dict()

            # Iterate through top-level transaction fields and get data from XML
            for field in transaction_fields:
                sub_fields = [subfield.tag for subfield in transaction.findall(f'./{field}/')]

                # Check if field has subfields
                if not sub_fields:
                    try:
                        transaction_data.update({field: transaction.find(f'./{field}').text})
                    except AttributeError:
                        transaction_data.update({field: np.nan})

                # Check if Value is a Subfield
                elif 'value' in sub_fields:
                    if len(transaction.findall(f'./{field}/value')) > 0:
                        transaction_data.update({field: transaction.find(f'./{field}/value').text})
                    else:
                        transaction_data.update({field: np.nan})

                # Iterate through subfields and get data from XML
                else:
                    for sub_field in sub_fields:
                        sub_sub_fields = [ssf.tag for ssf in transaction.findall(f'./{field}/{sub_field}/')]

                        # Check if field has subfields
                        if not sub_sub_fields:
                            try:
                                ssf_data = transaction.find(f'./{field}/{sub_field}').text
                                transaction_data.update({f"{field}.{sub_field}": ssf_data})
                            except AttributeError:
                                transaction_data.update({f"{field}.{sub_field}": np.nan})

                        # Check if Value is a Subfield
                        elif 'value' in sub_sub_fields:
                            if len(transaction.findall(f'./{field}/{sub_field}/value')) > 0:
                                ssf_data = transaction.find(f'./{field}/{sub_field}/value').text
                                transaction_data.update({f"{field}.{sub_field}": ssf_data})
                            else:
                                transaction_data.update({f"{field}.{sub_field}": np.nan})

            transactions_dict.update({count: transaction_data})
            count += 1

        # Create DataFrame from Data Dictionary
        transactions_df = pd.DataFrame.from_dict(transactions_dict, orient='index')

        # Replace None values with np.nan
        transactions_df = transactions_df.fillna(value=np.nan)

        return transactions_df

    @staticmethod
    def _parse_derivative_table(derivative_table: ElementTree.Element) -> pd.DataFrame:
        """
        Parse Derivative Table XML Data.
        Note: derivative is RSU, option and future on underlying stock or bonds and notes.

        :param derivative_table: Derivative Table XML Data
        :return: Parsed Derivative Table DataFrame
        """

        transaction_fields = [
            'securityTitle', 'conversionOrExercisePrice', 'transactionDate', 'transactionCoding',
            'transactionTimeliness', 'transactionAmounts', 'exerciseDate', 'expirationDate', 'underlyingSecurity',
            'postTransactionAmounts', 'ownershipNature'
        ]

        # Initialize Data Dictionary: Stores {count: transaction_data}
        transactions_dict = dict()
        count: int = 1

        # Iterate through transactions
        for transaction in derivative_table.findall('./'):
            # Initialize Transaction Data Dictionary
            transaction_data = dict()

            for field in transaction_fields:
                sub_fields = [subfield.tag for subfield in transaction.findall(f'./{field}/')]

                # Check if field has subfields
                if not sub_fields:
                    try:
                        transaction_data.update({field: transaction.find(f'./{field}').text})
                    except AttributeError:
                        transaction_data.update({field: np.nan})

                # Check if Value is a Subfield
                elif 'value' in sub_fields:
                    if len(transaction.findall(f'./{field}/value')) > 0:
                        transaction_data.update({field: transaction.find(f'./{field}/value').text})
                    else:
                        transaction_data.update({field: np.nan})

                # Iterate through subfields and get data from XML
                else:
                    for sub_field in sub_fields:
                        sub_sub_fields = [ssf.tag for ssf in transaction.findall(f'./{field}/{sub_field}/')]

                        # Check if field has subfields
                        if not sub_sub_fields:
                            try:
                                ssf_data = transaction.find(f'./{field}/{sub_field}').text
                                transaction_data.update({f"{field}.{sub_field}": ssf_data})
                            except AttributeError:
                                transaction_data.update({f"{field}.{sub_field}": np.nan})

                        # Check if Value is a Subfield
                        elif 'value' in sub_sub_fields:
                            if len(transaction.findall(f'./{field}/{sub_field}/value')) > 0:
                                ssf_data = transaction.find(f'./{field}/{sub_field}/value').text
                                transaction_data.update({f"{field}.{sub_field}": ssf_data})
                            else:
                                transaction_data.update({f"{field}.{sub_field}": np.nan})

            transactions_dict.update({count: transaction_data})
            count += 1

        # Create DataFrame from Data Dictionary
        transactions_df = pd.DataFrame.from_dict(transactions_dict, orient='index')

        # Replace None values with np.nan
        transactions_df = transactions_df.fillna(value=np.nan)

        return transactions_df
