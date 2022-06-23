# Get Field Names from XML Document

"""
Example Output
--------------
Field Names Dict for Form 4 and 4/A

{
    "ownershipDocument": {
        "issuer": {},
        "reportingOwner": {
            "reportingOwnerId": {},
            "reportingOwnerAddress": {},
            "reportingOwnerRelationship": {}
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

"""

# noinspection PyPep8Naming
from xml.etree import ElementTree as et

from lxml import etree

from tracker.parser.webpage_parser import WebpageParser


def get_fields(data: et):
    """
    Recursively get field names from Soup of XML Document

    :param data: XML ElementTree object
    """

    # Initialize field names dict
    fields = {}

    # Initialize Children dict
    children = {}

    # Traverse through Tree
    for child in data:
        # Recursively get field names from child
        if len(child) > 0:
            children.update(get_fields(child))

        # If no children, empty dict

    # Update fields dict with children
    fields.update({data.tag: children})

    return fields


def merge_dicts(dict1: dict, dict2: dict):
    """
    Recursively go through dict1 and dict2 and merge.
    Combine elements even if only in one dict.

    :param dict1: dict1s
    :param dict2: dict2
    """

    # Initialize merged dict to dict1
    merged = dict1

    # Traverse through dict2
    for key, value in dict2.items():
        # If key is not in dict1, add key and value to merged dict
        if key not in merged:
            merged.update({key: value})

        else:
            # If key is in dict1, recursively merge
            merged[key] = merge_dicts(merged[key], value)

    return merged


if __name__ == '__main__':
    ft = '4'

    filing_urls = []

    base_url = f'https://www.sec.gov/cgi-bin/browse-edgar?type={ft}&count=100&action=getcurrent'
    base_parser = WebpageParser('Base', base_url)
    base_soup = base_parser.get_soup()

    # Find Table of Filings
    table = base_soup.find('body').find('div').find_all('table')[-1]

    # Iterate through each row in table
    for row in table.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) == 6:
            # Get form type from first column text
            row_form_type = cols[0].text

            # Get link from second column href
            link = 'https://www.sec.gov/' + cols[1].find('a').get('href')

            # Check form_type and add to list
            if row_form_type == ft:
                filing_urls.append(link)
    print('Finished processing base urls')
    print(f'Found {str(len(filing_urls))} filings')
    print(filing_urls)
    print('\n\n')

    # Iterate through filing_urls and get xml urls
    xml_urls = []
    for filing_url in filing_urls:
        print(f"Processing Filing url: {filing_url}")
        filing_parser = WebpageParser('Filing', filing_url)
        filing_soup = filing_parser.get_soup()

        # Get list of HTML links with '.xml' in href. Ignore links with 'xsl' in url
        for link in filing_soup.find_all('a'):
            if '.xml' in link.get('href') and 'xsl' not in link.get('href'):
                xml_urls.append('https://www.sec.gov' + link.get('href'))
    print('Finished processing filing urls')
    print(f'Found {str(len(xml_urls))} xml urls')
    print(xml_urls)
    print('\n\n')

    # List of fields from each xml tree
    tree_fields = []

    # Iterate through xml_urls and get fields
    for url in xml_urls:
        print(f"Processing XML: {url}")
        parser = WebpageParser('Test', url)
        webpage = parser.get_webpage()

        # Parse XML Document
        try:
            tree: et = etree.fromstring(webpage)

            # Traverse through Document
            _tree_fields = get_fields(tree)
            tree_fields.append(_tree_fields)
        except Exception as e:
            print(f"Error parsing XML: {e} for url: {url}")

    print('Finished processing xml urls')
    print(f'Found {str(len(tree_fields))} xml fields')
    print(tree_fields)
    print('\n\n')

    print('Merging fields')

    # Merge fields
    fields_dict = {}

    # Iterate through tree_fields and merge
    for tree_field in tree_fields:
        fields_dict = merge_dicts(fields_dict, tree_field)

    print(fields_dict)
