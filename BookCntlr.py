"""
:mod: 'BookCntlr'
~~~~~~~~~~~~~~~~~

..  py:module:: BookCntlr
    :copyright: Copyright BitWorks LLC, All rights reserved.
    :license: MIT
    :synopsis: Main controller used by XBRLStudio, interfaces with Arelle
    :description: Contains the following classes:

        BookCntlr - a QObject that uses python3 and Arelle to convert XBRL files into a single XML fact file, for parsing and import into database
"""
try:
    import subprocess, webbrowser, sys, os, datetime, logging
    cntlr_logger = logging.getLogger()
    from PyQt5 import QtCore
    # Tiered
    from . import (BookFilingManager, BookFilingUtility, BookModel)
    # Flat
    # import BookFilingManager, BookFilingUtility, BookModel
except Exception as err:
    cntlr_logger.error("{0}:BookCntlr import error:{1}".format(str(datetime.datetime.now()), str(err)))

class BookCntlr(QtCore.QObject):
    """
    BookCntlr
    ~~~~~~~~~
    Customized class of QObject; interfaces with Arelle via the python3 interpreter, as well as utility (Filing and Database) functions via the filing manager

    Functions
    ~~~~~~~~~
    newDb(self) - create a new database using the book filing manager
    openDb(self) - open a database using the book filing manager
    closeDb(self) - close current database using the book filing manager
    updateParentInfo(self, child_cik, parent_cik) - sets the parent_cik for the entity with child_cik using the book filing manager
    processXbrl(self, mode, validate, importation, f_list, root_dir) - slot; used for processing Xbrl with options as arguments
    processInstances(self, f_list_instances, validate, importation) - called by processXbrl; imports fact files one by one as Filing objects
    getFiling(self, target_cik, target_period) - query the current database to select a filing, given a cik and period
    getFilingInfo(self, filing) - get critical information about a particular filing
    getNameFromCik(self, target_cik) - translate cik into entity_name
    removeEntity(self, target_cik) - remove an entity and its children from all tables in the current database
    removeFiling(self, filing_selection) - remove a filing item and its children from all tables in the current database
    renameEntity(self, target_cik, new_name) - rename an entity in the current database

    Attributes
    ~~~~~~~~~~
    view_status_bar_update_signal (signal type); implemented to inform the user what the program is currently doing
    processXbrl_finish_signal (signal type); implemented when controller's XBRL processing is completed
    warnUser_signal (signal type); implemented to warn the user whenever something goes awry with XBRL processing or importation
    book_filing_manager (BookFilingManager.BookFilingManager type); manages database connections and utilities, and filing utilities
    book_main_window (BookView.BookMainWindow type); controller's access to main window for application
    in_file (string type); XBRL instance file for the generation of a fact file by Arelle
    out_file (string type); new (temporary) fact file generated by Arelle for parsing and import into database (full path)
    modelManager (Arelle type); XBRL model manager
    fo (Arelle type); file object
    modelXbrl (Arelle type); XBRL model
    path (string type); path to fact_file (from os.path.split)
    fact_file (string type); new (temporary) fact file generated by Arelle for parsing and import into database (from os.path.split)
    """

    view_status_bar_update_signal = QtCore.pyqtSignal(["QString"])
    processXbrl_finish_signal = QtCore.pyqtSignal(["bool"])
    warnUser_signal = QtCore.pyqtSignal(["QString", "QString"])
    manual_import_signal = QtCore.pyqtSignal(["PyQt_PyObject"])
    multiple_cik_signal = QtCore.pyqtSignal(["PyQt_PyObject"])

    def __init__(self, book_main_window):
        cntlr_logger.info("{0}:Initializing BookCntlr".format(str(datetime.datetime.now())))
        QtCore.QObject.__init__(self)
        self.setObjectName("BookCntlr")
        self.book_filing_manager = BookFilingManager.BookFilingManager(book_main_window = book_main_window)
        self.book_main_window = book_main_window
        # Tiered
        self.arelle_cmd_path = os.path.join(self.book_main_window.directories.get("Global_arelle_dir"), "arelleCmdLine.py")
        # Flat
        # self.arelle_cmd_path = os.path.join(os.getcwd(), "res", "Arelle", "arelleCmdLine.py")

    def newDb(self):
        try:
            return self.book_filing_manager.initDb()
        except Exception as err:
            cntlr_logger.error("{0}:BookCntlr.newDb():{1}".format(str(datetime.datetime.now()), str(err)))
            return False

    def openDb(self):
        try:
            return self.book_filing_manager.initDb()
        except Exception as err:
            cntlr_logger.error("{0}:BookCntlr.openDb():{1}".format(str(datetime.datetime.now()), str(err)))
            return False

    def closeDb(self):
        try:
            return self.book_filing_manager.initDb(close = True)
        except Exception as err:
            cntlr_logger.error("{0}:BookCntlr.closeDb():{1}".format(str(datetime.datetime.now()), str(err)))
            return False

    def updateParentInfo(self, child_cik, parent_cik):
        try:
            return self.book_filing_manager.updateParentInfo(child_cik, parent_cik)
        except Exception as err:
            cntlr_logger.error("{0}:BookCntlr.updateParentInfo():{1}".format(str(datetime.datetime.now()), str(err)))
            return False

    #Slot: self.book_main_window.cntlr_processXbrl_start_signal
    def processXbrl(self, mode, validate, importation, f_list, root_dir):
        try:
            f_list_instances = []
            if mode == "File":
                if len(f_list) == 0:
                    return
                for entry in f_list:
                    if BookFilingUtility.isXbrlInstance(entry):
                        f_list_instances.append(entry)
                self.processInstances(f_list_instances, validate, importation)
                if len(self.manual_import_items) > 0:
                    self.manual_import_signal.emit(self.manual_import_items)
                    self.manual_import_items = []
                if len(self.multiple_cik_items) > 0:
                    self.multiple_cik_signal.emit(self.multiple_cik_items)
                    self.multiple_cik_items = []
            elif mode == "Folder":
                if len(root_dir) == 0:
                    return
                if self.book_main_window.pref.import_dir_recursive_option == "Search top folder and sub-folders":
                    for root, dirs, files in os.walk(root_dir):
                        for file in files:
                            if not file.startswith(".") and BookFilingUtility.isXbrlInstance(os.path.join(root, file)):
                                f_list_instances.append(os.path.join(root, file))
                    self.processInstances(f_list_instances, validate, importation)
                    if len(self.manual_import_items) > 0:
                        self.manual_import_signal.emit(self.manual_import_items)
                        self.manual_import_items = []
                    if len(self.multiple_cik_items) > 0:
                        self.multiple_cik_signal.emit(self.multiple_cik_items)
                        self.multiple_cik_items = []
                elif self.book_main_window.pref.import_dir_recursive_option == "Search top folder only":
                    files_folders = os.listdir(root_dir)
                    for item in files_folders:
                        if os.path.isfile(os.path.join(root_dir, item)):
                            if not item.startswith(".") and BookFilingUtility.isXbrlInstance(os.path.join(root_dir, item)):
                                f_list_instances.append(os.path.join(root_dir, item))
                            else:
                                cntlr_logger.error("{0}:BookCntlr.processXbrl():{1}".format(str(datetime.datetime.now()), "invalid file ('.' and instance)"))
                        else:
                            cntlr_logger.error("{0}:BookCntlr.processXbrl():{1}".format(str(datetime.datetime.now()), "invalid file (isfile)"))
                    self.processInstances(f_list_instances, validate, importation)
                    if len(self.manual_import_items) > 0:
                        self.manual_import_signal.emit(self.manual_import_items)
                        self.manual_import_items = []
                    if len(self.multiple_cik_items) > 0:
                        self.multiple_cik_signal.emit(self.multiple_cik_items)
                        self.multiple_cik_items = []
                else:
                    cntlr_logger.error("{0}:BookCntlr.processXbrl():{1}".format(str(datetime.datetime.now()), "invalid import_dir_recursive_option"))
            else:
                cntlr_logger.error("{0}:BookCntlr.processXbrl():{1}".format(str(datetime.datetime.now()), "invalid mode"))
            self.processXbrl_finish_signal.emit(importation)
        except Exception as err:
            cntlr_logger.error("{0}:BookCntlr.processXbrl():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def processInstances(self, f_list_instances, validate, importation):
        Global_python_dir = self.book_main_window.directories.get("Global_python_dir")
        self.manual_import_items = []
        self.multiple_cik_items = []
        try:
            entity_cik = None
            if len(f_list_instances) > 0:
                progress_count = 1
                f_list_count = len(f_list_instances)
                for instance in f_list_instances:
                    progress_count += 1
                    self.in_file = instance
                    self.out_file = os.path.join(self.book_main_window.directories.get("Global_tmp_dir"), os.path.split(self.in_file)[1])
                    if validate == True:
                        commands = [os.path.join(Global_python_dir, "pythonw.exe"), "-B", self.arelle_cmd_path, "-v", "-f", self.in_file]
                        result = subprocess.run(commands)
                    if importation == True:
                        commands = [os.path.join(Global_python_dir, "pythonw.exe"), "-B", self.arelle_cmd_path, "--file={0}".format(self.in_file), "--facts={0}".format(self.out_file)]
                        result = subprocess.run(commands)
                        if os.path.isfile(self.out_file):
                            filing_importable = BookFilingUtility.isImportable(self.out_file)
                            if not filing_importable:
                                self.manual_import_items.append(self.out_file)
                            else:
                                target_filing = BookFilingUtility.parseFactFile(self.out_file)
                                target_cik_list, target_parent_cik, target_name, target_period = BookFilingUtility.getFilingInfo(target_filing)
                                if len(target_cik_list) > 1:
                                    self.multiple_cik_items.append(self.out_file)
                                    self.view_status_bar_update_signal.emit("Importing {0}, {1} of {2} total XBRL filings.".format(os.path.split(self.in_file)[1], progress_count - 1, f_list_count))
                                elif len(target_cik_list) == 1:
                                    entity_cik = target_cik_list[0]
                                    self.view_status_bar_update_signal.emit("Importing {0}, {1} of {2} total XBRL filings.".format(os.path.split(self.in_file)[1], progress_count - 1, f_list_count))
                                    self.book_filing_manager.importFactFile(self.out_file, entity_cik)
                                    os.remove(self.out_file)
                    self.book_main_window.updateProgressBar(int(100 * progress_count / f_list_count))
            else:
                cntlr_logger.error("{0}:BookCntlr.processInstances():{1}".format(str(datetime.datetime.now()), "Processing error - no instances found"))
                self.warnUser_signal.emit("Invalid Selection", "No instances found. Select XBRL instance file(s) to import. Each instance must have a complete DTS in the same directory.")
                return
            self.book_main_window.resetProgressBar()
        except Exception as err:
            cntlr_logger.error("{0}:BookCntlr.processInstances():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def getFiling(self, target_cik, target_period):
        try:
            return self.book_filing_manager.getFiling(target_cik, target_period)
        except Exception as err:
            cntlr_logger.error("{0}:BookCntlr.getFiling():{1}".format(str(datetime.datetime.now()), str(err)))
            return None

    def getFilingInfo(self, filing):
        try:
            return self.book_filing_manager.getFilingInfo(filing)
        except Exception as err:
            cntlr_logger.error("{0}:BookCntlr.getFilingInfo():{1}".format(str(datetime.datetime.now()), str(err)))
            return None

    def getNameFromCik(self, target_cik):
        try:
            return self.book_filing_manager.getNameFromCik(target_cik)
        except Exception as err:
            cntlr_logger.error("{0}:BookCntlr.getNameFromCik():{1}".format(str(datetime.datetime.now()), str(err)))
            return None

    def removeEntity(self, target_cik):
        try:
            self.book_filing_manager.removeEntity(target_cik)
            self.openDb()
            self.book_main_window.refreshAll()
        except Exception as err:
            cntlr_logger.error("{0}:BookCntlr.removeEntity():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def removeFiling(self, filing_selection):
        try:
            current_cik = filing_selection.cik
            if len(filing_selection.period) > 4:
                current_period = filing_selection.period.split("-")[1].lower() + filing_selection.period.split("-")[0]
            else:
                current_period = filing_selection.period
            self.book_filing_manager.removeFiling(current_cik, current_period)
            self.openDb()
            self.book_main_window.refreshAll()
        except Exception as err:
            cntlr_logger.error("{0}:BookCntlr.removeFiling():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def renameEntity(self, target_cik, new_name):
        try:
            self.book_filing_manager.renameEntity(target_cik, new_name)
            self.openDb()
            self.book_main_window.refreshAll()
        except Exception as err:
            cntlr_logger.error("{0}:BookCntlr.renameEntity():{1}".format(str(datetime.datetime.now()), str(err)))
