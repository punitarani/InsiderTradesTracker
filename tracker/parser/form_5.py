"""
Form 5 Parser Class File
"""

from .sec import SECParser


class Form5Parser(SECParser):
    """
    Form 5 Parser
    """

    def __init__(self, name: str, url: str):
        """
        Form 5 Parser Class Constructor

        :param name: Form Name
        :param url: Form URL
        """

        # pylint: disable=pointless-string-statement
        # Fields schema
        """
        Fields:
        {
            "ownershipDocument": {
                "issuer": {},
                "reportingOwner": {
                    "reportingOwnerId": {},
                    "reportingOwnerAddress": {},
                    "reportingOwnerRelationship": {}
                },
                "ownerSignature": {}
            }
        }
        """

        super().__init__(name, url)
