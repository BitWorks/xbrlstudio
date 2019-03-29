"""
:mod: 'BookValidator'
~~~~~~~~~~~~~~~~~~~~~

..  py:module:: BookValidator
    :copyright: Copyright BitWorks LLC, All rights reserved.
    :license: MIT
    :synopsis: Functionality for validating software registration key against an expected key, given a sale_id
    :description: Key validation functionality
                    Features available for purchase:
                        Available database size (from <100MB to sqlite3 limit)
                    Method:
                        After purchase and transfer of funds is confirmed, customer will be emailed a receipt with the following:
                            first_name, last_name, email, sale_id, activation_key
                            Instructions to unlock purchased features using "Register" feature in XBRLStudio Help menu
                    IMPORTANT:
                        Run a local app for new sale keygen, then manually email customers their information (must control python version for this)
                        Software major version = 1, Python version = 3.6.1
"""

try:
    import math, decimal, sys, os, datetime, logging
    validator_logger = logging.getLogger()
except Exception as err:
    validator_logger.error("{0}:BookValidator import error:{1}".format(str(datetime.datetime.now()), str(err)))

class BookValidator():
    """
    BookValidator
    ~~~~~~~~~~~~~
    Custom class for generating and validating activation keys

    Functions
    ~~~~~~~~~
    validate(self, sale_id, test_key) - compares a given product activation key against the key expected given the sale_id
    keygen(self, sale_id) - generates a unique 20-character number (string), taking as input sale_id and software_major_version

    Attributes
    ~~~~~~~~~~
    software_major_version (int type) - major version of XBRLStudio
    """
    def __init__(self):
        self.software_major_version = 1

    def validate(self, sale_id, test_key):
        try:
            id_key = self.keygen(sale_id)
            if id_key == test_key:
                return True
            else:
                return False
        except Exception as err:
            validator_logger.error("{0}:BookValidator.validate error:{1}".format(str(datetime.datetime.now()), str(err)))

    def keygen(self, sale_id):
        try:
            if sale_id != "":
                sale_id = int(sale_id)
                sale_pre_key_dec = decimal.Decimal(math.sin(sale_id) + math.sin(self.software_major_version))
                sale_pre_key = str(sale_pre_key_dec).replace("-", "").replace(".","")
                sale_key = ""
                sale_key_scramble = [10, 5, 11, 17, 0, 7, 16, 8, 2, 19, 1, 4, 15, 13, 12, 3, 6, 9, 14, 18]
                for index, item in enumerate(sale_key_scramble):
                    if index in (4, 8, 12, 16):
                        sale_key += "-"
                    sale_key += str(sale_pre_key[item])
                return sale_key
        except Exception as err:
            validator_logger.error("{0}:BookValidator.keygen error:{1}".format(str(datetime.datetime.now()), str(err)))
