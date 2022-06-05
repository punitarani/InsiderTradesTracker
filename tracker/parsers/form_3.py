# Form 3 Parser Class File

from tracker.parsers import SECFilingsParser


class Form3Parser(SECFilingsParser):
    def __init__(self, name: str, url: str):
        """
        Form 3 Parser Class Constructor

        :param name: Form Name
        :param url: Form URL
        """

        super().__init__(name, url)

        self.fields: dict = {
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
