"""
:mod: 'BookModel'
~~~~~~~~~~~~~~~~~

..  py:module:: BookModel
    :copyright: Copyright BitWorks LLC, All rights reserved.
    :license: MIT
    :synopsis: Collection of PyQt models used by XBRLStudio
    :description: Contains the following classes:

        BookTableModel - model for numerical and textual XBRLStudio tables
        BookEntityTreeModel - model for the entity tree
        BookEntityTreeItem - model for an item within the entity tree
        BookFilingTreeModel - model for the filing tree
        BookFilingTreeItem - model for an item within the filing tree
        BookLineEdit - custom QLineEdit with overridden contextMenuEvent()
        BookTableViewDelegate - delegate object for table editors and models (see Qt model/view documentation)
"""

try:
    import copy, sys, os, datetime, logging
    model_logger = logging.getLogger()
    from PySide2 import (QtCore, QtWidgets, QtGui)
    # Tiered
    # from . import BookFilingUtility
    # Flat
    import BookFilingUtility
except Exception as err:
    model_logger.error("{0}:BookModel import error:{1}".format(str(datetime.datetime.now()), str(err)))

class BookTableModel(QtCore.QAbstractTableModel):
    """
    BookTableModel
    ~~~~~~~~~~~~~~
    Customized sub-class of QAbstractTableModel; this class implements all the required model functions, as well as
        a function for inserting a selected entity/filing pair into the table model

    Functions
    ~~~~~~~~~
    rowCount(self, parent) - returns row_count, the number of rows in the table
    addRows(self, num_rows) - appends user-defined number of rows to the table
    columnCount(self, parent) - returns the number of columns in the table, based on the table type
    data(self, index, role) - returns the items object at the given index position, for the given role
    headerData(self, section, orientation, role) - sets labels for the columns, and other column attributes
    setData(self, index, value, role) - assigns an items object to be equal to the given value, according to position (index) and role
    insertFilingIntoTable(self, current_cik, current_period) - inserts the selected entity name and filing into items
    flags(self, index) - function for QAbstractTableModel flags; defines aspects of the different columns
    setHeaderData(self, section, orientation, value, role) - default implementation of QAbstractTableModel.setHeaderData
    fillDown(self, index, fill_text) - fills a column (downwards) with text in fill_text at given index
    viewAll(self) - sets all rows to be viewed in table's graphic (numerical or textual)

    Attributes
    ~~~~~~~~~~
    book_table_view - (BookView.BookTableView type); view for instances of this model
    row_count - (int type); number of rows (initialized to be 10)
    items - (list type); main model collection of bool, string, and int values for use by the view
    view_indices - (list type); used (e.g., by BookView.BookMainWindow instance) to create persistent checkboxes in 'View' column
    sub_items - (list type); used during the initial creation of the items matrix (items[row][column])
    """

    def __init__(self, book_table_view):
        model_logger.info("{0}:Initializing BookTableModel".format(str(datetime.datetime.now())))
        QtCore.QAbstractTableModel.__init__(self)
        self.book_table_view = book_table_view
        self.row_count = 10
        self.items = []
        self.view_indices = []
        #cik, period, view, entity, filing, fact, context, value, unit, dec
        self.sub_items = [None, None, None, None, None, None, None, None, None, None]
        for i in range(0, self.row_count):
            self.items.append(copy.deepcopy(self.sub_items))
        if self.book_table_view.objectName() == "numericalTableView":
            self.setObjectName("numericalTableModel")
        elif self.book_table_view.objectName() == "textualTableView":
            self.setObjectName("textualTableModel")
        else:
            model_logger.error("{0}:BookTableModel.book_table_view.objectName(): unacceptable return value".format(str(datetime.datetime.now())))

    def rowCount(self, parent):

        return self.row_count

    def addRows(self, num_rows):
        self.layoutAboutToBeChanged.emit()

        for i in range(self.row_count, self.row_count + num_rows):
            self.items.append(copy.deepcopy(self.sub_items))
        self.row_count += num_rows

        self.layoutChanged.emit()

        return

    def columnCount(self, parent):
        if self.objectName() == "textualTableModel":
            return 5
        elif self.objectName() == "numericalTableModel":
            return 8
        else:
            model_logger.error("{0}:BookTableModel.columnCount(): unacceptable object name".format(str(datetime.datetime.now())))

    def data(self, index, role):
        if not index.isValid():
            model_logger.warning("{0}:BookTableModel.data(): invalid index".format(str(datetime.datetime.now())))
            return
        if index.column() == 0:
            if len(self.view_indices) < self.row_count:
                row = len(self.view_indices)
                while row < self.row_count:
                    self.view_indices.append(index.sibling(row, 0))
                    row += 1
            if role == QtCore.Qt.DisplayRole:
                pass
            elif role == QtCore.Qt.DecorationRole:
                return QtCore.Qt.AlignCenter
            elif role == QtCore.Qt.EditRole:
                return self.items[index.row()][index.column() + 2]
        elif index.column() in (1, 2, 3, 4):
            if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
                return self.items[index.row()][index.column() + 2]
        elif index.column() in (5, 6, 7):
            if role == QtCore.Qt.DisplayRole:
                if self.objectName() == "numericalTableModel":
                    return self.items[index.row()][index.column() + 2]
                elif self.objectName() == "textualTableModel":
                    return None
            if index.column() == 5:
                if role == QtCore.Qt.TextAlignmentRole:
                    return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
            if index.column() == 6 or index.column() == 7:
                if role == QtCore.Qt.TextAlignmentRole:
                    return QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        else:
            model_logger.warning("{0}:BookTableModel.data(): invalid index.column()".format(str(datetime.datetime.now())))
            return

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if section == 0:
                if role == QtCore.Qt.DisplayRole:
                    return "View"
                elif role == QtCore.Qt.SizeHintRole:
                    return QtCore.QSize(45, 25)
            elif section == 1:
                if role == QtCore.Qt.DisplayRole:
                    return "Entity"
                elif role == QtCore.Qt.SizeHintRole:
                    return QtCore.QSize(100, 25)
            elif section == 2:
                if role == QtCore.Qt.DisplayRole:
                    return "Filing"
                elif role == QtCore.Qt.SizeHintRole:
                    return QtCore.QSize(100, 25)
            elif section == 3:
                if role == QtCore.Qt.DisplayRole:
                    return "Fact"
                elif role == QtCore.Qt.SizeHintRole:
                    return QtCore.QSize(100, 25)
            elif section == 4:
                if role == QtCore.Qt.DisplayRole:
                    return "Context"
                elif role == QtCore.Qt.SizeHintRole:
                    return QtCore.QSize(100, 25)
            elif section == 5:
                if role == QtCore.Qt.DisplayRole:
                    return "Value"
                elif role == QtCore.Qt.SizeHintRole:
                    return QtCore.QSize(100, 25)
            elif section == 6:
                if role == QtCore.Qt.DisplayRole:
                    return "Unit"
                elif role == QtCore.Qt.SizeHintRole:
                    return QtCore.QSize(100, 25)
            elif section == 7:
                if role == QtCore.Qt.DisplayRole:
                    return "Dec"
                elif role == QtCore.Qt.SizeHintRole:
                    return QtCore.QSize(100, 25)
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return str(section + 1)
            elif role == QtCore.Qt.SizeHintRole:
                return QtCore.QSize(40, 25)

        return

    def setData(self, index, value, role):
        try:
            if value is not None and index.isValid():
                if index.column() == 0: #view toggled
                    self.book_table_view.closePersistentEditor(index)
                    self.items[index.row()][2] = value
                    self.book_table_view.openPersistentEditor(index)
                    self.book_table_view.refreshGraphic()
                elif index.column() == 1: #entity selected (set cik)
                    # TODO - rearrange for this to be cik_name_dict ({cik:name})
                    name_cik_dict = self.book_table_view.book_main_window.cntlr.book_filing_manager.getEntityDict()
                    current_cik = int(name_cik_dict[value])
                    self.items[index.row()][0] = current_cik
                    self.items[index.row()][3] = value
                elif index.column() == 2: #filing selected (set period)
                    current_period = value.split("-")[1].lower() + value.split("-")[0]
                    self.items[index.row()][1] = current_period
                    self.items[index.row()][4] = value
                elif index.column() == 3: #fact selected
                    self.items[index.row()][5] = value
                elif index.column() == 4: #context selected (set value and unit)
                    self.items[index.row()][6] = value
                    current_cik = self.items[index.row()][0]
                    current_period = self.items[index.row()][1]
                    current_filing = self.book_table_view.book_main_window.cntlr.book_filing_manager.getFiling(current_cik, current_period)
                    current_fact_name = self.items[index.row()][5]
                    current_context = str(value)
                    current_facts = set()
                    if current_filing is not None:
                        for fact_item in current_filing.facts:
                            if fact_item.label == current_fact_name:
                                if fact_item.context_ref == current_context:
                                    current_facts.add(fact_item)
                    if len(current_facts) == 1:
                        if self.objectName() == "numericalTableModel":
                            self.items[index.row()][7] = list(current_facts)[0].value
                            self.items[index.row()][8] = list(current_facts)[0].unit_ref
                            self.items[index.row()][9] = list(current_facts)[0].dec
                        elif self.objectName() == "textualTableModel":
                            self.items[index.row()][7] = list(current_facts)[0].value
                            self.items[index.row()][8] = list(current_facts)[0].unit_ref
                            self.items[index.row()][9] = list(current_facts)[0].dec
                    elif len(current_facts) != 1:
                        return False
                self.book_table_view.refreshGraphic()
                return True
        except Exception as err:
            model_logger.error("{0}:BookTableModel.setData():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def insertFilingIntoTable(self, current_cik, current_period):
        try:
            current_filing = self.book_table_view.book_main_window.cntlr.getFiling(current_cik, current_period)
            entity_name = self.book_table_view.book_main_window.cntlr.getNameFromCik(current_cik)
            pretty_filing_period = current_period[2:6] + "-" + current_period[0:2].upper()
            i = 0
            while i < self.row_count:
                if self.items[i][0] == None:
                    self.items[i][0] = int(current_cik)
                    self.items[i][1] = current_period
                    self.items[i][3] = entity_name
                    self.items[i][4] = pretty_filing_period
                    self.book_table_view.update()
                    i = self.row_count
                i += 1
        except Exception as err:
            model_logger.error("{0}:BookTableModel.insertFilingIntoTable():{1}".format(str(datetime.datetime.now()), str(err)))

    def flags(self, index):
        try:
            if not index.isValid():
                model_logger.info("{0}:BookTableModel.flags(): invalid index".format(str(datetime.datetime.now())))
                return QtCore.Qt.ItemIsEnabled
            if index.column() == 0:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
            elif index.column() == 1 or index.column() == 2:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDropEnabled
            elif index.column() == 3 or index.column() == 4:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable
            elif index.column() == 5 or index.column() == 6 or index.column() == 7:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable
            else:
                model_logger.warning("{0}:BookTableModel.flags(): invalid index.column()".format(str(datetime.datetime.now())))
        except Exception as err:
            model_logger.error("{0}:BookTableModel.flags():{1}".format(str(datetime.datetime.now()), str(err)))

    def setHeaderData(self, section, orientation, value, role):
        QtCore.QAbstractTableModel.setHeaderData(self, section, orientation, value, role)

        return

    def fillDown(self, index, fill_text):
        try:
            row_pos = index.row()
            col_pos = index.column()
            num_rows = self.row_count - row_pos
            if num_rows > 0:
                try:
                    if fill_text is not None and fill_text is not "":
                        i = row_pos
                        while i < self.row_count:
                            current_index = self.createIndex(i, col_pos)
                            self.setData(current_index, fill_text, QtCore.Qt.EditRole)
                            i += 1
                    self.book_table_view.update()
                except Exception as err:
                    model_logger.error("{0}:BookTableModel.fillDown():{1}".format(str(datetime.datetime.now()), str(err)))
        except Exception as err:
            model_logger.error("{0}:BookTableModel.fillDown():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def viewAll(self):
        try:
            i = 0
            while i < self.row_count:
                current_index = self.createIndex(i, 0)
                self.setData(current_index, True, QtCore.Qt.EditRole)
                i += 1
            self.book_table_view.update()
        except Exception as err:
            model_logger.error("{0}:BookTableModel.viewAll():{1}".format(str(datetime.datetime.now()), str(err)))

        return

class BookEntityTreeModel(QtGui.QStandardItemModel):
    """
    BookEntityTreeModel
    ~~~~~~~~~~~~~~~~~~~
    Customized sub-class of QStandardItemModel

    Functions
    ~~~~~~~~~
    itemMoved(self, item_changed) - updates parent_cik for the entity moved
    populateRawItems(self) - uses the controller to query the database and get entity tree information
    renameItem(self, target_cik, new_name) - uses the controller to rename an entity in the database
    flags(self, index) - enables drag and drop for entity tree, for reorganization of entity hierarchy

    Attributes
    ~~~~~~~~~~
    book_main_window - (BookView.BookMainWindow type); for accessing main window object, such as controller
    raw_items - (list type); list of tuples in the format [(entity_cik, parent_cik, entity_name)]
    itemChanged - (signal type); QStandardItemModel built-in signal, triggered when an item is modified/moved
    """

    def __init__(self, book_main_window, raw_items = None):
        model_logger.info("{0}:Initializing BookEntityTreeModel".format(str(datetime.datetime.now())))
        QtGui.QStandardItemModel.__init__(self)
        self.book_main_window = book_main_window
        self.raw_items = raw_items
        self.itemChanged.connect(self.itemMoved)

    def itemMoved(self, item_changed):
        child_cik = item_changed.data()
        try:
            parent_cik = item_changed.parent().data()
        except AttributeError:
            parent_cik = None
        update_attempt = self.book_main_window.cntlr.updateParentInfo(child_cik, parent_cik)
        if update_attempt:
            self.book_main_window.entity_tree_view.refresh()
            return
        else:
            model_logger.error("{0}:BookEntityTreeModel.itemMoved(): update attempt failed".format(str(datetime.datetime.now())))
            return

    def populateRawItems(self):
        try:
            self.raw_items = self.book_main_window.cntlr.book_filing_manager.getEntityTreeInfo()
        except Exception as err:
            model_logger.error("{0}:BookEntityTreeModel.populateRawItems():{1}".format(str(datetime.datetime.now()), str(err)))

        return

    def renameItem(self, target_cik, new_name):
        try:
            self.book_main_window.cntlr.renameEntity(target_cik, new_name)
        except Exception as err:
            model_logger.error("{0}:BookEntityTreeModel.renameItem():{1}".format(str(datetime.datetime.now()), str(err)))

    def flags(self, index):
        try:
            flags = super().flags(index)
            if index.isValid():
                flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled

            return flags
        except Exception as err:
            model_logger.error("{0}:BookEntityTreeModel.flags():{1}".format(str(datetime.datetime.now()), str(err)))

            return

class BookEntityTreeItem(QtGui.QStandardItem):
    """
    BookEntityTreeItem
    ~~~~~~~~~~~~~~~~~~
    Customized sub-class of QStandardItem

    Functions
    ~~~~~~~~~
    setChildren(self) - assigns children objects as QStandardItem children to construct the entity tree

    Attributes
    ~~~~~~~~~~
    cik - (string or int type); central index key, set as QStandardItem instance data
    parent_cik - (string or int type); parent entity central index key
    name - (string type); entity name
    children - (list type); list of children BookEntityTreeItem objects
    """

    def __init__(self, cik, parent_cik, name, children = None):
        model_logger.info("{0}:Initializing BookEntityTreeItem".format(str(datetime.datetime.now())))
        QtGui.QStandardItem.__init__(self)
        self.setEditable(False)
        self.cik = cik
        self.parent_cik = parent_cik
        self.name = name
        self.children = []
        self.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
        self.setData(self.cik)

    def setChildren(self):
        try:
            for row, child in enumerate(self.children):
                self.setChild(row, child)
        except Exception as err:
            model_logger.error("{0}:BookEntityTreeItem.setChildren():{1}".format(str(datetime.datetime.now()), str(err)))

class BookFilingTreeModel(QtGui.QStandardItemModel):
    """
    BookFilingTreeModel
    ~~~~~~~~~~~~~~~~~~~
    Customized sub-class of QStandardItemModel

    Functions
    ~~~~~~~~~
    populateRawItems(self) - uses the controller to query the database and get filing tree information

    Attributes
    ~~~~~~~~~~
    book_main_window - (BookView.BookMainWindow type); for accessing main window object, such as controller
    raw_items - (list type); list of tuples in the format [(entity_cik, parent_cik, entity_name)]
    """

    def __init__(self, book_main_window, raw_items = None):
        model_logger.info("{0}:Initializing BookFilingTreeModel".format(str(datetime.datetime.now())))
        QtGui.QStandardItemModel.__init__(self)
        self.book_main_window = book_main_window
        self.raw_items = raw_items

    def populateRawItems(self, target_cik):
        try:
            if target_cik is not None:
                self.raw_items = self.book_main_window.cntlr.book_filing_manager.getFilingTreeInfo(target_cik)
        except Exception as err:
            model_logger.error("{0}:BookFilingTreeModel.populateRawItems():{1}".format(str(datetime.datetime.now()), str(err)))

class BookFilingTreeItem(QtGui.QStandardItem):
    """
    BookFilingTreeItem
    ~~~~~~~~~~~~~~~~~~
    Customized sub-class of QStandardItem

    Functions
    ~~~~~~~~~
    setChildren(self) - assigns children objects as QStandardItem children to construct the filing tree

    Attributes
    ~~~~~~~~~~
    cik - (string or int type); central index key, set as QStandardItem instance data
    period - (string type); period descriptor
    children - (list type); list of children BookEntityTreeItem objects
    """

    def __init__(self, period, cik = None, children = None):
        model_logger.info("{0}:Initializing BookFilingTreeItem".format(str(datetime.datetime.now())))
        QtGui.QStandardItem.__init__(self)
        self.cik = cik
        self.period = period
        self.children = []
        self.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def setChildren(self):
        try:
            for row, child in enumerate(self.children):
                self.setChild(row, child)
        except Exception as err:
            model_logger.error("{0}:BookFilingTreeItem.setChildren():{1}".format(str(datetime.datetime.now()), str(err)))

class BookLineEdit(QtWidgets.QLineEdit):
    """
    BookLineEdit
    ~~~~~~~~~~~~
    Customized sub-class of QLineEdit

    Functions
    ~~~~~~~~~
    contextMenuEvent(self, event) - overrides QLineEdit context menu to add "fill down" option

    Attributes
    ~~~~~~~~~~
    parent - (unknown type) - required argument (see Qt documentation)
    index - (unknown type) - required argument (see Qt documentation)
    book_table_view - (BookView.BookTableView type) - allows access to book table view for fill down functionality
    menu - standard context menu for QLineEdit
    action_fill_down - (QAction type) - activates the fill down functionality in the current book table model using a lambda function
    """

    def __init__(self, parent, index):
        model_logger.info("{0}:Initializing BookLineEdit".format(str(datetime.datetime.now())))
        QtWidgets.QLineEdit.__init__(self)
        self.parent = parent
        self.index = index
        self.book_table_view = self.parent.parent()
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.setObjectName("BookLineEdit")

    def contextMenuEvent(self, event):
        try:
            self.menu = self.createStandardContextMenu()
            self.menu.addSeparator()
            self.action_fill_down = self.menu.addAction("Fill Down")
            self.action_fill_down.triggered.connect(lambda x: self.book_table_view.model().fillDown(self.index, self.text()))
            self.menu.exec_(event.globalPos())
            del(self.menu)
        except Exception as err:
            model_logger.error("{0}:BookLineEdit.contextMenuEvent():{1}".format(str(datetime.datetime.now()), str(err)))

        return

class BookTableViewDelegate(QtWidgets.QStyledItemDelegate):
    """
    BookTableViewDelegate
    ~~~~~~~~~~~~~~~~~~~~~
    Customized sub-class of QStyledItemDelegate

    Functions
    ~~~~~~~~~
    paint(self, painter, option, index) - default implementation of QStyledItemDelegate.paint function
    sizeHint(self, option, index) - default implementation of QStyledItemDelegate.sizeHint function
    createEditor(self, parent, option, index) - custom implementation, creates at least a combobox for the view
    setEditorData(self, editor, index) - sets the editor data to be equal to the current selection
    setModelData(self, editor, model, index) - sets the model data to be equal to the current selection
    updateEditorGeometry(self, editor, option, index) - default implmentation of QStyledItemDelegate.updateEditorGeometry function

    Attributes
    ~~~~~~~~~~
    book_table_view - (BookView.BookTableView type); view for instances of this model (model accessed via index)
    """

    def __init__(self, book_table_view):
        model_logger.info("{0}:Initializing BookTableViewDelegate".format(str(datetime.datetime.now())))
        QtWidgets.QStyledItemDelegate.__init__(self)
        self.book_table_view = book_table_view

    def paint(self, painter, option, index):
        QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

        return

    def sizeHint(self, option, index):

        return QtWidgets.QStyledItemDelegate.sizeHint(self, option, index)

    def createEditor(self, parent, option, index):
        if self.book_table_view.objectName() == "numericalTableView":
            if index.column() == 0: #View
                self.num_view_ch = QtWidgets.QCheckBox(parent)
                self.num_view_ch.toggled.connect(self.book_table_view.refreshGraphic)
                return self.num_view_ch
            elif index.column() == 1: #Entity
                self.num_entity_cb = QtWidgets.QComboBox(parent)
                self.num_entity_cb.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon)
                try:
                    # [cik, parent_cik, name]
                    self.num_entity_tree_info = self.book_table_view.book_main_window.cntlr.book_filing_manager.getEntityTreeInfo()
                    self.entity_list = []
                    for item in self.num_entity_tree_info:
                        self.entity_list.append(item[2])
                    self.num_entity_cb.addItems(self.entity_list)
                    self.num_entity_cb.setEditable(True)
                    self.num_entity_le = BookLineEdit(parent, index)

                    self.num_entity_le.undoAvailable = True
                    self.num_entity_le.redoAvailable = True
                    self.book_table_view.book_main_window.actionUndo.triggered.connect(self.num_entity_le.undo)
                    self.book_table_view.book_main_window.actionRedo.triggered.connect(self.num_entity_le.redo)
                    self.book_table_view.book_main_window.actionCut.triggered.connect(self.num_entity_le.cut)
                    self.book_table_view.book_main_window.actionCopy.triggered.connect(self.num_entity_le.copy)
                    self.book_table_view.book_main_window.actionPaste.triggered.connect(self.num_entity_le.paste)
                    self.book_table_view.book_main_window.actionDelete.triggered.connect(self.num_entity_le.backspace)
                    self.book_table_view.book_main_window.actionSelectAll.triggered.connect(self.num_entity_le.selectAll)

                    self.num_entity_cb.setLineEdit(self.num_entity_le)
                    self.num_entity_cm = QtWidgets.QCompleter(self)
                    self.num_entity_sl = QtCore.QStringListModel(self)
                    self.num_entity_cm.setModel(self.num_entity_sl)
                    self.num_entity_cm.setCompletionRole(QtCore.Qt.EditRole)
                    self.num_entity_sl.setStringList(sorted(self.entity_list))
                    self.num_entity_cb.setCompleter(self.num_entity_cm)
                    # self.num_entity_le.setFrame(False)
                    # self.num_entity_le.setTextMargins(0, 0, 10, 0)
                    # self.num_entity_le.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
                except Exception as err:
                    return self.num_entity_cb
                return self.num_entity_cb
            elif index.column() == 2: #Filing
                self.num_filing_cb = QtWidgets.QComboBox(parent)
                self.num_filing_cb.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon)
                try:
                    self.current_cik = self.book_table_view.model().items[index.row()][0]
                    self.num_filing_tree_info = self.book_table_view.book_main_window.cntlr.book_filing_manager.getFilingTreeInfo(self.current_cik)
                    self.num_filing_cb.addItems(self.num_filing_tree_info)
                    self.num_filing_cb.setEditable(True)
                    self.num_filing_le = BookLineEdit(parent, index)

                    self.num_filing_le.undoAvailable = True
                    self.num_filing_le.redoAvailable = True
                    self.book_table_view.book_main_window.actionUndo.triggered.connect(self.num_filing_le.undo)
                    self.book_table_view.book_main_window.actionRedo.triggered.connect(self.num_filing_le.redo)
                    self.book_table_view.book_main_window.actionCut.triggered.connect(self.num_filing_le.cut)
                    self.book_table_view.book_main_window.actionCopy.triggered.connect(self.num_filing_le.copy)
                    self.book_table_view.book_main_window.actionPaste.triggered.connect(self.num_filing_le.paste)
                    self.book_table_view.book_main_window.actionDelete.triggered.connect(self.num_filing_le.backspace)
                    self.book_table_view.book_main_window.actionSelectAll.triggered.connect(self.num_filing_le.selectAll)

                    self.num_filing_cb.setLineEdit(self.num_filing_le)
                    self.num_filing_cm = QtWidgets.QCompleter(self)
                    self.num_filing_sl = QtCore.QStringListModel(self)
                    self.num_filing_cm.setModel(self.num_filing_sl)
                    self.num_filing_cm.setCompletionRole(QtCore.Qt.EditRole)
                    self.num_filing_sl.setStringList(sorted(self.num_filing_tree_info))
                    self.num_filing_cb.setCompleter(self.num_filing_cm)
                except Exception as err:
                    return self.num_filing_cb
                return self.num_filing_cb
            elif index.column() == 3: #Fact
                self.num_fact_cb = QtWidgets.QComboBox(parent)
                self.num_fact_cb.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon)
                try:
                    self.current_cik = self.book_table_view.model().items[index.row()][0]
                    self.current_period = self.book_table_view.model().items[index.row()][1]
                    self.num_filing = self.book_table_view.book_main_window.cntlr.book_filing_manager.getFiling(self.current_cik, self.current_period)
                    self.num_fact_labels = set()
                    for fact_item in self.num_filing.facts:
                        if not BookFilingUtility.isAlphaOrHtml(fact_item):
                            self.num_fact_labels.add(fact_item.label)
                    self.num_fact_cb.addItems(sorted(list(self.num_fact_labels)))
                    self.num_fact_cb.setEditable(True)
                    self.num_fact_le = BookLineEdit(parent, index)

                    self.num_fact_le.undoAvailable = True
                    self.num_fact_le.redoAvailable = True
                    self.book_table_view.book_main_window.actionUndo.triggered.connect(self.num_fact_le.undo)
                    self.book_table_view.book_main_window.actionRedo.triggered.connect(self.num_fact_le.redo)
                    self.book_table_view.book_main_window.actionCut.triggered.connect(self.num_fact_le.cut)
                    self.book_table_view.book_main_window.actionCopy.triggered.connect(self.num_fact_le.copy)
                    self.book_table_view.book_main_window.actionPaste.triggered.connect(self.num_fact_le.paste)
                    self.book_table_view.book_main_window.actionDelete.triggered.connect(self.num_fact_le.backspace)
                    self.book_table_view.book_main_window.actionSelectAll.triggered.connect(self.num_fact_le.selectAll)

                    self.num_fact_cb.setLineEdit(self.num_fact_le)
                    self.num_fact_cm = QtWidgets.QCompleter(self)
                    self.num_fact_sl = QtCore.QStringListModel(self)
                    self.num_fact_cm.setModel(self.num_fact_sl)
                    self.num_fact_cm.setCompletionRole(QtCore.Qt.EditRole)
                    self.num_fact_sl.setStringList(sorted(list(self.num_fact_labels)))
                    self.num_fact_cb.setCompleter(self.num_fact_cm)
                except:
                    return self.num_fact_cb
                return self.num_fact_cb
            elif index.column() == 4: #Context
                self.num_con_cb = QtWidgets.QComboBox(parent)
                self.num_con_cb.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon)
                try:
                    self.current_cik = self.book_table_view.model().items[index.row()][0]
                    self.current_period = self.book_table_view.model().items[index.row()][1]
                    self.num_filing = self.book_table_view.book_main_window.cntlr.book_filing_manager.getFiling(self.current_cik, self.current_period)
                    self.current_fact_name = self.book_table_view.model().items[index.row()][5]
                    self.num_fact_contexts = set()
                    for fact_item in self.num_filing.facts:
                        if fact_item.label == self.current_fact_name:
                            self.num_fact_contexts.add(fact_item.context_ref)
                    self.num_con_cb.addItems(sorted(list(self.num_fact_contexts)))
                    self.num_con_cb.setEditable(True)
                    self.num_con_le = BookLineEdit(parent, index)

                    self.num_con_le.undoAvailable = True
                    self.num_con_le.redoAvailable = True
                    self.book_table_view.book_main_window.actionUndo.triggered.connect(self.num_con_le.undo)
                    self.book_table_view.book_main_window.actionRedo.triggered.connect(self.num_con_le.redo)
                    self.book_table_view.book_main_window.actionCut.triggered.connect(self.num_con_le.cut)
                    self.book_table_view.book_main_window.actionCopy.triggered.connect(self.num_con_le.copy)
                    self.book_table_view.book_main_window.actionPaste.triggered.connect(self.num_con_le.paste)
                    self.book_table_view.book_main_window.actionDelete.triggered.connect(self.num_con_le.backspace)
                    self.book_table_view.book_main_window.actionSelectAll.triggered.connect(self.num_con_le.selectAll)

                    self.num_con_cb.setLineEdit(self.num_con_le)
                    self.num_con_cm = QtWidgets.QCompleter(self)
                    self.num_con_sl = QtCore.QStringListModel(self)
                    self.num_con_cm.setModel(self.num_fact_sl)
                    self.num_con_cm.setCompletionRole(QtCore.Qt.EditRole)
                    self.num_con_sl.setStringList(sorted(list(self.num_fact_contexts)))
                    self.num_con_cb.setCompleter(self.num_con_cm)
                except:
                    return self.num_con_cb
                return self.num_con_cb

        elif self.book_table_view.objectName() == "textualTableView":
            if index.column() == 0: #View
                self.tex_view_ch = QtWidgets.QCheckBox(parent)
                self.tex_view_ch.toggled.connect(self.book_table_view.refreshGraphic)
                return self.tex_view_ch
            elif index.column() == 1: #Entity
                self.tex_entity_cb = QtWidgets.QComboBox(parent)
                try:
                    # cik, parent_cik, name
                    self.tex_entity_tree_info = self.book_table_view.book_main_window.cntlr.book_filing_manager.getEntityTreeInfo()
                    self.entity_list = []
                    for item in self.tex_entity_tree_info:
                        self.entity_list.append(item[2])
                    self.tex_entity_cb.addItems(self.entity_list)
                    self.tex_entity_cb.setEditable(True)
                    self.tex_entity_le = BookLineEdit(parent, index)

                    self.tex_entity_le.undoAvailable = True
                    self.tex_entity_le.redoAvailable = True
                    self.book_table_view.book_main_window.actionUndo.triggered.connect(self.tex_entity_le.undo)
                    self.book_table_view.book_main_window.actionRedo.triggered.connect(self.tex_entity_le.redo)
                    self.book_table_view.book_main_window.actionCut.triggered.connect(self.tex_entity_le.cut)
                    self.book_table_view.book_main_window.actionCopy.triggered.connect(self.tex_entity_le.copy)
                    self.book_table_view.book_main_window.actionPaste.triggered.connect(self.tex_entity_le.paste)
                    self.book_table_view.book_main_window.actionDelete.triggered.connect(self.tex_entity_le.backspace)
                    self.book_table_view.book_main_window.actionSelectAll.triggered.connect(self.tex_entity_le.selectAll)

                    self.tex_entity_cb.setLineEdit(self.tex_entity_le)
                    self.tex_entity_cm = QtWidgets.QCompleter(self)
                    self.tex_entity_sl = QtCore.QStringListModel(self)
                    self.tex_entity_cm.setModel(self.tex_entity_sl)
                    self.tex_entity_cm.setCompletionRole(QtCore.Qt.EditRole)
                    self.tex_entity_sl.setStringList(sorted(self.entity_list))
                    self.tex_entity_cb.setCompleter(self.tex_entity_cm)
                except:
                    return self.tex_entity_cb
                return self.tex_entity_cb
            elif index.column() == 2: #Filing
                self.tex_filing_cb = QtWidgets.QComboBox(parent)
                try:
                    self.current_cik = self.book_table_view.model().items[index.row()][0]
                    self.tex_filing_tree_info = self.book_table_view.book_main_window.cntlr.book_filing_manager.getFilingTreeInfo(self.current_cik)
                    self.tex_filing_cb.addItems(self.tex_filing_tree_info)
                    self.tex_filing_cb.setEditable(True)
                    self.tex_filing_le = BookLineEdit(parent, index)

                    self.tex_filing_le.undoAvailable = True
                    self.tex_filing_le.redoAvailable = True
                    self.book_table_view.book_main_window.actionUndo.triggered.connect(self.tex_filing_le.undo)
                    self.book_table_view.book_main_window.actionRedo.triggered.connect(self.tex_filing_le.redo)
                    self.book_table_view.book_main_window.actionCut.triggered.connect(self.tex_filing_le.cut)
                    self.book_table_view.book_main_window.actionCopy.triggered.connect(self.tex_filing_le.copy)
                    self.book_table_view.book_main_window.actionPaste.triggered.connect(self.tex_filing_le.paste)
                    self.book_table_view.book_main_window.actionDelete.triggered.connect(self.tex_filing_le.backspace)
                    self.book_table_view.book_main_window.actionSelectAll.triggered.connect(self.tex_filing_le.selectAll)

                    self.tex_filing_cb.setLineEdit(self.tex_filing_le)
                    self.tex_filing_cm = QtWidgets.QCompleter(self)
                    self.tex_filing_sl = QtCore.QStringListModel(self)
                    self.tex_filing_cm.setModel(self.tex_filing_sl)
                    self.tex_filing_cm.setCompletionRole(QtCore.Qt.EditRole)
                    self.tex_filing_sl.setStringList(sorted(self.tex_filing_tree_info))
                    self.tex_filing_cb.setCompleter(self.tex_filing_cm)
                except:
                    return self.tex_filing_cb
                return self.tex_filing_cb
            elif index.column() == 3: #Fact
                self.tex_fact_cb = QtWidgets.QComboBox(parent)
                try:
                    self.current_cik = self.book_table_view.model().items[index.row()][0]
                    self.current_period = self.book_table_view.model().items[index.row()][1]
                    self.tex_filing = self.book_table_view.book_main_window.cntlr.book_filing_manager.getFiling(self.current_cik, self.current_period)
                    self.tex_fact_labels = set()
                    for fact_item in self.tex_filing.facts:
                        if BookFilingUtility.isAlphaOrHtml(fact_item):
                            self.tex_fact_labels.add(fact_item.label)
                    self.tex_fact_cb.addItems(sorted(list(self.tex_fact_labels)))
                    self.tex_fact_cb.setEditable(True)
                    self.tex_fact_le = BookLineEdit(parent, index)

                    self.tex_fact_le.undoAvailable = True
                    self.tex_fact_le.redoAvailable = True
                    self.book_table_view.book_main_window.actionUndo.triggered.connect(self.tex_fact_le.undo)
                    self.book_table_view.book_main_window.actionRedo.triggered.connect(self.tex_fact_le.redo)
                    self.book_table_view.book_main_window.actionCut.triggered.connect(self.tex_fact_le.cut)
                    self.book_table_view.book_main_window.actionCopy.triggered.connect(self.tex_fact_le.copy)
                    self.book_table_view.book_main_window.actionPaste.triggered.connect(self.tex_fact_le.paste)
                    self.book_table_view.book_main_window.actionDelete.triggered.connect(self.tex_fact_le.backspace)
                    self.book_table_view.book_main_window.actionSelectAll.triggered.connect(self.tex_fact_le.selectAll)

                    self.tex_fact_cb.setLineEdit(self.tex_fact_le)
                    self.tex_fact_cm = QtWidgets.QCompleter(self)
                    self.tex_fact_sl = QtCore.QStringListModel(self)
                    self.tex_fact_cm.setModel(self.tex_fact_sl)
                    self.tex_fact_cm.setCompletionRole(QtCore.Qt.EditRole)
                    self.tex_fact_sl.setStringList(sorted(list(self.tex_fact_labels)))
                    self.tex_fact_cb.setCompleter(self.tex_fact_cm)
                except:
                    return self.tex_fact_cb
                return self.tex_fact_cb
            elif index.column() == 4: #Context
                self.tex_con_cb = QtWidgets.QComboBox(parent)
                try:
                    self.current_cik = self.book_table_view.model().items[index.row()][0]
                    self.current_period = self.book_table_view.model().items[index.row()][1]
                    self.tex_filing = self.book_table_view.book_main_window.cntlr.book_filing_manager.getFiling(self.current_cik, self.current_period)
                    self.current_fact_name = self.book_table_view.model().items[index.row()][5]
                    self.tex_fact_contexts = set()
                    for fact_item in self.tex_filing.facts:
                        if fact_item.label == self.current_fact_name:
                            self.tex_fact_contexts.add(fact_item.context_ref)
                    self.tex_con_cb.addItems(sorted(list(self.tex_fact_contexts)))
                    self.tex_con_cb.setEditable(True)
                    self.tex_con_le = BookLineEdit(parent, index)

                    self.tex_con_le.undoAvailable = True
                    self.tex_con_le.redoAvailable = True
                    self.book_table_view.book_main_window.actionUndo.triggered.connect(self.tex_con_le.undo)
                    self.book_table_view.book_main_window.actionRedo.triggered.connect(self.tex_con_le.redo)
                    self.book_table_view.book_main_window.actionCut.triggered.connect(self.tex_con_le.cut)
                    self.book_table_view.book_main_window.actionCopy.triggered.connect(self.tex_con_le.copy)
                    self.book_table_view.book_main_window.actionPaste.triggered.connect(self.tex_con_le.paste)
                    self.book_table_view.book_main_window.actionDelete.triggered.connect(self.tex_con_le.backspace)
                    self.book_table_view.book_main_window.actionSelectAll.triggered.connect(self.tex_con_le.selectAll)

                    self.tex_con_cb.setLineEdit(self.tex_con_le)
                    self.tex_con_cm = QtWidgets.QCompleter(self)
                    self.tex_con_sl = QtCore.QStringListModel(self)
                    self.tex_con_cm.setModel(self.tex_fact_sl)
                    self.tex_con_cm.setCompletionRole(QtCore.Qt.EditRole)
                    self.tex_con_sl.setStringList(sorted(list(self.tex_fact_contexts)))
                    self.tex_con_cb.setCompleter(self.tex_con_cm)
                except:
                    return self.tex_con_cb
                return self.tex_con_cb

        else:
            model_logger.error("{0}:BookTableViewDelegate:createEditor(): Invalid book_table_view.objectName()".format(str(datetime.datetime.now())))

    def setEditorData(self, editor, index):
        if self.book_table_view.objectName() == "numericalTableView":
            if index.column() == 0:
                super().setEditorData(editor, index)
            elif index.column() == 1:
                current_value = str(index.data(QtCore.Qt.EditRole))
                current_index = self.num_entity_cb.findText(current_value)
                self.num_entity_cb.setCurrentIndex(current_index)
            elif index.column() == 2:
                current_value = str(index.data(QtCore.Qt.EditRole))
                current_index = self.num_filing_cb.findText(current_value)
                self.num_filing_cb.setCurrentIndex(current_index)
            elif index.column() == 3:
                current_value = str(index.data(QtCore.Qt.EditRole))
                current_index = self.num_fact_cb.findText(current_value)
                self.num_fact_cb.setCurrentIndex(current_index)
            elif index.column() == 4:
                current_value = str(index.data(QtCore.Qt.EditRole))
                current_index = self.num_con_cb.findText(current_value)
                self.num_con_cb.setCurrentIndex(current_index)
        elif self.book_table_view.objectName() == "textualTableView":
            if index.column() == 0:
                super().setEditorData(editor, index)
            elif index.column() == 1:
                current_value = str(index.data(QtCore.Qt.EditRole))
                current_index = self.tex_entity_cb.findText(current_value)
                self.tex_entity_cb.setCurrentIndex(current_index)
            elif index.column() == 2:
                current_value = str(index.data(QtCore.Qt.EditRole))
                current_index = self.tex_filing_cb.findText(current_value)
                self.tex_filing_cb.setCurrentIndex(current_index)
            elif index.column() == 3:
                current_value = str(index.data(QtCore.Qt.EditRole))
                current_index = self.tex_fact_cb.findText(current_value)
                self.tex_fact_cb.setCurrentIndex(current_index)
            elif index.column() == 4:
                current_value = str(index.data(QtCore.Qt.EditRole))
                current_index = self.tex_con_cb.findText(current_value)
                self.tex_con_cb.setCurrentIndex(current_index)

            return
        else:
            model_logger.error("{0}:BookTableViewDelegate:createEditor(): Invalid book_table_view.objectName()".format(str(datetime.datetime.now())))

    def setModelData(self, editor, model, index):
        if self.book_table_view.objectName() == "numericalTableView":
            if index.column() == 0:
                model.setData(index, editor.isChecked(), QtCore.Qt.EditRole)
            elif index.column() in (1, 2, 3, 4):
                model.setData(index, editor.currentText(), QtCore.Qt.EditRole)
        elif self.book_table_view.objectName() == "textualTableView":
            if index.column() == 0:
                model.setData(index, editor.isChecked(), QtCore.Qt.EditRole)
            elif index.column() in (1, 2, 3, 4):
                model.setData(index, editor.currentText(), QtCore.Qt.EditRole)
        else:
            model_logger.error("{0}:BookTableViewDelegate:createEditor(): Invalid book_table_view.objectName()".format(str(datetime.datetime.now())))

        return

    def updateEditorGeometry(self, editor, option, index):
        QtWidgets.QStyledItemDelegate.updateEditorGeometry(self, editor, option, index)

        return
