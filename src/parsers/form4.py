# Form 4 Parser Class File

from src.parsers.SECFilingsParser import SECFilingsParser


class Form4(SECFilingsParser):
    def __init__(self, name: str, url: str):
        """
        Form 4 Parser Class Constructor

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
