"""
Form 3 Parser Class File
"""

from .sec import SECParser


class Form3Parser(SECParser):
    """
    Form 3 Parser
    """

    def __init__(self, name: str, url: str):
        """
        Form 3 Parser Class Constructor

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
                "nonDerivativeTable": {
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
                    "derivativeHolding": {
                        "securityTitle": {},
                        "conversionOrExercisePrice": {},
                        "exerciseDate": {},
                        "expirationDate": {},
                        "underlyingSecurity": {
                            "underlyingSecurityTitle": {},
                            "underlyingSecurityShares": {}
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

        super().__init__(name, url)
