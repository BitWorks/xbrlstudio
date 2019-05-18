"""
:mod: 'BookView'
~~~~~~~~~~~~~~~~

..  py:module:: BookView
    :copyright: Copyright BitWorks LLC, All rights reserved.
    :license: MIT
    :synopsis: Collection of views used by XBRLStudio
    :description: Contains the following classes:

        BookMainWindow - main GUI window for application
        BookFilingTreeView - filing tree view for viewing filings available for a particular entity
        BookEntityTreeView - entity tree view for viewing entities available for a particular database
        BookStatusBar - status bar indicator for sending brief messages to the interface
        BookTableView - table view for viewing numerical and textual tables
        BookNumericalGraphic - chart graphic for viewing numerical table facts
        BookNumericalChart - QtCharts.QChart type with refresh functionality
        BookTextualGraphic - html graphic for viewing textual table facts
"""
try:
    import webbrowser, sys, os, datetime, logging
    import subprocess
    view_logger = logging.getLogger()
    from PySide2 import (QtWidgets, QtCore)
    from PySide2.QtCharts import QtCharts
    # (QtCharts.QBarSeries, QtCharts.QBarSet, QtCharts.QChart, QtCharts.QChartView, QtCharts.QLineSeries, QtCharts.QScatterSeries)
    from PySide2.QtCore import (QPoint, QPointF)
    from PySide2.QtGui import (QPainter, QColor, QPixmap, QImage)
    from PySide2.QtWidgets import (QApplication, QMainWindow)
    # Tiered
    # from . import (BookModel, BookCntlr, BookFilingManager, BookFilingUtility, BookValidator, BookExportUtility)
    # Flat
    import BookModel, BookCntlr, BookFilingManager, BookFilingUtility, BookValidator, BookExportUtility
except Exception as err:
    view_logger.error("{0}:BookView import error:{1}".format(str(datetime.datetime.now()), str(err)))

# global variable for user-selected database uri
Global_db_uri = ""

