"""
:mod: 'BookFilingManager'
~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:module:: BookFilingManager
    :copyright: Copyright BitWorks LLC, All rights reserved.
    :license: MIT
    :synopsis: Manager used by controller instance, interfaces with the utility modules (BookFilingUtility, BookDatabaseUtility)
    :description: Contains the following classes:

        BookFilingManager - primary filing manager used for interfacing with filing and database utility modules; uses a conditional import of BookDatabaseUtility, which triggers the SQLAlchemy ORM, which prepares the Engine and MetaData objects used by db_util functions
"""

try:
    import importlib, os, sys, datetime, logging
    filing_manager_logger = logging.getLogger()
    # Tiered
    from . import (BookFilingUtility, BookView)
    # Flat
    # import BookFilingUtility, BookView
except Exception as err:
    filing_manager_logger.error("{0}:BookFilingManager import error:{1}".format(str(datetime.datetime.now()), str(err)))

class BookFilingManager():
    """
    BookFilingManager
    ~~~~~~~~~~~~~~~~~
    Custom class providing access to utility (Filing and Database) functions, and management of the SQLAlchemy ORM through db_util (re)import, as needed

    Functions
    ~~~~~~~~~
    initDb(self) - initialize database by importing BookDatabaseUtility, which runs the SQLAlchemy ORM module-level code
    getEntityTreeInfo(self) - retrieves entity tree information in the form of a list of tuples, where each tuple is a row [(entity_cik, parent_cik, entity_name)]
    getFilingTreeInfo(self, target_cik) - retrieves filing tree information in the form of a list of strings, where each string corresponds to a filing available for viewing
    updateParentInfo(self, child_cik, parent_cik) - updates the parent_cik for a given child_cik
    importFactFile(self, target_fact_uri) - parses and imports an Arelle-generated fact file into the currently-open database
    manualImportFactFile(self, manual_cik, manual_name, manual_period, target_fact_uri) - given parameters from user, parses and imports an Arelle-generated fact file into the currently-open database
    removeEntity(self, target_cik) - removes an entity and its children from the currently-open database
    removeFiling(self, target_cik, target_period) - removes a filing item and its children from the currently-open database
    getFiling(self, current_cik, current_period) - queries the database and gets a filing, given a cik and period; None otherwise
    getFilingInfo(self, filing) - processes a filing and returns critical information about the filing
    getNameFromCik(self, target_cik) - translates a cik into an entity name from the currently-open database
    getEntityDict(self) - queries the database and returns a dict, where key=entity_name and val=entity_cik (used in BookModel)
    renameEntity(self, target_cik, new_name) - updates the database at cik=target_cik with the new name, new_name

    Attributes
    ~~~~~~~~~~
    book_main_window - (BookView.BookMainWindow type); access to book main window and related functionality
    """

    def __init__(self, book_main_window):
        filing_manager_logger.info("{0}:Initializing BookFilingManager".format(str(datetime.datetime.now())))
        self.book_main_window = book_main_window

    def initDb(self, close = False):
        try:
            global db_util
            try:
                # Tiered
                if "XBRLStudio1.src.BookDatabaseUtility" not in sys.modules:
                # Flat
                # if "BookDatabaseUtility" not in sys.modules:
                    # Tiered
                    from . import BookDatabaseUtility as db_util
                    # Flat
                    # import BookDatabaseUtility as db_util
                db_util.buildEngine(BookView.Global_db_uri)
                if not db_util.tableExists("entities"):
                    db_util.makeEntityTable()
                return True
            except Exception as err:
                filing_manager_logger.error("{0}:BookFilingManager.initDb() inner:{1}".format(str(datetime.datetime.now()), str(err)))
                return False
        except Exception as err:
            filing_manager_logger.error("{0}:BookFilingManager.initDb() outer:{1}".format(str(datetime.datetime.now()), str(err)))
            return False

    def getEntityTreeInfo(self):
        try:
            global db_util
            try:
                entity_tree_info = db_util.getEntityTreeInfo()
                return entity_tree_info
            except Exception as err:
                filing_manager_logger.error("{0}:BookFilingManager.getEntityTreeInfo() inner:{1}".format(str(datetime.datetime.now()), str(err)))
                return
        except Exception as err:
            filing_manager_logger.error("{0}:BookFilingManager.getEntityTreeInfo() outer:{1}".format(str(datetime.datetime.now()), str(err)))

    def getFilingTreeInfo(self, target_cik):
        try:
            global db_util
            try:
                if target_cik is not None:
                    filing_info = db_util.getFilingTreeInfo(target_cik)
                    return filing_info
                else:
                    filing_info = None
                    return filing_info
            except Exception as err:
                filing_manager_logger.error("{0}:BookFilingManager.getFilingTreeInfo() inner:{1}".format(str(datetime.datetime.now()), str(err)))
                return
        except Exception as err:
            filing_manager_logger.error("{0}:BookFilingManager.getFilingTreeInfo() outer:{1}".format(str(datetime.datetime.now()), str(err)))

    def updateParentInfo(self, child_cik, parent_cik):
        try:
            global db_util
            try:
                if child_cik is not None:
                    if db_util.updateEntityParent(child_cik, parent_cik):
                        return True
                    else:
                        return False
                else:
                    return False
            except Exception as err:
                filing_manager_logger.error("{0}:BookFilingManager.updateParentInfo() inner:{1}".format(str(datetime.datetime.now()), str(err)))
                return False
        except Exception as err:
            filing_manager_logger.error("{0}:BookFilingManager.updateParentInfo() outer:{1}".format(str(datetime.datetime.now()), str(err)))

    def importFactFile(self, target_fact_uri, target_cik = None):
        try:
            global db_util
            try:
                pre_existing_filings = db_util.existsInDatabase(target_fact_uri, target_cik)
                if len(pre_existing_filings) >= 1:
                    continue_choice = self.book_main_window.preExistingFilingWarning(pre_existing_filings)
                    if continue_choice is True:
                        db_util.addToDatabase(target_fact_uri, target_cik)
                    else:
                        return
                else:
                    db_util.addToDatabase(target_fact_uri, target_cik)
            except Exception as err:
                filing_manager_logger.error("{0}:BookFilingManager.importFactFile() inner:{1}".format(str(datetime.datetime.now()), str(err)))
                return
        except Exception as err:
            filing_manager_logger.error("{0}:BookFilingManager.importFactFile() outer:{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def manualImportFactFile(self, manual_cik, manual_name, manual_period, target_fact_uri):
        try:
            global db_util
            try:
                pre_existing_filing = db_util.manualExistsInDatabase(manual_cik, manual_period)
                if pre_existing_filing == True:
                    overwrite = self.book_main_window.manualPreExistingFilingWarning(manual_name, manual_period)
                    if overwrite:
                        db_util.manualAddToDatabase(manual_cik, manual_name, manual_period, target_fact_uri)
                    else:
                        return
                else:
                    db_util.manualAddToDatabase(manual_cik, manual_name, manual_period, target_fact_uri)
            except Exception as err:
                filing_manager_logger.error("{0}:BookFilingManager.manualImportFactFile() inner:{1}".format(str(datetime.datetime.now()), str(err)))
        except Exception as err:
            filing_manager_logger.error("{0}:BookFilingManager.manualImportFactFile() outer:{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def removeEntity(self, target_cik):
        try:
            global db_util
            try:
                if target_cik is not None:
                    db_util.removeEntityFromDatabase(self.book_main_window, target_cik, call = 0, total_items = 0)
                else:
                    filing_manager_logger.error("{0}:BookFilingManager.removeEntity() inner:{1}".format(str(datetime.datetime.now()), "target_cik is None"))
            except Exception as err:
                filing_manager_logger.error("{0}:BookFilingManager.removeEntity() middle:{1}".format(str(datetime.datetime.now()), str(err)))
        except Exception as err:
            filing_manager_logger.error("{0}:BookFilingManager.removeEntity() outer:{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def removeFiling(self, target_cik, target_period):
        try:
            global db_util
            try:
                if target_cik is not None and target_period is not None:
                    db_util.removeFilingFromDatabase(self.book_main_window, target_cik, target_period, call = 0, total_items = 0)
                else:
                    filing_manager_logger.error("{0}:BookFilingManager.removeFiling() inner:{1}".format(str(datetime.datetime.now()), "None in target_cik or target_period"))
            except Exception as err:
                filing_manager_logger.error("{0}:BookFilingManager.removeFiling() middle:{1}".format(str(datetime.datetime.now()), str(err)))
        except Exception as err:
            filing_manager_logger.error("{0}:BookFilingManager.removeFiling() outer:{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def getFiling(self, current_cik, current_period):
        try:
            global db_util
            try:
                if current_cik is not None and current_period is not None:
                    filing = db_util.selectFromDatabase(current_cik, current_period)
                    return filing
                else:
                    filing_manager_logger.error("{0}:BookFilingManager.getFiling() inner:{1}".format(str(datetime.datetime.now()), "None in current_cik or current_period"))
                    filing = None
                    return filing
            except Exception as err:
                filing_manager_logger.error("{0}:BookFilingManager.getFiling() middle:{1}".format(str(datetime.datetime.now()), str(err)))
                return None
        except Exception as err:
            filing_manager_logger.error("{0}:BookFilingManager.getFiling() outer:{1}".format(str(datetime.datetime.now()), str(err)))

    def getFilingInfo(self, filing):
        try:
            if filing is not None:
                return BookFilingUtility.getFilingInfo(filing)
            else:
                filing_manager_logger.error("{0}:BookFilingManager.getFiling() inner:{1}".format(str(datetime.datetime.now()), "None in filing"))
                return None
        except Exception as err:
            filing_manager_logger.error("{0}:BookFilingManager.getFilingInfo() outer:{1}".format(str(datetime.datetime.now()), str(err)))

    def getNameFromCik(self, target_cik):
        try:
            global db_util
            try:
                current_name = db_util.getNameFromCik(target_cik)
                return current_name
            except Exception as err:
                filing_manager_logger.error("{0}:BookFilingManager.getNameFromCik() inner:{1}".format(str(datetime.datetime.now()), str(err)))
        except Exception as err:
            filing_manager_logger.error("{0}:BookFilingManager.getNameFromCik() outer:{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def getEntityDict(self):
        try:
            global db_util
            entity_dict = {}
            entity_dict = db_util.getEntityDict()

            return entity_dict
        except Exception as err:
            filing_manager_logger.error("{0}:BookFilingManager.getEntityDict():{1}".format(str(datetime.datetime.now()), str(err)))

    def renameEntity(self, target_cik, new_name):
        try:
            global db_util
            db_util.renameEntityInDatabase(target_cik, new_name)
        except Exception as err:
            filing_manager_logger.error("{0}:BookFilingManager.renameEntity():{1}".format(str(datetime.datetime.now()), str(err)))
