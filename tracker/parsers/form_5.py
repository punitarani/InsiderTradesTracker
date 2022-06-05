# Form 5 Parser Class File

from tracker.parsers.sec_filings_parser import SECFilingsParser


class Form5Parser(SECFilingsParser):
    def __init__(self, name: str, url: str):
        """
        Form 5 Parser Class Constructor

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
                "ownerSignature": {}
            }
        }