class BookMainWindow(QtWidgets.QMainWindow):
    """
    BookMainWindow
    ~~~~~~~~~~~~~~
    Customized sub-class of QMainWindow; instance of this class is the main application window

    Functions
    ~~~~~~~~~
    setupUi(self) - prepares the user interface by instantiating and organizing layouts and widgets
    previousTab(self) - changes focus to previous top-level tab
    nextTab(self) - changes focus to next top-level tab
    renameTab(self, current_index) - dialog-based renaming of the selected top-level tab
    closeTab(self, current_index) - closes current top-level tab
    addNewTab(self, current_index) - adds a new top-level tab
    newDb(self) - dialog-based creation of a new sqlite database
    openDb(self) - dialog-based opening of a pre-existing sqlite database
    closeDb(self) - closes the current sqlite database, resets view
    clearTabs(self) - removes all top-level tabs, replaces with single fresh top-level tab
    preExistingFilingWarning(self, filing_uri) - warns user if importing a pre-existing filing
    manualPreExistingFilingWarning(self, manual_name, manual_period) - warns user if importing a manually-entered pre-existing filing
    fileImport(self) - dialog-based selection of XBRL file to import
    folderImport(self) - dialog-based selection of XBRL folder to import
    exitApplication(self) - closes database and exits the application
    customMenuEntityTreeView(self, position) - custom (right-click) menu for entity tree view
    customMenuFilingTreeView(self, position) - custom (right-click) menu for filing tree view
    customMenuNumericalGraphic(self, position) - custom (right-click) menu for numerical graphic
    customMenuTextualGraphic(self, position) - custom (right-click) menu for textual graphic
    choosePreferences(self) - window for editing general application preferences (see attribute self.pref and class BookPref)
    refreshAll(self, import_successful = False) - refreshes entity and filing treeviews; argument for future implementations
    getManualImportInfo(self, target_uri) - get cik, entity_name, and filing_period from user manual input (maximizes compatibility)
    warnUser(self, title, body) - generic function for warning and/or informing the user
    registerApplication(self) - uses BookValidator.BookValidator() instance and a field input window to "register" the application
    aboutXbrlStudio(self) - displays logo and general information about XBRLStudio
    addTableRows(self) - adds user-defined number of rows to the currently active table
    viewAll(self) - sets all "view" column rows to True; graphs all current table items in the current table graphic
    getInputText(self, title, body) - simple pop-up window that prompts the user for text (e.g., manual cik, entity_name, filing_period)
    getCikCombobox(self, fact_file_list) - simple pip-up window that prompts the user to specify one among more than one cik values found
    updateProgressBar(self, value) - used by expensive functions to update the user regarding progress (e.g., importing XBRL into database)
    resetProgressBar(self) - resets the progress bar to zero
    exportTabHtml(self) - Export currently active textual graphic to html
    exportHtml(self) - Export all textual graphics to html, across all tabs
    exportTabCsv(self) - Export currently active numerical table to csv
    exportCsv(self) - Export all numerical tables to csv, across all tabs

    Attributes
    ~~~~~~~~~~
    cntlr - (BookCntlr.BookCntlr type); provides access to Arelle and other controller functions
    registration - (bool type); holds whether the current copy of XBRLStudio is "registered" or not; determines available functionality
                    registration = False; openDb limited to sqlite database files <= 100MB
                    registration = True; openDb limited to sqlite database file maximum size
    pref - (BookView.BookPref type); holds a list of preferences for the main application window (see class BookPref)
    centralWidget - (QtWidgets.QWidget type); central window widget
    centralWidget_HL - (QtWidgets.QHBoxLayout type); central window widget layout
    centralSplitter - (QtWidgets.QSplitter type); central window widget layout splitter
    selectWidget - (QtWidgets.QWidget type); contains entity and filing tree views
    selectWidget_HL - (QtWidgets.QHBoxLayout type); layout for selectWidget
    selectWidgetSplitter - (QtWidgets.QSplitter type); splitter for selectWidget, dividing entity and filing tree views
    entity_tree_view - (BookEntityTreeView type); tree view displaying entities available in the opened database
    entity_tree_view_model - (BookModel.BookEntityTreeModel type);  model for entity tree view
    entity_tree_view_HL - (QtWidgets.QHBoxLayout type); layout for entity tree view (left of selectWidgetSplitter)
    filing_tree_view - BookFilingTreeView type); tree view displaying filings available in the opened database for the entity selected
    filing_tree_view_model - (BookModel.BookFilingTreeModel type); model for filing tree view
    filing_tree_view_HL - (QtWidgets.QHBoxLayout type); layout for filing tree view (right of selectWidgetSplitter)
    browseWidget - (QtWidgets.QWidget type); contains mainTabWidget and its children
    browseWidget_HL - (QtWidgets.QHBoxLayout type); layout for browseWidget
    menuBar - (QtWidgets.QMenuBar type); main menu bar (top of window)
    status_bar - (BookStatusBar type); main status bar (bottom of window)
    menuFile - (QtWidgets.QMenu type); file menu
        actionNew - (QtWidgets.QAction type); create new database
        actionOpen - (QtWidgets.QAction type); open existing database
        actionClose - (QtWidgets.QAction type); close currently open database
        menuImport - (QtWidgets.QMenu type); import XBRL into currently open database
        actionExport - (QtWidgets.QAction type); export to external file types
        actionImportLocalFiles - (QtWidgets.QAction type); dialog, import XBRL files into currently open database
        actionImportLocalFolder - (QtWidgets.QAction type); dialog, import XBRL files within a folder
        actionExit - (QtWidgets.QAction type); close any current database and exit the application
    menuEdit - (QtWidgets.QMenu type); edit menu
        actionUndo - (QtWidgets.QAction type); undo last action
        actionRedo - (QtWidgets.QAction type); redo last action
        actionCut - (QtWidgets.QAction type); delete selection and place in clipboard
        actionCopy - (QtWidgets.QAction type); copy selection and place in clipboard
        actionPaste - (QtWidgets.QAction type); paste from clipboard to cursor location
        actionDelete - (QtWidgets.QAction type); delete at cursor location
        actionSelectAll - (QtWidgets.QAction type); select all text within the active widget
    menuView - (QtWidgets.QMenu type); view menu
        actionNewTab - (QtWidgets.QAction type); create new, empty tab at the end of the available tabs
        actionPreviousTab - (QtWidgets.QAction type); move focus to previous tab
        actionNextTab - (QtWidgets.QAction type); move focus to next tab
        actionCloseTab - (QtWidgets.QAction type); close tab at current focus
    menuWindow - (QtWidgets.QMenu type); window menu
        actionMaximize - (QtWidgets.QAction type); maximize main window
        actionMinimize - (QtWidgets.QAction type); minimize main window
        actionMinimizeAll - (QtWidgets.QAction type); minimize all active XBRLStudio windows
    menuHelp - (QtWidgets.QMenu type); help menu
        actionAboutXbrlStudio - (QtWidgets.QAction type); display information about XBRLStudio
    plusTab - (QtWidgets.QWidget type); tab which, when brought into focus, creates a new tab and changes focus to the new tab
    current_tab_count - (int type); integer containing number of top-level tabs
    newTab - (QtWidgets.QWidget type); main tab containing table and graphic objects
    newTab_VL - (QtWidgets.QVBoxLayout type); layout for newTab
    newTab_subTabWidget - (QtWidgets.QTabWidget type); sub-tab object for numerical/textual division of facts
    newTab_numericalTab - (QtWidgets.QWidget type); tab containing numerical table and graphic
    newTab_numericalTab_VL - (QtWidgets.QVBoxLayout type); layout for numerical tab
    newTab_numericalSplitter - (QtWidgets.QSplitter type); splitter for numerical tab (top = table; bottom = graphic)
    newTab_numericalTableFrame - (QtWidgets.QFrame type); frame for numerical table
    newTab_numericalTableFrame_VL - (QtWidgets.QVBoxLayout type); layout for numerical table frame
    newTab_numericalTableView - (BookTableView type); view of numerical table model
    newTab_numericalTableHeader - (QtWidgets.QHeaderView type); header for numerical table
    newTab_numericalTableModel - (BookModel.BookTableModel type); numerical table model
    newTab_numericalTableViewDelegate - (BookModel.BookTableViewDelegate type); delegate for numerical table view
    newTab_numericalGraphicFrame - (QtWidgets.QFrame type); frame for numerical graphic
    newTab_numericalGraphicFrame_VL - (QtWidgets.QVBoxLayout type); layout for numerical graphic frame
    newTab_numericalGraphicChart - (BookNumericalChart type); chart visualization for numerical graphic
    newTab_numericalGraphic - (BookNumericalGraphic type); numerical graphic containing chart
    newTab_textualTab - (QtWidgets.QWidget type); tab containing textual table and graphic
    newTab_textualTab_VL - (QtWidgets.QVBoxLayout type); layout for textual tab
    newTab_textualSplitter - (QtWidgets.QSplitter type); splitter for textual tab (top = table; bottom = graphic)
    newTab_textualTableFrame - (QtWidgets.QFrame type); frame for textual table
    newTab_textualTableFrame_VL - (QtWidgets.QVBoxLayout type); layout for textual table frame
    newTab_textualTableView - (BookTableView type); view of textual table model
    newTab_textualTableHeader - (QtWidgets.QHeaderView type); header for textual table
    newTab_textualTableModel - (BookModel.BookTableModel type); textual table model
    newTab_textualTableViewDelegate - (BookModel.BookTableViewDelegate type); delegate for textual table view
    newTab_textualGraphicFrame - (QtWidgets.QFrame type); frame for textual graphic
    newTab_textualGraphicFrame_VL - (QtWidgets.QVBoxLayout type); layout for textual graphic frame
    newTab_textualGraphic - (BookTextualGraphic type); textual graphic containing embedded browser
    """

    # cntlr_processXbrl_start_signal = QtCore.pyqtSignal("QString", "bool", "bool", "PyQt_PyObject", "QString")
    cntlr_processXbrl_start_signal = QtCore.Signal("QString", "bool", "bool", "QObject", "QString")

    def __init__(self, directories, registration):
        view_logger.info("{0}:Initializing BookMainWindow".format(str(datetime.datetime.now())))
        QtWidgets.QMainWindow.__init__(self)
        self.directories = directories
        """self.directories
                        {"Global_app_dir":Global_app_dir,
                        "Global_tmp_dir":Global_tmp_dir,
                        "Global_log_dir":Global_log_dir,
                        "Global_key_dir":Global_key_dir,
                        "Global_res_dir":Global_res_dir,
                        "Global_img_dir":Global_img_dir,
                        "Global_doc_dir":Global_doc_dir,
                        "Global_python_dir":Global_python_dir,
                        "Global_arelle_dir":Global_arelle_dir}
        """
        # print(self.directories)
        self.registration = registration #boolean; True = registered; False = unregistered
        self.setupUi()
        self.setObjectName("BookMainWindow")

        self.cntlr_processXbrl_start_signal.connect(self.cntlr.processXbrl)
        self.cntlr.view_status_bar_update_signal.connect(self.statusBar().showMessage)
        self.cntlr.processXbrl_finish_signal.connect(self.refreshAll)
        self.cntlr.warnUser_signal.connect(self.warnUser)
        self.cntlr.manual_import_signal.connect(self.manualImport)
        self.cntlr.multiple_cik_signal.connect(self.getCikCombobox)

    def setupUi(self):
        try:
            self.setWindowTitle("XBRLStudio")
            self.resize(1050, 700)
            self.cntlr = BookCntlr.BookCntlr(book_main_window = self)
            self.book_filing_manager = BookFilingManager.BookFilingManager(book_main_window = self)
            self.pref = BookPref(book_main_window = self)
            self.book_exporter = BookExportUtility.BookExporter(book_main_window = self)
            self.centralWidget = QtWidgets.QWidget(self)
            self.centralWidget_HL = QtWidgets.QHBoxLayout(self.centralWidget)
            self.centralWidget_HL.setSpacing(0)
            self.centralWidget_HL.setContentsMargins(0, 0, 0, 0)
            self.centralWidget.setLayout(self.centralWidget_HL)

            self.centralSplitter = QtWidgets.QSplitter(self.centralWidget)
            self.centralSplitter.setOrientation(QtCore.Qt.Horizontal)
            self.centralWidget_HL.addWidget(self.centralSplitter)

            self.selectWidget = QtWidgets.QWidget(self.centralWidget)
            self.selectWidget_VL = QtWidgets.QVBoxLayout(self.selectWidget)
            self.selectWidget_VL.setSpacing(0)
            self.selectWidget_VL.setContentsMargins(0, 0, 0, 0)
            self.selectWidget.setLayout(self.selectWidget_VL)

            self.selectWidgetSplitter = QtWidgets.QSplitter(self.selectWidget)
            self.selectWidgetSplitter.setOrientation(QtCore.Qt.Horizontal)
            self.selectWidget_VL.addWidget(self.selectWidgetSplitter)

            self.entity_tree_view = BookEntityTreeView(self)
            self.entity_tree_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.entity_tree_view_model = BookModel.BookEntityTreeModel(self)
            self.entity_tree_view_model.setHorizontalHeaderLabels(["Entity"])
            self.entity_tree_view.setModel(self.entity_tree_view_model)
            self.entity_tree_view.header().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
            self.entity_tree_view.header().setSectionsMovable(True)
            self.entity_tree_view.setUniformRowHeights(False)
            self.entity_tree_view_HL = QtWidgets.QHBoxLayout(self.entity_tree_view)
            self.entity_tree_view_HL.setSpacing(0)
            self.entity_tree_view_HL.setContentsMargins(0, 0, 0, 0)
            self.entity_tree_view.setLayout(self.entity_tree_view_HL)
            self.selectWidgetSplitter.addWidget(self.entity_tree_view)
            self.entity_tree_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.entity_tree_view.customContextMenuRequested.connect(self.customMenuEntityTreeView)

            self.filing_tree_view = BookFilingTreeView(self)
            self.filing_tree_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.filing_tree_view_model = BookModel.BookFilingTreeModel(self)
            self.filing_tree_view_model.setHorizontalHeaderLabels(["Filing"])
            self.filing_tree_view.setModel(self.filing_tree_view_model)
            self.filing_tree_view.header().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
            self.filing_tree_view.setUniformRowHeights(True)
            self.filing_tree_view_HL = QtWidgets.QHBoxLayout(self.filing_tree_view)
            self.filing_tree_view_HL.setSpacing(0)
            self.filing_tree_view_HL.setContentsMargins(0, 0, 0, 0)
            self.filing_tree_view.setLayout(self.filing_tree_view_HL)
            self.selectWidgetSplitter.addWidget(self.filing_tree_view)
            self.filing_tree_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.filing_tree_view.customContextMenuRequested.connect(self.customMenuFilingTreeView)

            self.browseWidget = QtWidgets.QWidget(self.centralWidget)
            self.browseWidget_HL = QtWidgets.QHBoxLayout(self.browseWidget)
            self.browseWidget_HL.setSpacing(0)
            self.browseWidget_HL.setContentsMargins(0, 0, 0, 0)
            self.browseWidget.setLayout(self.browseWidget_HL)

            self.mainTabWidget = QtWidgets.QTabWidget(self.browseWidget)
            self.mainTabWidget.setTabsClosable(True)
            self.mainTabWidget.setMovable(False)
            self.browseWidget_HL.addWidget(self.mainTabWidget)

            self.centralSplitter.addWidget(self.selectWidget)
            self.centralSplitter.addWidget(self.browseWidget)
            self.centralSplitter.setSizes([300, 600])

            self.setCentralWidget(self.centralWidget)
            self.addNewTab(-1)

            #Menu bar
            self.menu_bar = QtWidgets.QMenuBar(self)
            self.menu_bar.setGeometry(QtCore.QRect(0, 0, 1000, 22))
            self.setMenuBar(self.menu_bar)

            #Status bar
            self.status_bar = BookStatusBar(self)
            self.setStatusBar(self.status_bar)

            #Progress bar
            self.progressBar = QtWidgets.QProgressBar(self)
            self.progressBar_sizePolicy = QtWidgets.QSizePolicy()
            self.progressBar_sizePolicy.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
            self.progressBar_sizePolicy.setHorizontalStretch(0)
            self.progressBar_sizePolicy.setVerticalStretch(0)
            self.progressBar_sizePolicy.setHeightForWidth(False)
            self.progressBar.setSizePolicy(self.progressBar_sizePolicy)
            self.selectWidget_VL.addWidget(self.progressBar)
            self.resetProgressBar()

            #File
            self.menuFile = QtWidgets.QMenu("File", self.menuBar())
            self.actionNew = QtWidgets.QAction("New Database", self)
            self.actionNew.triggered.connect(self.newDb)
            self.menuFile.addAction(self.actionNew)
            self.actionOpen = QtWidgets.QAction("Open Database", self)
            self.actionOpen.triggered.connect(self.openDb)
            self.menuFile.addAction(self.actionOpen)
            self.actionClose = QtWidgets.QAction("Close Database", self)
            self.actionClose.triggered.connect(self.closeDb)
            self.menuFile.addAction(self.actionClose)
            self.menuFile.addSeparator()
            self.menuImport = QtWidgets.QMenu("Import", self.menuFile)
            self.menuFile.addAction(self.menuImport.menuAction())
            self.menuExport = QtWidgets.QMenu("Export", self.menuFile)
            self.menuFile.addAction(self.menuExport.menuAction())
            self.menuFile.addSeparator()
            self.actionImportLocalFiles = QtWidgets.QAction("File(s)", self.menuFile)
            self.actionImportLocalFiles.triggered.connect(self.fileImport)
            self.menuImport.addAction(self.actionImportLocalFiles)
            self.actionImportLocalFolder = QtWidgets.QAction("Folder", self.menuFile)
            self.actionImportLocalFolder.triggered.connect(self.folderImport)
            self.menuImport.addAction(self.actionImportLocalFolder)
            self.actionExportTabHtml = QtWidgets.QAction("Current Textual Graphic to HTML", self.menuFile)
            self.actionExportTabHtml.triggered.connect(self.exportTabHtml)
            self.menuExport.addAction(self.actionExportTabHtml)
            self.actionExportHtml = QtWidgets.QAction("All Textual Graphics to HTML", self.menuFile)
            self.actionExportHtml.triggered.connect(self.exportHtml)
            self.menuExport.addAction(self.actionExportHtml)
            self.actionExportTabCsv = QtWidgets.QAction("Current Numerical Table to CSV", self.menuFile)
            self.actionExportTabCsv.triggered.connect(self.exportTabCsv)
            self.menuExport.addAction(self.actionExportTabCsv)
            self.actionExportCsv = QtWidgets.QAction("All Numerical Tables to CSV", self.menuFile)
            self.actionExportCsv.triggered.connect(self.exportCsv)
            self.menuExport.addAction(self.actionExportCsv)
            self.menuFile.addSeparator()
            self.actionPreferences = QtWidgets.QAction("Preferences", self.menuFile)
            self.actionPreferences.triggered.connect(self.choosePreferences)
            self.menuFile.addAction(self.actionPreferences)
            self.menuFile.addSeparator()
            self.actionExit = QtWidgets.QAction("Exit", self.menuFile)
            self.actionExit.triggered.connect(self.exitApplication)
            self.menuFile.addAction(self.actionExit)
            self.actionExportTabHtml.setEnabled(True)
            self.actionExportHtml.setEnabled(True)
            self.actionExportTabCsv.setEnabled(True)
            self.actionExportCsv.setEnabled(True)

            #Edit
            self.menuEdit = QtWidgets.QMenu("Edit", self.menuBar())
            self.actionUndo = QtWidgets.QAction("Undo", self)
            self.menuEdit.addAction(self.actionUndo)
            self.actionRedo = QtWidgets.QAction("Redo", self)
            self.menuEdit.addAction(self.actionRedo)
            self.menuEdit.addSeparator()
            self.actionCut = QtWidgets.QAction("Cut", self)
            self.menuEdit.addAction(self.actionCut)
            self.actionCopy = QtWidgets.QAction("Copy", self)
            self.menuEdit.addAction(self.actionCopy)
            self.actionPaste = QtWidgets.QAction("Paste", self)
            self.menuEdit.addAction(self.actionPaste)
            self.actionDelete = QtWidgets.QAction("Delete", self)
            self.menuEdit.addAction(self.actionDelete)
            self.menuEdit.addSeparator()
            self.actionSelectAll = QtWidgets.QAction("Select All", self)
            self.menuEdit.addAction(self.actionSelectAll)

            #View
            self.menuView = QtWidgets.QMenu("View", self.menuBar())
            self.menuTab = QtWidgets.QMenu("Tab", self.menuView)
            self.menuView.addAction(self.menuTab.menuAction())
            self.actionNewTab = QtWidgets.QAction("New", self)
            self.actionNewTab.triggered.connect(lambda x: self.addNewTab(self.mainTabWidget.count() - 1))
            self.menuTab.addAction(self.actionNewTab)
            self.actionPreviousTab = QtWidgets.QAction("Previous", self)
            self.actionPreviousTab.triggered.connect(self.previousTab)
            self.menuTab.addAction(self.actionPreviousTab)
            self.actionNextTab = QtWidgets.QAction("Next", self)
            self.actionNextTab.triggered.connect(self.nextTab)
            self.menuTab.addAction(self.actionNextTab)
            self.actionCloseTab = QtWidgets.QAction("Close", self)
            self.actionCloseTab.triggered.connect(lambda x: self.closeTab(self.mainTabWidget.currentIndex()))
            self.menuTab.addAction(self.actionCloseTab)

            self.menuTable = QtWidgets.QMenu("Table", self.menuView)
            self.menuView.addAction(self.menuTable.menuAction())
            self.actionAddRows = QtWidgets.QAction("Add Rows", self)
            self.actionAddRows.triggered.connect(self.addTableRows)
            self.menuTable.addAction(self.actionAddRows)

            self.menuGraphic = QtWidgets.QMenu("Graphic", self.menuView)
            self.menuView.addAction(self.menuGraphic.menuAction())
            self.actionViewAll = QtWidgets.QAction("View All", self)
            self.actionViewAll.triggered.connect(self.viewAll)
            self.menuGraphic.addAction(self.actionViewAll)

            #Window
            self.menuWindow = QtWidgets.QMenu("Window", self.menuBar())
            self.actionMaximize = QtWidgets.QAction("Maximize", self)
            self.actionMaximize.triggered.connect(lambda x: self.showMaximized())
            self.menuWindow.addAction(self.actionMaximize)
            self.actionMinimize = QtWidgets.QAction("Minimize", self)
            self.actionMinimize.triggered.connect(lambda x: self.showMinimized())
            self.menuWindow.addAction(self.actionMinimize)

            #Help
            self.menuHelp = QtWidgets.QMenu("Help", self.menuBar())
            self.actionHelp = QtWidgets.QAction("Website", self)
            self.actionHelp.triggered.connect(lambda x: webbrowser.open("https://xbrlstudio.com/", new = 2, autoraise = True))
            self.menuHelp.addAction(self.actionHelp)
            self.actionRegister = QtWidgets.QAction("Register", self)
            self.actionRegister.triggered.connect(self.registerApplication)
            self.menuHelp.addAction(self.actionRegister)
            self.actionAboutXbrlStudio = QtWidgets.QAction("About XBRLStudio", self)
            self.actionAboutXbrlStudio.triggered.connect(lambda x: self.aboutXbrlStudio())
            self.menuHelp.addAction(self.actionAboutXbrlStudio)

            #Enable menus
            self.menuBar().addAction(self.menuFile.menuAction())
            self.menuBar().addAction(self.menuEdit.menuAction())
            self.menuBar().addAction(self.menuView.menuAction())
            self.menuBar().addAction(self.menuWindow.menuAction())
            self.menuBar().addAction(self.menuHelp.menuAction())

            #Plus tab
            self.plusTab = QtWidgets.QWidget(self.mainTabWidget)
            self.plusTab.setObjectName("plusTab")
            self.mainTabWidget.addTab(self.plusTab, "+")
            #Hide "close tab" button on plusTab
            if sys.platform.startswith("win") or sys.platform.startswith("linux"):
                try:
                    self.mainTabWidget.tabBar().tabButton(1, QtWidgets.QTabBar.RightSide).hide()
                except Exception as err:
                    view_logger.error("{0}:BookMainWindow.setupUi():{1}".format(str(datetime.datetime.now()), str(err)))
            elif sys.platform.startswith("darwin"):
                try:
                    self.mainTabWidget.tabBar().tabButton(1, QtWidgets.QTabBar.LeftSide).hide()
                except Exception as err:
                    view_logger.error("{0}:BookMainWindow.setupUi():{1}".format(str(datetime.datetime.now()), str(err)))
            else:
                view_logger.error("{0}:BookMainWindow.setupUi():{1}".format(str(datetime.datetime.now()), "OS not in (win, linux, darwin)"))

            self.mainTabWidget.setCurrentIndex(0)
            self.mainTabWidget.tabBarClicked.connect(self.addNewTab)
            self.mainTabWidget.tabBarDoubleClicked.connect(self.renameTab)
            self.mainTabWidget.tabCloseRequested.connect(self.closeTab)

            QtCore.QMetaObject.connectSlotsByName(self)
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.setupUi():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def previousTab(self):
        try:
            self.mainTabWidget.setCurrentIndex(self.mainTabWidget.currentIndex() - 1)
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.previousTab():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def nextTab(self):
        try:
            self.current_tab_count = self.mainTabWidget.count()
            if self.mainTabWidget.currentIndex() == self.current_tab_count - 2:
                return
            else:
                self.mainTabWidget.setCurrentIndex(self.mainTabWidget.currentIndex() + 1)
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.nextTab():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def renameTab(self, current_index):
        try:
            if current_index == self.mainTabWidget.count() - 1:
                return
            self.new_tab_name_tuple = QtWidgets.QInputDialog.getText(self.mainTabWidget, "Rename Tab", "New Tab Name:",
                                                     QtWidgets.QLineEdit.Normal, self.mainTabWidget.tabText(current_index))
            if self.new_tab_name_tuple[1] is True:
                self.mainTabWidget.setTabText(current_index, self.new_tab_name_tuple[0])
                self.mainTabWidget.widget(current_index).setObjectName(self.new_tab_name_tuple[0])
                self.newTab_numericalGraphic.refreshGraphic()
                self.newTab_textualGraphic.refreshGraphic()
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.renameTab():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def closeTab(self, current_index):
        try:
            if current_index == self.mainTabWidget.count() - 1:
                return
            elif current_index == self.mainTabWidget.count() - 2:
                self.mainTabWidget.removeTab(current_index)
                self.mainTabWidget.setCurrentIndex(current_index - 1)
            else:
                self.mainTabWidget.removeTab(current_index)
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.closeTab():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def addNewTab(self, current_index):
        try:
            self.current_tab_count = self.mainTabWidget.count()
            if current_index == self.current_tab_count - 1:
                self.newTab = QtWidgets.QWidget(self.mainTabWidget)
                self.newTab.setObjectName("New Tab")
                self.newTab_VL = QtWidgets.QVBoxLayout(self.newTab)
                self.newTab_VL.setSpacing(0)
                self.newTab_VL.setContentsMargins(0, 0, 0, 0)
                self.newTab_subTabWidget = QtWidgets.QTabWidget(self.newTab)
                self.newTab_subTabWidget.setObjectName("newTab_subTabWidget")
                self.newTab_numericalTab = QtWidgets.QWidget(self.newTab_subTabWidget)
                self.newTab_numericalTab.setObjectName("newTab_numericalTab")
                self.newTab_numericalTab_VL = QtWidgets.QVBoxLayout(self.newTab_numericalTab)
                self.newTab_numericalTab_VL.setSpacing(0)
                self.newTab_numericalTab_VL.setContentsMargins(0, 0, 0, 0)
                self.newTab_numericalSplitter = QtWidgets.QSplitter(self.newTab_numericalTab)
                self.newTab_numericalSplitter.setOrientation(QtCore.Qt.Vertical)
                self.newTab_numericalTableFrame = QtWidgets.QFrame(self.newTab_numericalSplitter)
                self.newTab_numericalTableFrame.setObjectName("numericalTableFrame")
                self.newTab_numericalTableFrame_VL = QtWidgets.QVBoxLayout(self.newTab_numericalTableFrame)
                self.newTab_numericalTableFrame_VL.setObjectName("numericalTableFrame_VL")
                self.newTab_numericalTableFrame_VL.setSpacing(0)
                self.newTab_numericalTableFrame_VL.setContentsMargins(0, 0, 0, 0)

                #Numerical table
                self.newTab_numericalTableView = BookTableView(self.newTab_numericalTableFrame, book_main_window = self)
                self.newTab_numericalTableView.setObjectName("numericalTableView")
                self.newTab_numericalTableHeader = QtWidgets.QHeaderView(QtCore.Qt.Horizontal, self.newTab_numericalTableView)
                self.newTab_numericalTableHeader.setMinimumSectionSize(45)
                self.newTab_numericalTableView.setHorizontalHeader(self.newTab_numericalTableHeader)
                self.newTab_numericalTableHeader.setStretchLastSection(True)
                self.newTab_numericalTableModel = BookModel.BookTableModel(self.newTab_numericalTableView)
                self.newTab_numericalTableView.setModel(self.newTab_numericalTableModel)
                self.newTab_numericalTableFrame_VL.addWidget(self.newTab_numericalTableView)
                self.newTab_numericalTableView.resizeColumnsToContents()
                self.newTab_numericalTableView.resizeRowsToContents()
                self.newTab_numericalTableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
                self.newTab_numericalTableView.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
                self.newTab_numericalTableView.setCornerButtonEnabled(True)

                if self.pref.general_show_decimal_column == "Yes":
                    try:
                        self.newTab_numericalTableView.showColumn(7)
                    except Exception as err:
                        pass
                elif self.pref.general_show_decimal_column == "No":
                    try:
                        self.newTab_numericalTableView.hideColumn(7)
                    except Exception as err:
                        pass

                #Numerical table delegate
                self.newTab_numericalTableViewDelegate = BookModel.BookTableViewDelegate(self.newTab_numericalTableView)
                self.newTab_numericalTableView.setItemDelegate(self.newTab_numericalTableViewDelegate)

                #Persistent view checkbox
                for view_index in self.newTab_numericalTableView.model().view_indices:
                    if view_index.isValid():
                        self.newTab_numericalTableView.openPersistentEditor(view_index)

                #Numerical table signals
                self.newTab_numericalTableView.clicked.connect(self.newTab_numericalTableView.edit)

                self.newTab_numericalGraphicFrame = QtWidgets.QFrame(self.newTab_numericalSplitter)
                self.newTab_numericalGraphicFrame_VL = QtWidgets.QVBoxLayout(self.newTab_numericalGraphicFrame)
                self.newTab_numericalGraphicFrame_VL.setSpacing(0)
                self.newTab_numericalGraphicFrame_VL.setContentsMargins(0, 0, 0, 0)

                #Numerical graphic
                self.newTab_numericalGraphicChart = BookNumericalChart(self.newTab_numericalTableView)
                self.newTab_numericalGraphic = BookNumericalGraphic(self.newTab_numericalTableView)
                self.newTab_numericalGraphic.setChart(self.newTab_numericalGraphicChart)
                self.newTab_numericalGraphic_sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
                self.newTab_numericalGraphic_sizePolicy.setHorizontalStretch(0)
                self.newTab_numericalGraphic_sizePolicy.setVerticalStretch(0)
                self.newTab_numericalGraphic_sizePolicy.setHeightForWidth(self.newTab_numericalGraphic.sizePolicy().hasHeightForWidth())
                self.newTab_numericalGraphic.setSizePolicy(self.newTab_numericalGraphic_sizePolicy)
                self.newTab_numericalGraphic.setObjectName("numericalGraphic")
                self.newTab_numericalTableView.graphic = self.newTab_numericalGraphic
                self.newTab_numericalGraphicFrame_VL.addWidget(self.newTab_numericalGraphic)
                self.newTab_numericalGraphic.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                self.newTab_numericalGraphic.customContextMenuRequested.connect(self.customMenuNumericalGraphic)

                self.newTab_numericalTab_VL.addWidget(self.newTab_numericalSplitter)
                self.newTab_subTabWidget.addTab(self.newTab_numericalTab, "Numerical")

                self.newTab_textualTab = QtWidgets.QWidget(self.newTab_subTabWidget)
                self.newTab_textualTab.setObjectName("newTab_textualTab")
                self.newTab_textualTab_VL = QtWidgets.QVBoxLayout(self.newTab_textualTab)
                self.newTab_textualTab_VL.setSpacing(0)
                self.newTab_textualTab_VL.setContentsMargins(0, 0, 0, 0)
                self.newTab_textualSplitter = QtWidgets.QSplitter(self.newTab_textualTab)
                self.newTab_textualSplitter.setOrientation(QtCore.Qt.Vertical)
                self.newTab_textualTableFrame = QtWidgets.QFrame(self.newTab_textualSplitter)
                self.newTab_textualTableFrame.setObjectName("textualTableFrame")
                self.newTab_textualTableFrame_VL = QtWidgets.QVBoxLayout(self.newTab_textualTableFrame)
                self.newTab_textualTableFrame_VL.setSpacing(0)
                self.newTab_textualTableFrame_VL.setContentsMargins(0, 0, 0, 0)

                #Textual table
                self.newTab_textualTableView = BookTableView(self.newTab_textualTableFrame, book_main_window = self)
                self.newTab_textualTableView.setObjectName("textualTableView")
                self.newTab_textualTableHeader = QtWidgets.QHeaderView(QtCore.Qt.Horizontal, self.newTab_textualTableView)
                self.newTab_textualTableHeader.setMinimumSectionSize(45)
                self.newTab_textualTableView.setHorizontalHeader(self.newTab_textualTableHeader)
                self.newTab_textualTableHeader.setStretchLastSection(True)
                self.newTab_textualTableModel = BookModel.BookTableModel(self.newTab_textualTableView)
                self.newTab_textualTableView.setModel(self.newTab_textualTableModel)
                self.newTab_textualTableFrame_VL.addWidget(self.newTab_textualTableView)
                self.newTab_textualTableView.resizeColumnsToContents()
                self.newTab_textualTableView.resizeRowsToContents()
                self.newTab_textualTableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
                self.newTab_textualTableView.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
                self.newTab_textualTableView.setCornerButtonEnabled(True)

                #Textual table delegate
                self.newTab_textualTableViewDelegate = BookModel.BookTableViewDelegate(self.newTab_textualTableView)
                self.newTab_textualTableView.setItemDelegate(self.newTab_textualTableViewDelegate)

                #Persistent view checkbox
                for view_index in self.newTab_textualTableView.model().view_indices:
                    if view_index.isValid():
                        self.newTab_textualTableView.openPersistentEditor(view_index)

                #Textual table signals
                self.newTab_textualTableView.clicked.connect(self.newTab_textualTableView.edit)

                self.newTab_textualGraphicFrame = QtWidgets.QFrame(self.newTab_textualSplitter)
                self.newTab_textualGraphicFrame_VL = QtWidgets.QVBoxLayout(self.newTab_textualGraphicFrame)
                self.newTab_textualGraphicFrame_VL.setSpacing(0)
                self.newTab_textualGraphicFrame_VL.setContentsMargins(0, 0, 0, 0)

                #Textual graphic
                self.newTab_textualGraphic = BookTextualGraphic(book_table_view = self.newTab_textualTableView)
                self.newTab_textualGraphic_sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
                self.newTab_textualGraphic_sizePolicy.setHorizontalStretch(0)
                self.newTab_textualGraphic_sizePolicy.setVerticalStretch(0)
                self.newTab_textualGraphic_sizePolicy.setHeightForWidth(self.newTab_textualGraphic.sizePolicy().hasHeightForWidth())
                self.newTab_textualGraphic.setSizePolicy(self.newTab_textualGraphic_sizePolicy)
                # self.newTab_textualGraphic.setUrl(QtCore.QUrl("about:blank"))
                self.newTab_textualTableView.graphic = self.newTab_textualGraphic
                self.newTab_textualGraphicFrame_VL.addWidget(self.newTab_textualGraphic)
                self.newTab_textualGraphic.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                self.newTab_textualGraphic.customContextMenuRequested.connect(self.customMenuTextualGraphic)

                self.newTab_textualTab_VL.addWidget(self.newTab_textualSplitter)
                self.newTab_subTabWidget.addTab(self.newTab_textualTab, "Textual")
                self.newTab_VL.addWidget(self.newTab_subTabWidget)
                self.mainTabWidget.insertTab(self.current_tab_count - 1, self.newTab, "New Tab")
                self.newTab_numericalSplitter.setSizes([193, 207])
                self.newTab_textualSplitter.setSizes([193, 207])
                self.mainTabWidget.setCurrentIndex(self.mainTabWidget.count() - 2)
                self.newTab_subTabWidget.setCurrentIndex(0)

                #Initialize graphics
                self.newTab_numericalGraphic.refreshGraphic()
                self.newTab_textualGraphic.refreshGraphic()
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.addNewTab():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def newDb(self):
        try:
            global Global_db_uri
            Global_db_uri = QtWidgets.QFileDialog.getSaveFileName(caption = "New database",
                                  directory = "C:\\",
                                  filter = "SQLite (*.sqlite)",
                                  options = QtWidgets.QFileDialog.DontConfirmOverwrite)[0]
            if Global_db_uri != "":
                if Global_db_uri.split(os.sep)[-1] != "":
                    file_name = Global_db_uri.split(os.sep)[-1]
                if "." in file_name:
                    if file_name[0] == ".":
                        hidden_file_choice = QtWidgets.QMessageBox.warning(self,
                                                       "Database name confirmation",
                                                       "Are you sure you want to create database {0}".format(Global_db_uri.split(os.sep)[-1]),
                                                       QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                                                       QtWidgets.QMessageBox.Cancel)
                        if hidden_file_choice == QtWidgets.QMessageBox.Cancel:
                            return
                    if file_name.split(".")[-1] != "sqlite":
                        file_name += ".sqlite"
                        Global_db_uri += ".sqlite"
                elif "." not in file_name:
                    file_name += ".sqlite"
                    Global_db_uri += ".sqlite"
            if os.path.isfile(Global_db_uri):
                overwrite_choice = QtWidgets.QMessageBox.warning(self,
                                               "Overwrite database?",
                                               "Are you sure you want to overwrite {0}?".format(Global_db_uri.split(os.sep)[-1]),
                                               QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                                               QtWidgets.QMessageBox.Cancel)
                if overwrite_choice == QtWidgets.QMessageBox.Ok:
                    os.remove(Global_db_uri)
                else:
                    return
            if self.cntlr.newDb() is True and Global_db_uri != "":
                self.setWindowTitle("{0} - XBRLStudio".format(os.path.split(Global_db_uri)[1].split(".")[0]))
                self.entity_tree_view.refresh()
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.newDb():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def openDb(self):
        try:
            global Global_db_uri
            temp_db_uri = Global_db_uri
            Global_db_uri = QtWidgets.QFileDialog.getOpenFileName(caption = "Open database",
                                  directory = "C:\\",
                                  filter = "SQLite (*.sqlite)")[0]
            if temp_db_uri != Global_db_uri:
                self.cntlr.closeDb()
            if os.path.isfile(Global_db_uri):
                try:
                    if self.registration is False and os.path.getsize(Global_db_uri) > 100000000:
                            self.warnUser("Database Too Large",
                            "This database is too large for the free version of XBRLStudio.\n\nPlease visit xbrlstudio.com and buy a commercial license to open databases greater than 100 MB in size.")
                            return
                    else:
                        self.cntlr.openDb()
                        self.setWindowTitle("{0} - XBRLStudio".format(os.path.split(Global_db_uri)[1].split(".")[0]))
                        self.entity_tree_view.refresh()
                        return
                except:
                    return
            else:
                return
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.openDb():{1}".format(str(datetime.datetime.now()), str(err)))

    def closeDb(self):
        try:
            global Global_db_uri
            Global_db_uri = ""
            self.cntlr.closeDb()
            self.setWindowTitle("XBRLStudio")
            self.cntlr.openDb()
            self.refreshAll()
            self.clearTabs()
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.closeDb():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def clearTabs(self):
        try:
            tab_count = self.mainTabWidget.count()
            tab_count -= 1
            i = 0
            while i < tab_count:
                self.mainTabWidget.removeTab(0)
                i += 1
            self.addNewTab(0)
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.clearTabs():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def preExistingFilingWarning(self, pre_existing_filings): #pre_existing_filings is [(cik, period, filingobject)...(cik, period, filingobject)]
        try:
            global Global_db_uri
            body = "The following filings were found in the database:\n"
            for filing in pre_existing_filings:
                body += "CIK {0} at period {1}\n".format(filing[0], filing[1])
            body += "\nDo you wish to continue?\n"
            continue_choice = QtWidgets.QMessageBox.warning(self,
                                               "Filings found",
                                               body,
                                               QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                                               QtWidgets.QMessageBox.Ok)
            if continue_choice == QtWidgets.QMessageBox.Ok:
                return True
            else:
                return False
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.preExistingFilingWarning():{1}".format(str(datetime.datetime.now()), str(err)))
            return False

    def manualPreExistingFilingWarning(self, manual_name, manual_period):
        try:
            global Global_db_uri
            overwrite_choice = QtWidgets.QMessageBox.warning(self,
                                               "Overwrite filing?",
                                               "Are you sure you want to replace {0}, {1} in database {2}?".format(manual_name, manual_period, os.path.split(Global_db_uri)[1].split(".")[0]),
                                               QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                                               QtWidgets.QMessageBox.Ok)
            if overwrite_choice == QtWidgets.QMessageBox.Ok:
                return True
            else:
                return False
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.manualPreExistingFilingWarning():{1}".format(str(datetime.datetime.now()), str(err)))
            return False

    def fileImport(self):
        try:
            global Global_db_uri
            if Global_db_uri is "" or os.path.split(Global_db_uri)[1].split(".")[-1] != "sqlite":
                pop_up = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                               "Select database",
                                               "Select or create a XBRLStudio SQLite database for importing.",
                                               QtWidgets.QMessageBox.Ok,
                                               self,
                                               QtCore.Qt.Popup)
                pop_up.show()
                return
            root_dir = None
            f_list = QtWidgets.QFileDialog.getOpenFileNames(caption = "Select XBRL File(s)",
                                          directory = "C:\\",
                                          filter = "Instances (*.xml)")[0]
            self.cntlr_processXbrl_start_signal.emit("File", False, True, f_list, root_dir)
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.fileImport():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def folderImport(self):
        try:
            global Global_db_uri
            if Global_db_uri is "" or os.path.split(Global_db_uri)[1].split(".")[-1] != "sqlite":
                pop_up = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                               "Select database",
                                               "Select or create a XBRLStudio SQLite database for importing.",
                                               QtWidgets.QMessageBox.Ok,
                                               self,
                                               QtCore.Qt.Popup)
                pop_up.show()
                return
            f_list = None
            root_dir = QtWidgets.QFileDialog.getExistingDirectory(caption = "Select XBRL Folder", directory = "C:\\")
            self.cntlr_processXbrl_start_signal.emit("Folder", False, True, f_list, root_dir)
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.folderImport():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def exitApplication(self):
        try:
            self.closeDb()
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.exitApplication():{1}".format(str(datetime.datetime.now()), str(err)))

        return sys.exit()

    def customMenuEntityTreeView(self, position):
        try:
            selection = self.entity_tree_view.model().itemFromIndex(self.entity_tree_view.indexAt(position))
            if selection is not None:
                clipboard = QApplication.clipboard()
                entity_tree_view_context_menu = QtWidgets.QMenu(self)
                view_filings_action = entity_tree_view_context_menu.addAction("View Filings")
                view_filings_action.triggered.connect(lambda x: self.entity_tree_view.updateFilingTreeView(self.entity_tree_view.indexAt(position)))
                copy_cik_action = entity_tree_view_context_menu.addAction("Copy CIK")
                copy_cik_action.triggered.connect(lambda x: clipboard.setText(selection.toolTip().split("=")[1]))
                rename_entity_action = entity_tree_view_context_menu.addAction("Rename Entity")
                rename_entity_action.triggered.connect(lambda x: self.entity_tree_view.renameEntity(self.entity_tree_view.indexAt(position)))
                entity_tree_view_context_menu.addSeparator()
                remove_entity_action = entity_tree_view_context_menu.addAction("Remove Entity")
                remove_entity_action.triggered.connect(lambda x: self.cntlr.removeEntity(selection.toolTip().split("=")[1]))
                entity_tree_view_context_menu.exec_(self.entity_tree_view.viewport().mapToGlobal(position))
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.customMenuEntityTreeView():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def customMenuFilingTreeView(self, position):
        try:
            selection = self.filing_tree_view.model().itemFromIndex(self.filing_tree_view.indexAt(position))
            if selection is not None:
                clipboard = QApplication.clipboard()
                filing_tree_view_context_menu = QtWidgets.QMenu(self)
                table_insert_action = filing_tree_view_context_menu.addAction("Append to Table")
                table_insert_action.triggered.connect(lambda x: self.filing_tree_view.insertFilingIntoTable(self.filing_tree_view.indexAt(position)))
                filing_tree_view_context_menu.addSeparator()
                remove_filing_action = filing_tree_view_context_menu.addAction("Remove Filing")
                remove_filing_action.triggered.connect(lambda x: self.cntlr.removeFiling(selection))
                filing_tree_view_context_menu.exec_(self.filing_tree_view.viewport().mapToGlobal(position))
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.customMenuFilingTreeView():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def customMenuNumericalGraphic(self, position):
        try:
            current_num_graphic = self.mainTabWidget.currentWidget().findChild(QtCharts.QChartView, "numericalGraphic")
            if current_num_graphic.chart().items_viewed == True:
                clipboard = QApplication.clipboard()
                numerical_graphic_context_menu = QtWidgets.QMenu(self)
                graphic_copy_action = numerical_graphic_context_menu.addAction("Copy Image")
                graphic_copy_action.triggered.connect(lambda x: clipboard.setPixmap(current_num_graphic.grab()))
                numerical_graphic_context_menu.exec_(current_num_graphic.viewport().mapToGlobal(position))
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.customMenuNumericalGraphic():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def customMenuTextualGraphic(self, position):
        try:
            current_tex_graphic = self.mainTabWidget.currentWidget().findChild(QtWidgets.QTextEdit, "textualGraphic")
            if current_tex_graphic.items_viewed == True:
                clipboard = QApplication.clipboard()
                textual_graphic_context_menu = QtWidgets.QMenu(self)
                graphic_copy_html_action = textual_graphic_context_menu.addAction("Copy HTML")
                graphic_copy_html_action.triggered.connect(lambda x: clipboard.setText(current_tex_graphic.html))
                graphic_copy_img_action = textual_graphic_context_menu.addAction("Copy Image")
                graphic_copy_img_action.triggered.connect(lambda x: clipboard.setPixmap(current_tex_graphic.grab()))
                textual_graphic_context_menu.exec_(current_tex_graphic.mapToGlobal(position))
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.customMenuTextualGraphic():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def choosePreferences(self):
        try:
            self.pref_window = BookPrefWindow(self, QtCore.Qt.Window)
            self.pref_window.show()
            self.pref_window.activateWindow()
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.choosePreferences():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def refreshAll(self, import_successful = False):
        try:
            self.entity_tree_view.refresh()
            self.filing_tree_view.refresh()
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.refreshAll():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def manualImport(self, fact_file_list):
        if self.pref.import_manual_info_option == "Yes":
            for fact_file in fact_file_list:
                try:
                    entity_cik, entity_name, filing_period = self.getManualImportInfo(fact_file)
                    self.showStatus("Importing {0}".format(os.path.split(fact_file)[1]))
                    self.book_filing_manager.manualImportFactFile(entity_cik, entity_name, filing_period, fact_file)
                    os.remove(fact_file)
                except Exception as err:
                    view_logger.error("{0}:BookMainWindow.manualImport():{1}".format(str(datetime.datetime.now()), "Processing error - manual input failed"))
                    self.warnUser_signal.emit("Processing Error", "Error processing {0}. Manually input the filing information as indicated. Each instance must have a complete DTS in the same directory.".format(fact_file))
                    os.remove(fact_file)
            self.refreshAll()
            return
        else:
            view_logger.error("{0}:BookMainWindow.manualImport():{1}".format(str(datetime.datetime.now()), "Processing error - manual input required"))
            self.warnUser_signal.emit("Processing Error", "Error processing {0}. Enable manual import under File->Preferences->Import. Each instance must have a complete DTS in the same directory.".format(fact_file))
            os.remove(fact_file)
            self.refreshAll()
            return

    def getManualImportInfo(self, target_uri):
        try:
            manual_entity_cik = None
            manual_entity_name = None
            manual_filing_period = None
            target_file_name = os.path.split(target_uri)[1]
            notifier = QtWidgets.QMessageBox.warning(self,
                                               "Import failed",
                                               "Please manually provide information for import of filing {0}.".format(target_file_name),
                                               QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                                               QtWidgets.QMessageBox.Ok)
            if notifier == QtWidgets.QMessageBox.Ok:
                manual_entity_cik = QtWidgets.QInputDialog.getText(self, "Entity CIK", "CIK:",
                                                         QtWidgets.QLineEdit.Normal)[0]
                manual_entity_name = QtWidgets.QInputDialog.getText(self, "Entity Name", "Name:",
                                                         QtWidgets.QLineEdit.Normal)[0]
                manual_filing_period = QtWidgets.QInputDialog.getText(self, "Filing Period", "Period (e.g., q42015):",
                                                         QtWidgets.QLineEdit.Normal)[0]

            return manual_entity_cik, manual_entity_name, manual_filing_period
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.getManualImportInfo():{1}".format(str(datetime.datetime.now()), str(err)))

    def warnUser(self, title, body):
        try:
            notifier = QtWidgets.QMessageBox.warning(self,
                                       title,
                                       body,
                                       QtWidgets.QMessageBox.Ok,
                                       QtWidgets.QMessageBox.Ok)
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.warnUser():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def registerApplication(self):
        try:
            self.register_window = BookRegisterWindow(self, QtCore.Qt.Window)
            self.register_window.show()
            self.register_window.activateWindow()
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.registerApplication():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def aboutXbrlStudio(self):
        try:
            # Tiered
            # current_logo_path = os.path.join(self.directories.get("Global_img_dir"), "XBRLStudio_1_1_0_Logo.png")
            # Flat
            # current_logo_path = os.path.join(os.getcwd(), "res", "img", "XBRLStudio1Logo.png")
            current_logo_path = os.path.join(self.directories.get("Global_img_dir"), "XBRLStudio_1_1_0_Logo.png")
            title = "XBRLStudio"
            body = "Copyright by BitWorks, LLC.\n\n\nMIT License\n\n\n"
            notifier = QtWidgets.QMessageBox(self)
            current_logo_image = QImage(current_logo_path)
            if current_logo_image is None:
                notifier.setIconPixmap(QPixmap())
            else:
                current_logo_pixmap = QPixmap().fromImage(current_logo_image)
                notifier.setIconPixmap(current_logo_pixmap)
            notifier.setWindowTitle(title)
            notifier.setText(body)
            notifier.show()
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.aboutXbrlStudio():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def addTableRows(self):
        try:
            current_sub_tab = self.mainTabWidget.currentWidget().findChild(QtWidgets.QTabWidget, "newTab_subTabWidget").currentWidget()
            if current_sub_tab.objectName() == "newTab_numericalTab":
                num_table_view = self.mainTabWidget.currentWidget().findChild(QtWidgets.QTableView, "numericalTableView")
                num_rows = QtWidgets.QInputDialog.getText(self, "Add Rows", "Number of rows to add (integer):", QtWidgets.QLineEdit.Normal)[0]
                if num_rows != "":
                    try:
                        original_row_count = num_table_view.model().row_count
                        num_rows = int(num_rows)
                        if num_rows < 1:
                            raise Exception
                        num_table_view.model().addRows(num_rows)
                        #Persistent view checkbox
                        for view_index in num_table_view.model().view_indices:
                            if view_index.isValid():
                                num_table_view.openPersistentEditor(view_index)
                        i = 0
                        while i < original_row_count + num_rows:
                            num_table_view.setRowHeight(i + original_row_count, 25)
                            i += 1
                        num_table_view.update()
                    except Exception as err:
                        self.addTableRows()
            elif current_sub_tab.objectName() == "newTab_textualTab":
                tex_table_view = self.mainTabWidget.currentWidget().findChild(QtWidgets.QTableView, "textualTableView")
                num_rows = QtWidgets.QInputDialog.getText(self, "Add Rows", "Number of rows to add (integer):", QtWidgets.QLineEdit.Normal)[0]
                if num_rows != "":
                    try:
                        original_row_count = tex_table_view.model().row_count
                        num_rows = int(num_rows)
                        if num_rows < 1:
                            raise Exception
                        tex_table_view.model().addRows(num_rows)
                        #Persistent view checkbox
                        for view_index in tex_table_view.model().view_indices:
                            if view_index.isValid():
                                tex_table_view.openPersistentEditor(view_index)
                        i = 0
                        while i < original_row_count + num_rows:
                            tex_table_view.setRowHeight(i + original_row_count, 25)
                            i += 1
                        tex_table_view.update()
                    except Exception as err:
                        self.addTableRows()
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.addTableRows():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def viewAll(self):
        try:
            current_sub_tab = self.mainTabWidget.currentWidget().findChild(QtWidgets.QTabWidget, "newTab_subTabWidget").currentWidget()
            if current_sub_tab.objectName() == "newTab_numericalTab":
                num_table_view = self.mainTabWidget.currentWidget().findChild(QtWidgets.QTableView, "numericalTableView")
                num_table_view.model().viewAll()
            elif current_sub_tab.objectName() == "newTab_textualTab":
                tex_table_view = self.mainTabWidget.currentWidget().findChild(QtWidgets.QTableView, "textualTableView")
                tex_table_view.model().viewAll()
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.viewAll():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def getInputText(self, title, body):
        try:
            return QtWidgets.QInputDialog.getText(self, title, body, QtWidgets.QLineEdit.Normal)[0]
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.getInputText():{1}".format(str(datetime.datetime.now()), str(err)))

    def getCikCombobox(self, fact_file_list):
        try:
            for fact_file in fact_file_list:
                target_filing = BookFilingUtility.parseFactFile(fact_file)
                target_cik_list, target_parent_cik, target_name, target_period = BookFilingUtility.getFilingInfo(target_filing)
                title = "Select CIK"
                body = "Multiple Central Index Keys were found in filing {0}.\nPlease choose the CIK you want to import this filing under.\n".format(os.path.split(fact_file)[1])
                str_selection_list = []
                selection_list = sorted(target_cik_list)
                for selection in selection_list:
                    str_selection_list.append(str(selection))
                selection = QtWidgets.QInputDialog.getItem(self, title, body, str_selection_list)
                if selection[1] is True:
                    self.status_bar.showMessage("Importing {0}.".format(os.path.split(fact_file)[1]))
                    self.book_filing_manager.importFactFile(target_fact_uri = fact_file, target_cik = selection[0])
                os.remove(fact_file)
            self.refreshAll()
            return
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.getCikCombobox():{1}".format(str(datetime.datetime.now()), str(err)))

    def updateProgressBar(self, value):
        try:
            self.progressBar.setValue(value)
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.updateProgressBar():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def resetProgressBar(self):
        try:
            self.progressBar.setValue(0)
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.resetProgressBar():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def exportTabHtml(self):
        try:
            self.book_exporter.exportHtml("single_tab")
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.exportTabHtml():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def exportHtml(self):
        try:
            self.book_exporter.exportHtml("all_tabs")
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.exportHtml():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def exportTabCsv(self):
        try:
            self.book_exporter.exportCsv("single_tab")
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.exportTabCsv():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def exportCsv(self):
        try:
            self.book_exporter.exportCsv("all_tabs")
        except Exception as err:
            view_logger.error("{0}:BookMainWindow.exportCsv():{1}".format(str(datetime.datetime.now()), str(err)))

        return

class BookPrefTab(QtWidgets.QWidget):
    """
    BookPrefTab
    ~~~~~~~~~~~
    Customized sub-class of QWidget, for the display and alteration of the application's preferences; this is for one tab of the window

    Functions
    ~~~~~~~~~
    setupUi(self, tab_name) - sets up user interface based on the tab name being built

    Attributes
    ~~~~~~~~~~
    book_main_window (BookView.BookMainWindow type); provides access to functions and attributes of the 'parental' BookMainWindow instance
    main_VL (QtWidgets.QVBoxLayout type); primary vertical layout for widgets
    general_num_graph_type_wd (QtWidgets.QWidget type); placeholder for sub-layout
    general_num_graph_type_HL (QtWidgets.QHBoxLayout type); sub-layout for label and combobox
    general_num_graph_type_la (QtWidgets.QLabel type); label for numerical graph type
    general_num_graph_type_cb (QtWidgets.QComboBox type); combobox for selecting numerical graph type
    general_show_dec_wd (QtWidgets.QWidget type); placeholder for sub-layout
    general_show_dec_HL (QtWidgets.QHBoxLayout type); sub-layout for label and combobox
    general_show_dec_la (QtWidgets.QLabel type); label for showing decimal precision
    general_show_dec_cb (QtWidgets.QComboBox type); combobox for selecting whether to show or hide decimal precision
    import_dir_recur_wd (QtWidgets.QWidget type); placeholder for sub-layout
    import_dir_recur_HL (QtWidgets.QHBoxLayout type); sub-layout for label and combobox
    import_dir_recur_la (QtWidgets.QLabel type); label for recursive searching of folders during a folder import operation
    import_dir_recur_cb (QtWidgets.QComboBox type); combobox for selecting whether to recursive searching of folders during import
    import_manual_info_wd (QtWidgets.QWidget type); placeholder for sub-layout
    import_manual_info_HL (QtWidgets.QHBoxLayout type); sub-layout for label and combobox
    import_manual_info_la (QtWidgets.QLabel type); label for whether to allow user to manually enter information needed for import
    import_manual_info_cb (QtWidgets.QComboBox type); combobox for selecting whether to allow user to manually enter information

    """
    def __init__(self, book_pref_window_mtw, tab_name, book_main_window):
        view_logger.info("{0}:Initializing BookPrefTab".format(str(datetime.datetime.now())))
        QtWidgets.QWidget.__init__(self, book_pref_window_mtw)
        self.book_pref_window_mtw = book_pref_window_mtw
        self.setObjectName(tab_name.lower() + "Tab")
        self.main_VL = QtWidgets.QVBoxLayout(self)
        self.main_VL.setSpacing(0)
        self.main_VL.setContentsMargins(0, 0, 0, 0)
        self.book_main_window = book_main_window
        self.setupUi(tab_name)

    def setupUi(self, tab_name):
        try:
            if tab_name == "General":
                self.general_num_graph_type_wd = QtWidgets.QWidget(self)
                self.general_num_graph_type_HL = QtWidgets.QHBoxLayout(self.general_num_graph_type_wd)
                self.general_num_graph_type_HL.setSpacing(0)
                self.general_num_graph_type_HL.setContentsMargins(0, 0, 0, 0)
                self.general_num_graph_type_la = QtWidgets.QLabel(self.general_num_graph_type_wd)
                self.general_num_graph_type_la.setText("Numerical graphic type:")
                self.general_num_graph_type_cb = QtWidgets.QComboBox(self.general_num_graph_type_wd)
                self.general_num_graph_type_cb.addItems(["Bar", "Line", "Scatter"])
                self.general_num_graph_type_cb.setCurrentText(self.book_main_window.pref.general_num_graph_type)
                self.general_num_graph_type_wd.setLayout(self.general_num_graph_type_HL)
                self.general_num_graph_type_HL.addWidget(self.general_num_graph_type_la)
                self.general_num_graph_type_HL.addWidget(self.general_num_graph_type_cb)
                self.main_VL.addWidget(self.general_num_graph_type_wd)

                self.general_show_dec_wd = QtWidgets.QWidget(self)
                self.general_show_dec_HL = QtWidgets.QHBoxLayout(self.general_show_dec_wd)
                self.general_show_dec_HL.setSpacing(0)
                self.general_show_dec_HL.setContentsMargins(0, 0, 0, 0)
                self.general_show_dec_la = QtWidgets.QLabel(self.general_show_dec_wd)
                self.general_show_dec_la.setText("Show decimal precision:")
                self.general_show_dec_cb = QtWidgets.QComboBox(self.general_show_dec_wd)
                self.general_show_dec_cb.addItems(["No", "Yes"])
                self.general_show_dec_cb.setCurrentText(self.book_main_window.pref.general_show_decimal_column)
                self.general_show_dec_wd.setLayout(self.general_show_dec_HL)
                self.general_show_dec_HL.addWidget(self.general_show_dec_la)
                self.general_show_dec_HL.addWidget(self.general_show_dec_cb)
                self.main_VL.addWidget(self.general_show_dec_wd)

            elif tab_name == "Import":
                self.import_dir_recur_wd = QtWidgets.QWidget(self)
                self.import_dir_recur_HL = QtWidgets.QHBoxLayout(self.import_dir_recur_wd)
                self.import_dir_recur_HL.setSpacing(0)
                self.import_dir_recur_HL.setContentsMargins(0, 0, 0, 0)
                self.import_dir_recur_la = QtWidgets.QLabel(self.import_dir_recur_wd)
                self.import_dir_recur_la.setText("Folder import:")
                self.import_dir_recur_cb = QtWidgets.QComboBox(self.import_dir_recur_wd)
                self.import_dir_recur_cb.addItems(["Search top folder only", "Search top folder and sub-folders"])
                self.import_dir_recur_cb.setCurrentText(self.book_main_window.pref.import_dir_recursive_option)
                self.import_dir_recur_wd.setLayout(self.import_dir_recur_HL)
                self.import_dir_recur_HL.addWidget(self.import_dir_recur_la)
                self.import_dir_recur_HL.addWidget(self.import_dir_recur_cb)
                self.main_VL.addWidget(self.import_dir_recur_wd)

                self.import_manual_info_wd = QtWidgets.QWidget(self)
                self.import_manual_info_HL = QtWidgets.QHBoxLayout(self.import_manual_info_wd)
                self.import_manual_info_HL.setSpacing(0)
                self.import_manual_info_HL.setContentsMargins(0, 0, 0, 0)
                self.import_manual_info_la = QtWidgets.QLabel(self.import_manual_info_wd)
                self.import_manual_info_la.setText("Manual import on failure:")
                self.import_manual_info_cb = QtWidgets.QComboBox(self.import_manual_info_wd)
                self.import_manual_info_cb.addItems(["Yes", "No"])
                self.import_manual_info_cb.setCurrentText(self.book_main_window.pref.import_manual_info_option)
                self.import_manual_info_wd.setLayout(self.import_manual_info_HL)
                self.import_manual_info_HL.addWidget(self.import_manual_info_la)
                self.import_manual_info_HL.addWidget(self.import_manual_info_cb)
                self.main_VL.addWidget(self.import_manual_info_wd)
        except Exception as err:
            view_logger.error("{0}:BookPrefTab.setupUi():{1}".format(str(datetime.datetime.now()), str(err)))

        return

class BookPref():
    """
    BookPref
    ~~~~~~~~
    Custom class, for storing the application's preferences

    Functions
    ~~~~~~~~~

    Attributes
    ~~~~~~~~~~
    book_main_window (BookView.BookMainWindow type); provides access to functions and attributes of the 'parental' BookMainWindow instance
    general_num_graph_type (string type); may be "Bar", "Line", or "Scatter" to specify the desired numerical graph type
    general_show_decimal_column (string type); may be "Yes" or "No" to specify whether to show or hide the decimal precision column
    import_dir_recursive_option (string type); specifies whether to search folders recursively or not during a folder import
    import_manual_info_option (string type); specifies whether to allow user to manually enter import information, where needed
    """
    def __init__(self, book_main_window):
        view_logger.info("{0}:Initializing BookPref".format(str(datetime.datetime.now())))
        self.book_main_window = book_main_window
        self.general_num_graph_type = "Bar"
        self.general_show_decimal_column = "No"
        self.import_dir_recursive_option = "Search top folder and sub-folders"
        self.import_manual_info_option = "Yes"

class BookPrefWindow(QtWidgets.QDialog):
    """
    BookPrefWindow
    ~~~~~~~~~~~~~~
    Customized sub-class of QDialog, for the display and alteration of the application's preferences (all tabs)

    Functions
    ~~~~~~~~~
    setupUi(self) - set up the user interface (two layouts: one for tabs and one for buttons)
    closeWithoutChanges(self) - closes the window without changes to book_main_window.pref
    closeWithChanges(self) - updates preferences and closes the window
    updatePreferences(self) - updates all available preferences for all tabs

    Attributes
    ~~~~~~~~~~
    book_main_window (BookView.BookMainWindow type); provides access to functions and attributes of the 'parental' BookMainWindow instance
    main_VL (QtWidgets.QVBoxLayout type); container for tab_HL and button_HL
    tab_HL (QtWidgets.QHBoxLayout type); container for mainTabWidget
    button_HL (QtWidgets.QHBoxLayout type); container for cancel_button, apply_button, and ok_button
    mainTabWidget (QtWidgets.QTabWidget type); tab widget container for general_tab, and import_tab
    general_tab (BookPrefTab type); tab widget for displaying/altering general preferences
    import_tab (BookPrefTab type); tab widget for displaying/altering import preferences
    cancel_button (QtWidgets.QPushButton type); connected to closeWithoutChanges
    apply_button (QtWidgets.QPushButton type); connected to updatePreferences
    ok_button (QtWidgets.QPushButton type); connected to closeWithChanges
    """
    def __init__(self, book_main_window, window_flags):
        view_logger.info("{0}:Initializing BookPrefWindow".format(str(datetime.datetime.now())))
        QtWidgets.QDialog.__init__(self)
        self.book_main_window = book_main_window #self.book_main_window.pref = BookPref() instance
        self.setupUi()
        self.setObjectName("BookPrefWindow")

    def setupUi(self):
        try:
            self.setWindowModality(QtCore.Qt.ApplicationModal)
            self.setWindowTitle("XBRLStudio Preferences")
            self.resize(350, 200)
            self.main_VL = QtWidgets.QVBoxLayout(self)
            self.main_VL.setSpacing(0)
            self.main_VL.setContentsMargins(0, 0, 0, 0)
            self.tab_HL = QtWidgets.QHBoxLayout()
            self.button_HL = QtWidgets.QHBoxLayout()
            self.main_VL.addLayout(self.tab_HL)
            self.main_VL.addLayout(self.button_HL)
            self.mainTabWidget = QtWidgets.QTabWidget(self)
            self.mainTabWidget.setTabsClosable(False)
            self.mainTabWidget.setMovable(False)
            self.general_tab = BookPrefTab(self.mainTabWidget, "General", self.book_main_window)
            self.import_tab = BookPrefTab(self.mainTabWidget, "Import", self.book_main_window)
            self.cancel_button = QtWidgets.QPushButton("Cancel", self)
            self.cancel_button.setDefault(True)
            self.apply_button = QtWidgets.QPushButton("Apply", self)
            self.ok_button = QtWidgets.QPushButton("Ok", self)
            self.mainTabWidget.addTab(self.general_tab, "General")
            self.mainTabWidget.addTab(self.import_tab, "Import")
            self.tab_HL.addWidget(self.mainTabWidget)
            self.button_HL.addStretch()
            self.button_HL.addWidget(self.cancel_button)
            self.button_HL.addWidget(self.apply_button)
            self.button_HL.addWidget(self.ok_button)
            self.mainTabWidget.setCurrentIndex(0)
            self.cancel_button.clicked.connect(self.closeWithoutChanges)
            self.apply_button.clicked.connect(self.updatePreferences)
            self.ok_button.clicked.connect(self.closeWithChanges)
        except Exception as err:
            view_logger.error("{0}:BookPrefWindow.setupUi():{1}".format(str(datetime.datetime.now()), str(err)))

    def closeWithoutChanges(self):
        try:
            return self.book_main_window.pref_window.close()
        except Exception as err:
            view_logger.error("{0}:BookPrefWindow.closeWithoutChanges():{1}".format(str(datetime.datetime.now()), str(err)))

    def closeWithChanges(self):
        try:
            self.updatePreferences()

            return self.book_main_window.pref_window.close()
        except Exception as err:
            view_logger.error("{0}:BookPrefWindow.closeWithChanges():{1}".format(str(datetime.datetime.now()), str(err)))

    def updatePreferences(self):
        try:
            self.book_main_window.pref.general_num_graph_type = self.general_tab.general_num_graph_type_cb.currentText()
            self.book_main_window.pref.general_show_decimal_column = self.general_tab.general_show_dec_cb.currentText()
            self.book_main_window.pref.import_dir_recursive_option = self.import_tab.import_dir_recur_cb.currentText()
            self.book_main_window.pref.import_manual_info_option = self.import_tab.import_manual_info_cb.currentText()

            current_index = 0
            while current_index < self.book_main_window.mainTabWidget.count() - 1:
                current_tab = self.book_main_window.mainTabWidget.widget(current_index)
                current_num_table = current_tab.findChild(QtWidgets.QTableView, "numericalTableView")
                current_num_graphic = current_tab.findChild(QtCharts.QChartView, "numericalGraphic")
                current_tex_table = current_tab.findChild(QtWidgets.QTableView, "textualTableView")
                current_tex_graphic = current_tab.findChild(QtWidgets.QTextEdit, "textualGraphic")

                if self.book_main_window.pref.general_show_decimal_column == "Yes":
                    try:
                        current_num_table.showColumn(7)
                    except Exception as err:
                        pass
                elif self.book_main_window.pref.general_show_decimal_column == "No":
                    try:
                        current_num_table.hideColumn(7)
                    except Exception as err:
                        pass

                current_num_table.update()
                current_num_graphic.refreshGraphic()
                current_tex_table.update()
                current_tex_graphic.refreshGraphic()

                current_index += 1
        except Exception as err:
            view_logger.error("{0}:BookPrefWindow.updatePreferences():{1}".format(str(datetime.datetime.now()), str(err)))

        return

class BookRegisterWindow(QtWidgets.QDialog):
    """
    BookRegisterWindow
    ~~~~~~~~~~~~~~~~~~
    Customized sub-class of QDialog, for registration of the software (validation of the key)

    Functions
    ~~~~~~~~~
    setupUi(self) - set up the user interface (three layouts: one for sale_id, one for key, one for buttons)
    closeWithoutRegistration(self) - closes the window without registration attempt
    attemptRegistration(self) - attempts to register a given sale_id/key combination

    Attributes
    ~~~~~~~~~~
    book_main_window (BookView.BookMainWindow type); provides access to functions and attributes of the 'parental' BookMainWindow instance
    validator (BookValidator.BookValidator type); provides access to functions for generating and validating keys, needed for validation
    main_VL (QtWidgets.QVBoxLayout type); primary vertical layout for holding lineEdit and button layouts
    le_HL_1 (QtWidgets.QHBoxLayout type); sale_id lineEdit/label layout
    le_HL_2 (QtWidgets.QHBoxLayout type); key lineEdit/label layout
    button_HL (QtWidgets.QHBoxLayout type); button layout
    sale_id_la (QtWidgets.QLabel type); label prompting for sale ID
    sale_id_le (QtWidgets.QLineEdit type); lineEdit for entering sale ID
    key_la (QtWidgets.QLabel type); label prompting for entering key
    key_le_1 (QtWidgets.QLineEdit type); lineEdit for entering key part 1 of 5
    key_la_1 (QtWidgets.QLabel type); label "-" to help user enter key
    key_le_2 (QtWidgets.QLineEdit type); lineEdit for entering key part 2 of 5
    key_la_2 (QtWidgets.QLabel type); label "-" to help user enter key
    key_le_3 (QtWidgets.QLineEdit type); lineEdit for entering key part 3 of 5
    key_la_3 (QtWidgets.QLabel type); label "-" to help user enter key
    key_le_4 (QtWidgets.QLineEdit type); lineEdit for entering key part 4 of 5
    key_la_4 (QtWidgets.QLabel type); label "-" to help user enter key
    key_le_5 (QtWidgets.QLineEdit type); lineEdit for entering key part 5 of 5
    cancel_button (QtWidgets.QPushButton type); connected to closeWithoutRegistration
    register_button (QtWidgets.QPushButton type); connected to attemptRegistration
    """
    def __init__(self, book_main_window, window_flags):
        view_logger.info("{0}:Initializing BookRegisterWindow".format(str(datetime.datetime.now())))
        QtWidgets.QDialog.__init__(self)
        self.book_main_window = book_main_window
        self.setupUi()
        self.setObjectName("BookRegisterWindow")
        self.validator = BookValidator.BookValidator()

    def setupUi(self):
        try:
            self.setWindowModality(QtCore.Qt.ApplicationModal)
            self.setWindowTitle("XBRLStudio Registration")
            self.resize(350, 200)
            self.main_VL = QtWidgets.QVBoxLayout(self)
            self.main_VL.setSpacing(0)
            self.main_VL.setContentsMargins(0, 0, 0, 0)
            self.le_HL_1 = QtWidgets.QHBoxLayout()
            self.le_HL_2 = QtWidgets.QHBoxLayout()
            self.button_HL = QtWidgets.QHBoxLayout()
            self.main_VL.addLayout(self.le_HL_1)
            self.main_VL.addLayout(self.le_HL_2)
            self.main_VL.addLayout(self.button_HL)
            self.sale_id_la = QtWidgets.QLabel("Sale ID:", self)
            self.sale_id_le = QtWidgets.QLineEdit(self)
            self.key_la = QtWidgets.QLabel("Registration Key:", self)
            self.key_le_1 = QtWidgets.QLineEdit(self)
            self.key_la_1 = QtWidgets.QLabel("-", self)
            self.key_le_2 = QtWidgets.QLineEdit(self)
            self.key_la_2 = QtWidgets.QLabel("-", self)
            self.key_le_3 = QtWidgets.QLineEdit(self)
            self.key_la_3 = QtWidgets.QLabel("-", self)
            self.key_le_4 = QtWidgets.QLineEdit(self)
            self.key_la_4 = QtWidgets.QLabel("-", self)
            self.key_le_5 = QtWidgets.QLineEdit(self)
            self.cancel_button = QtWidgets.QPushButton("Cancel", self)
            self.register_button = QtWidgets.QPushButton("Register", self)
            self.register_button.setDefault(True)
            self.le_HL_1.addWidget(self.sale_id_la)
            self.le_HL_1.addWidget(self.sale_id_le)
            self.le_HL_2.addWidget(self.key_la)
            self.le_HL_2.addWidget(self.key_le_1)
            self.le_HL_2.addWidget(self.key_la_1)
            self.le_HL_2.addWidget(self.key_le_2)
            self.le_HL_2.addWidget(self.key_la_2)
            self.le_HL_2.addWidget(self.key_le_3)
            self.le_HL_2.addWidget(self.key_la_3)
            self.le_HL_2.addWidget(self.key_le_4)
            self.le_HL_2.addWidget(self.key_la_4)
            self.le_HL_2.addWidget(self.key_le_5)
            self.button_HL.addStretch()
            self.button_HL.addWidget(self.cancel_button)
            self.button_HL.addWidget(self.register_button)
            self.cancel_button.clicked.connect(self.closeWithoutRegistration)
            self.register_button.clicked.connect(lambda x: self.attemptRegistration(self.book_main_window.directories.get("Global_key_dir")))
        except Exception as err:
            view_logger.error("{0}:BookRegisterWindow.setupUi():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def closeWithoutRegistration(self):
        try:
            return self.book_main_window.register_window.close()
        except Exception as err:
            view_logger.error("{0}:BookRegisterWindow.closeWithoutRegistration():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def attemptRegistration(self, key_dir):
        try:
            self.sale_id = self.sale_id_le.text()
            self.input_key = str(
                self.key_le_1.text()) + "-" + str(
                self.key_le_2.text()) + "-" + str(
                self.key_le_3.text()) + "-" + str(
                self.key_le_4.text()) + "-" + str(self.key_le_5.text())
            self.expected_key = str(self.validator.keygen(self.sale_id))
            if self.input_key == self.expected_key:
                self.book_main_window.registration = True
                self.book_main_window.warnUser("Registration Succeeded", "Thank you for registering your copy of XBRLStudio! Full access to the program's functionality is granted.")
                sale_id_file = open(os.path.join(key_dir, "XBRLStudio_1_1_0_SaleID.txt"), "w")
                key_file = open(os.path.join(key_dir, "XBRLStudio_1_1_0_Key.txt"), "w")
                sale_id_file.write(self.sale_id)
                key_file.write(self.input_key)
                sale_id_file.close()
                key_file.close()
                return self.book_main_window.register_window.close()
            else:
                self.book_main_window.registration = False
                self.book_main_window.warnUser("Registration Failed", "Please ensure that your Sale ID and Registration Key are entered correctly.\n\nDo not enter dashes when entering the Registration Key.\n\n")
                return
        except Exception as err:
            view_logger.error("{0}:BookRegisterWindow.attemptRegistration():{1}".format(str(datetime.datetime.now()), str(err)))

        return

class BookFilingTreeView(QtWidgets.QTreeView):
    """
    BookFilingTreeView
    ~~~~~~~~~~~~~~~~~~
    Customized sub-class of QTreeView; implements a refresh function, as well as a function for inserting a selected entity/filing pair into the table model

    Functions
    ~~~~~~~~~
    refresh(self, new_cik = None) - if a new entity is selected, refreshes the tree view to display its filings
    insertFilingIntoTable(self, selection) - if a filing is double-clicked, this function inserts the corresponding entity and filing descriptors into the currently-viewed table

    Attributes
    ~~~~~~~~~~
    book_main_window (BookView.BookMainWindow type); provides access to functions and attributes of the 'parental' BookMainWindow instance
    filing_items (list type); collection of BookModel.BookFilingTreeItem instances
    raw_year_items (list type); collection of strings, each a representation of the filing years available (e.g., '2015')
    real_year_items (list type); collection of BookModel.BookFilingTreeItem instances
    """

    def __init__(self, book_main_window):
        view_logger.info("{0}:Initializing BookFilingTreeView".format(str(datetime.datetime.now())))
        QtWidgets.QTreeView.__init__(self)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.book_main_window = book_main_window
        self.doubleClicked.connect(self.insertFilingIntoTable)

    def refresh(self, new_cik = None):
        try:
            self.model().removeRows(0, self.model().rowCount())
            if new_cik:
                self.filing_items = []
                self.raw_year_items = set()
                self.real_year_items = []
                self.model().populateRawItems(new_cik)
                if self.model().raw_items is not None:
                    for filing_str in self.model().raw_items:
                        filing = BookModel.BookFilingTreeItem(period = filing_str, cik = new_cik)
                        filing.setText(filing_str)
                        filing.setToolTip("{0} filing from {1}".format(filing_str.split("-")[1],
                                                                   filing_str.split("-")[0]))
                        self.filing_items.append(filing)
                        self.raw_year_items.add(filing_str.split("-")[0])
                    self.raw_year_items = sorted(list(self.raw_year_items))
                    for raw_year_item in self.raw_year_items:
                        real_item = BookModel.BookFilingTreeItem(period = raw_year_item, cik = new_cik)
                        real_item.setText(raw_year_item)
                        real_item.setToolTip("Filings from {0}".format(raw_year_item))
                        self.real_year_items.append(real_item)
                    for real_year_item in self.real_year_items:
                        for filing_item in self.filing_items:
                            if filing_item.period.split("-")[0] == real_year_item.period:
                                real_year_item.children.append(filing_item)
                        real_year_item.setChildren()
                        self.model().appendRow(real_year_item)
        except Exception as err:
            view_logger.error("{0}:BookFilingTreeView.refresh():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def insertFilingIntoTable(self, selection):
        try:
            current_cik = selection.model().itemFromIndex(selection).cik
            current_period = selection.model().itemFromIndex(selection).period
            if len(current_period) > 4:
                current_period = current_period.split("-")[1].lower() + current_period.split("-")[0]
                current_sub_tab = self.book_main_window.mainTabWidget.currentWidget().findChild(QtWidgets.QTabWidget, "newTab_subTabWidget").currentWidget()
                if current_sub_tab.objectName() == "newTab_numericalTab":
                    num_table_view = self.book_main_window.mainTabWidget.currentWidget().findChild(QtWidgets.QTableView, "numericalTableView")
                    num_table_view.model().insertFilingIntoTable(current_cik, current_period)
                elif current_sub_tab.objectName() == "newTab_textualTab":
                    tex_table_view = self.book_main_window.mainTabWidget.currentWidget().findChild(QtWidgets.QTableView, "textualTableView")
                    tex_table_view.model().insertFilingIntoTable(current_cik, current_period)
        except Exception as err:
            view_logger.error("{0}:BookFilingTreeView.insertFilingIntoTable():{1}".format(str(datetime.datetime.now()), str(err)))

        return

class BookEntityTreeView(QtWidgets.QTreeView):
    """
    BookEntityTreeView
    ~~~~~~~~~~~~~~~~~~
    Customized sub-class of QTreeView; this class implements a refresh function, as well as
        a function for updating the filing tree view when an entity is double-clicked

    Functions
    ~~~~~~~~~
    updateFilingTreeView(self, selection) - updates the filing tree view when an entity is selected
    refresh(self) - if a database is opened/closed, refreshes the tree view to display its entities

    Attributes
    ~~~~~~~~~~
    book_main_window (BookView.BookMainWindow type); provides access to functions and attributes of the 'parental' BookMainWindow instance
    entity_items (list type); collection of BookModel.BookEntityTreeItem instances
    """

    def __init__(self, book_main_window):
        view_logger.info("{0}:Initializing BookEntityTreeView".format(str(datetime.datetime.now())))
        QtWidgets.QTreeView.__init__(self)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.book_main_window = book_main_window
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.doubleClicked.connect(self.updateFilingTreeView)

    def updateFilingTreeView(self, selection):
        try:
            self.book_main_window.filing_tree_view.refresh(selection.model().itemFromIndex(selection).data())
        except Exception as err:
            view_logger.error("{0}:BookEntityTreeView.updateFilingTreeView():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def renameEntity(self, selection):
        try:
            title = "Rename Entity"
            body = "Enter a new name."
            new_name = self.book_main_window.getInputText(title, body)
            if new_name is not None and new_name is not "":
                selection.model().itemFromIndex(selection).model().renameItem(selection.model().itemFromIndex(selection).data(), new_name)
                self.refresh()
        except Exception as err:
            view_logger.error("{0}:BookEntityTreeView.renameEntity():{1}".format(str(datetime.datetime.now()), str(err)))

    def refresh(self):
        try:
            self.model().removeRows(0, self.model().rowCount())
            self.entity_items = []
            self.model().raw_items = None
            self.model().populateRawItems()
            if self.model().raw_items is not None:
                for item in self.model().raw_items:
                    entity = BookModel.BookEntityTreeItem(cik = item[0], parent_cik = item[1], name = item[2])
                    entity.setText(item[2])
                    entity.setToolTip("CIK={0}".format(item[0]))
                    self.entity_items.append(entity)
                for thing in self.entity_items:
                    for sub_thing in self.entity_items:
                        if sub_thing.parent_cik == thing.cik:
                            thing.children.append(sub_thing)
                    thing.setChildren()
                for thang in self.entity_items:
                    if thang.parent_cik == None:
                        self.model().appendRow(thang)
            else:
                pass
        except Exception as err:
            view_logger.error("{0}:BookEntityTreeView.refresh():{1}".format(str(datetime.datetime.now()), str(err)))

        return

class BookStatusBar(QtWidgets.QStatusBar):
    """
    BookStatusBar
    ~~~~~~~~~~~~~
    Customized sub-class of QStatusBar; implements a showMessage function as a slot for the controller

    Functions
    ~~~~~~~~~
    showMessage(self, message, timeout = 5000) - display controller message (i.e., from Arelle) to the main window status bar

    Attributes
    ~~~~~~~~~~
    ui (BookView.BookMainWindow type); provides access to the 'user interface' if necessary in the future
    """

    def __init__(self, ui):
        view_logger.info("{0}:Initializing BookStatusBar".format(str(datetime.datetime.now())))
        QtWidgets.QStatusBar.__init__(self)
        self.ui = ui

    #Slot
    def showMessage(self, message, timeout = 5000):
        try:
            super().showMessage(message, timeout)
            # QtWidgets.QStatusBar.showMessage(message, timeout)
        except Exception as err:
            view_logger.error("{0}:BookStatusBar.showMessage():{1}".format(str(datetime.datetime.now()), str(err)))

        return

class BookTableView(QtWidgets.QTableView):
    """
    BookTableView
    ~~~~~~~~~~~~~
    Customized sub-class of QTableView; this class implements a refreshGraphic function

    Functions
    ~~~~~~~~~
    refreshGraphic(self) - refreshes the graphic associated with this table view

    Attributes
    ~~~~~~~~~~
    parental_frame - (QtWidgets.QFrame type); frame containing the instance of this table view
    book_main_window - (BookMainWindow type); main application window
    graphic - (BookNumericalGraphic or BookTextualGraphic); the graphic (numerical or textual) associated with this table view
    """

    def __init__(self, parental_frame, book_main_window, graphic = None):
        view_logger.info("{0}:Initializing BookTableView".format(str(datetime.datetime.now())))
        QtWidgets.QTableView.__init__(self)
        self.parental_frame = parental_frame
        self.book_main_window = book_main_window
        self.setStyleSheet("padding:0px")
        self.setTabKeyNavigation(True)
        self.graphic = graphic

    def refreshGraphic(self):
        try:
            self.graphic.refreshGraphic()
        except Exception as err:
            view_logger.error("{0}:BookTableView.refreshGraphic():{1}".format(str(datetime.datetime.now()), str(err)))

        return

class BookNumericalGraphic(QtCharts.QChartView):
    """
    BookNumericalGraphic
    ~~~~~~~~~~~~~~~~~~~~
    Customized sub-class of QtCharts.QChartView; implements a refreshGraphic function

    Functions
    ~~~~~~~~~
    refreshGraphic(self) - refreshes the graphic associated with this chart view

    Attributes
    ~~~~~~~~~~
    book_table_view - (BookTableView type); table view associated with this chart view
    """

    def __init__(self, book_table_view):
        view_logger.info("{0}:Initializing BookNumericalGraphic".format(str(datetime.datetime.now())))
        QtCharts.QChartView.__init__(self, book_table_view)
        self.book_table_view = book_table_view
        self.setRenderHint(QPainter.Antialiasing)
        self.setObjectName("numericalGraphic")

    def refreshGraphic(self):
        try:
            self.chart().refreshGraphic()
            self.repaint()
        except Exception as err:
            view_logger.error("{0}:BookNumericalGraphic.refreshGraphic():{1}".format(str(datetime.datetime.now()), str(err)))

        return

class BookNumericalChart(QtCharts.QChart):
    """
    BookNumericalChart
    ~~~~~~~~~~~~~~~~~~
    Customized sub-class of QtCharts.QChart; implements a refreshGraphic function

    Functions
    ~~~~~~~~~
    refreshGraphic(self) - refreshes the QtCharts.QChart according to user-defined settings and facts selected for viewing

    Attributes
    ~~~~~~~~~~
    book_table_view (BookTableView type); table view associated with this chart view
    chart_type (string type); type of chart (e.g., 'bar', 'scatter', 'line'), from book_main_window.pref
    items_viewed (bool type); value depends on whether user has selected table rows for graphing
    """

    def __init__(self, book_table_view):
        view_logger.info("{0}:Initializing BookNumericalChart".format(str(datetime.datetime.now())))
        QtCharts.QChart.__init__(self)
        self.book_table_view = book_table_view
        self.chart_type = self.book_table_view.book_main_window.pref.general_num_graph_type
        self.items_viewed = False

    def refreshGraphic(self):
        try:
            self.chart_type = self.book_table_view.book_main_window.pref.general_num_graph_type

            if self.chart_type == "Bar":
                self.setTheme(QtCharts.QChart.ChartThemeHighContrast)
                self.removeAllSeries()
                self.setBackgroundVisible(True)
                data_series = QtCharts.QBarSeries(self)
                zero_series = QtCharts.QLineSeries(self)
                zero_series.insert(0, QPointF(QPoint(0, 0)))
                bar_set = QtCharts.QBarSet("")
                active_rows = []
                self.items_viewed = False
                for index, item in enumerate(self.book_table_view.model().items):
                    if item[2] == True:
                        self.items_viewed = True
                        try:
                            bar_set.insert(index + 1, float(item[7].replace(",", "")))
                            active_rows.append(str(index + 1))
                        except Exception as err:
                            pass
                zero_series.insert(1, QPointF(QPoint(len(active_rows), 0)))
                zero_series.setColor(QColor(QtCore.Qt.red))
                if self.items_viewed:
                    data_series.append(bar_set)
                    self.addSeries(data_series)
                    self.addSeries(zero_series)
                    self.createDefaultAxes()
                    self.axisX(data_series).setTitleText("Index")
                    self.axisX(data_series).setTitleVisible(True)
                    self.axisX(data_series).setGridLineVisible(False)
                    self.axisX(data_series).setLabelsVisible(True)
                    self.axisX(data_series).setLineVisible(True)
                    self.axisX(data_series).setMinorGridLineVisible(False)
                    self.axisY(data_series).setTitleText("Value (Units)")
                    self.axisY(data_series).setTitleVisible(True)
                    self.axisY(data_series).setGridLineVisible(False)
                    self.axisY(data_series).setLabelsVisible(True)
                    self.axisY(data_series).setLineVisible(True)
                    self.axisY(data_series).setMinorGridLineVisible(False)
                    self.axisX(zero_series).setVisible(False)
                    self.axisY(data_series).applyNiceNumbers()
                    self.axisX(zero_series).setRange(0, len(active_rows))
                    self.setDropShadowEnabled(False)
                    self.setAnimationOptions(QtCharts.QChart.NoAnimation)
                    self.legend().setVisible(False)
                else:
                    self.setDropShadowEnabled(False)
                    self.setAnimationOptions(QtCharts.QChart.NoAnimation)
                    self.legend().setVisible(False)

            elif self.chart_type == "Line":
                self.setTheme(QtCharts.QChart.ChartThemeHighContrast)
                self.removeAllSeries()
                self.setBackgroundVisible(True)
                line_series = QtCharts.QLineSeries(self)
                line_series_data = []
                scatter_series = QtCharts.QScatterSeries(self)
                scatter_series_data = []
                zero_series = QtCharts.QLineSeries(self)
                zero_series.insert(0, QPointF(QPoint(0, 0)))
                self.items_viewed = False
                for index, item in enumerate(self.book_table_view.model().items):
                    if item[2] == True:
                        self.items_viewed = True
                        try:
                            line_series_data.append(QPointF(float(index + 1), float(item[7].replace(",", ""))))
                            scatter_series_data.append(QPointF(float(index + 1), float(item[7].replace(",", ""))))
                        except Exception as err:
                            pass
                    else:
                        pass
                zero_series.insert(1, QPointF(QPoint(len(line_series_data), 0)))
                zero_series.setColor(QColor(QtCore.Qt.red))
                if self.items_viewed:
                    scatter_series.append(scatter_series_data)
                    line_series.append(line_series_data)
                    self.addSeries(scatter_series)
                    self.addSeries(line_series)
                    self.addSeries(zero_series)
                    self.createDefaultAxes()
                    self.axisX(scatter_series).setTitleText("Index")
                    self.axisX(scatter_series).setTitleVisible(True)
                    self.axisX(scatter_series).setGridLineVisible(False)
                    self.axisX(scatter_series).setLabelsVisible(True)
                    self.axisX(scatter_series).setLineVisible(True)
                    self.axisX(scatter_series).setMinorGridLineVisible(False)
                    self.axisY(scatter_series).setTitleText("Value (Units)")
                    self.axisY(scatter_series).setTitleVisible(True)
                    self.axisY(scatter_series).setGridLineVisible(False)
                    self.axisY(scatter_series).setLabelsVisible(True)
                    self.axisY(scatter_series).setLineVisible(True)
                    self.axisY(scatter_series).setMinorGridLineVisible(False)
                    self.axisX(line_series).setVisible(False)
                    self.axisX(zero_series).setVisible(False)
                    self.axisX(scatter_series).setVisible(True)
                    self.axisX(line_series).applyNiceNumbers()
                    self.axisX(line_series).setTickCount(len(line_series_data))
                    self.axisY(line_series).applyNiceNumbers()
                    self.axisX(scatter_series).applyNiceNumbers()
                    self.axisX(scatter_series).setTickCount(len(line_series_data))
                    self.axisY(scatter_series).applyNiceNumbers()
                    self.axisX(line_series).setRange(1, len(line_series_data))
                    self.axisX(zero_series).setRange(1, len(line_series_data))
                    self.setDropShadowEnabled(False)
                    self.setAnimationOptions(QtCharts.QChart.NoAnimation)
                    self.legend().setVisible(False)
                else:
                    self.setDropShadowEnabled(False)
                    self.setAnimationOptions(QtCharts.QChart.NoAnimation)
                    self.legend().setVisible(False)

            elif self.chart_type == "Scatter":
                self.setTheme(QtCharts.QChart.ChartThemeHighContrast)
                self.removeAllSeries()
                self.setBackgroundVisible(True)
                scatter_series = QtCharts.QScatterSeries(self)
                scatter_series_data = []
                zero_series = QtCharts.QLineSeries(self)
                zero_series_data = []
                zero_series.insert(0, QPointF(QPoint(0, 0)))
                self.items_viewed = False
                for index, item in enumerate(self.book_table_view.model().items):
                    if item[2] == True:
                        self.items_viewed = True
                        try:
                            scatter_series_data.append(QPointF(float(index + 1), float(item[7].replace(",", ""))))
                            zero_series_data.append(QPointF(QPoint(index + 1, 0)))
                        except Exception as err:
                            pass
                    else:
                        pass
                zero_series.insert(1, QPointF(QPoint(len(scatter_series_data), 0)))
                zero_series.setColor(QColor(QtCore.Qt.red))
                if self.items_viewed:
                    scatter_series.append(scatter_series_data)
                    self.addSeries(scatter_series)
                    self.addSeries(zero_series)
                    self.createDefaultAxes()
                    self.axisX(scatter_series).setTitleText("Index")
                    self.axisX(scatter_series).setTitleVisible(True)
                    self.axisX(scatter_series).setGridLineVisible(False)
                    self.axisX(scatter_series).setLabelsVisible(True)
                    self.axisX(scatter_series).setLineVisible(True)
                    self.axisX(scatter_series).setMinorGridLineVisible(False)
                    self.axisY(scatter_series).setTitleText("Value (Units)")
                    self.axisY(scatter_series).setTitleVisible(True)
                    self.axisY(scatter_series).setGridLineVisible(False)
                    self.axisY(scatter_series).setLabelsVisible(True)
                    self.axisY(scatter_series).setLineVisible(True)
                    self.axisY(scatter_series).setMinorGridLineVisible(False)
                    self.axisX(zero_series).setVisible(False)
                    self.axisX(scatter_series).setVisible(True)
                    self.axisX(scatter_series).applyNiceNumbers()
                    self.axisX(scatter_series).setTickCount(len(scatter_series_data))
                    self.axisY(scatter_series).applyNiceNumbers()
                    self.axisX(scatter_series).setRange(1, len(scatter_series_data))
                    self.axisX(zero_series).setRange(1, len(scatter_series_data))
                    self.setDropShadowEnabled(False)
                    self.setAnimationOptions(QtCharts.QChart.NoAnimation)
                    self.legend().setVisible(False)
                else:
                    self.setDropShadowEnabled(False)
                    self.setAnimationOptions(QtCharts.QChart.NoAnimation)
                    self.legend().setVisible(False)
        except Exception as err:
            view_logger.error("{0}:BookNumericalChart.refreshGraphic():{1}".format(str(datetime.datetime.now()), str(err)))

        return

class BookTextualGraphic(QtWidgets.QTextEdit):
    """
    BookTextualGraphic
    ~~~~~~~~~~~~~~~~~~
    Customized sub-class of QTextEdit; implements a refreshGraphic function

    Functions
    ~~~~~~~~~
    refreshGraphic(self) - refreshes the QTextEdit according to the facts selected for viewing

    Attributes
    ~~~~~~~~~~
    book_table_view (BookTableView type); table view associated with this chart view
    items_viewed (bool type); value depends on whether user has selected table rows for graphing
    """
    def __init__(self, book_table_view):
        view_logger.info("{0}:Initializing BookTextualGraphic".format(str(datetime.datetime.now())))
        QtWidgets.QTextEdit.__init__(self)
        self.setReadOnly(True)
        self.book_table_view = book_table_view
        self.setObjectName("textualGraphic")
        self.items_viewed = False

    def refreshGraphic(self):
        try:
            self.items_viewed = False
            self.html_string = ""
            self.html = ""
            for item in self.book_table_view.model().items:
                if item[2] == True:
                    self.items_viewed = True
                    self.html_string += str(item[7])
            if self.html_string != "":
                try:
                    self.html = BookFilingUtility.decodeHtml(self.html_string)
                except Exception as err:
                    view_logger.error("{0}:BookTextualGraphic.refreshGraphic() inner:{1}".format(str(datetime.datetime.now()), str(err)))
            self.setHtml(self.html)
            self.update()
            self.show()
        except Exception as err:
            view_logger.error("{0}:BookTextualGraphic.refreshGraphic() outer:{1}".format(str(datetime.datetime.now()), str(err)))

        return
