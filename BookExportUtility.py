"""
:mod: 'BookExportUtility'
~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:module:: BookExportUtility
    :copyright: Copyright BitWorks LLC, All rights reserved.
    :license: MIT
    :synopsis: Exporter class for exporting data from XBRLStudio to external file types
    :description: Contains the following classes:

        BookExporter - primary class for exporting from XBRLStudio to external file types; currently supports PDF and CSV exports
"""

try:
    import copy, csv, sys, os, datetime, logging
    export_utility_logger = logging.getLogger()
    from PyQt5 import QtWidgets
    from PyQt5.QtCore import (QFile, QIODevice)
    from PyQt5.QtChart import QChartView
except Exception as err:
    export_utility_logger.error("{0}:BookExportUtility import error:{1}".format(str(datetime.datetime.now()), str(err)))

class BookExporter():
    """
    BookExporter
    ~~~~~~~~~~~~
    Custom class providing access to export libraries (pdf and csv)

    Functions
    ~~~~~~~~~
    buildHtmlTexGraphic(self, current_top_tab, current_tex_graphic, out_file, current_tab_index, tmp_files) - builds textual graphic html string
    exportHtml(self, mode) - exports textual graphics (from single or total tabs) to a html file
    exportCsv(self, mode) - exports numerical tables (from single or total tabs) to a csv file

    Attributes
    ~~~~~~~~~~
    book_main_window - (BookView.BookMainWindow type); access to main window and related functionality
    """

    def __init__(self, book_main_window):
        export_utility_logger.info("{0}:Initializing BookExporter".format(str(datetime.datetime.now())))
        self.book_main_window = book_main_window
        self.tmp_dir = self.book_main_window.directories["Global_tmp_dir"]

    def buildHtmlTexGraphic(self, current_top_tab, current_tex_graphic):
        try:
            current_tex_html = ""
            current_tex_html += "<p>{0} - Textual Graphic</p><br>".format(current_top_tab.objectName())
            current_tex_html += current_tex_graphic.html

            return current_tex_html
        except Exception as err:
            export_utility_logger.error("{0}:BookExporter.buildHtmlTexGraphic():{1}".format(str(datetime.datetime.now()), str(err)))

    def exportHtml(self, mode):
        try:
            #Get out_file path, ensure valid filename for a html
            out_file = QtWidgets.QFileDialog.getSaveFileName(caption = "HTML Export",
                                                            directory = "C:\\",
                                                            filter = "HTML (*.html)",
                                                            options = QtWidgets.QFileDialog.DontConfirmOverwrite)[0]
            if out_file != "":
                if out_file.split(os.sep)[-1] != "":
                    file_name = out_file.split(os.sep)[-1]
                if "." in file_name:
                    if file_name[0] == ".":
                        hidden_file_choice = QtWidgets.QMessageBox.warning(self.book_main_window,
                                                       "HTML file name confirmation",
                                                       "Are you sure you want to create HTML file {0}".format(out_file.split(os.sep)[-1]),
                                                       QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                                                       QtWidgets.QMessageBox.Cancel)
                        if hidden_file_choice == QtWidgets.QMessageBox.Cancel:
                            return
                    if file_name.split(".")[-1] != "html":
                        file_name += ".html"
                        out_file += ".html"
                elif "." not in file_name:
                    file_name += ".html"
                    out_file += ".html"
            if os.path.isfile(out_file):
                overwrite_choice = QtWidgets.QMessageBox.warning(self.book_main_window,
                                               "Overwrite file?",
                                               "Are you sure you want to overwrite {0}?".format(out_file.split(os.sep)[-1]),
                                               QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                                               QtWidgets.QMessageBox.Cancel)
                if overwrite_choice == QtWidgets.QMessageBox.Ok:
                    os.remove(out_file)
                else:
                    return
            if out_file != "":
                if mode == "all_tabs":
                    tab_index = 0
                    current_html_tex_graphic = ""
                    while tab_index < self.book_main_window.mainTabWidget.count() - 1:
                        current_top_tab = self.book_main_window.mainTabWidget.widget(tab_index)
                        current_tex_graphic = current_top_tab.findChild(QtWidgets.QTextEdit, "textualGraphic")
                        current_html_tex_graphic += self.buildHtmlTexGraphic(current_top_tab, current_tex_graphic)
                        tab_index += 1

                elif mode == "single_tab":
                    tab_index = self.book_main_window.mainTabWidget.currentIndex()
                    current_html_tex_graphic = ""
                    current_top_tab = self.book_main_window.mainTabWidget.widget(tab_index)
                    current_tex_graphic = current_top_tab.findChild(QtWidgets.QTextEdit, "textualGraphic")
                    current_html_tex_graphic += self.buildHtmlTexGraphic(current_top_tab, current_tex_graphic)

                html_file = open(out_file, "w")
                html_file.write(current_html_tex_graphic)
                html_file.close()

            return
        except Exception as err:
            export_utility_logger.error("{0}:BookExporter.exportHtml():{1}".format(str(datetime.datetime.now()), str(err)))

    def exportCsv(self, mode):
        try:
            #Get out_file path, ensure valid filename for a csv
            out_file = QtWidgets.QFileDialog.getSaveFileName(caption = "CSV Export",
                                  directory = "C:\\",
                                  filter = "CSV (*.csv)",
                                  options = QtWidgets.QFileDialog.DontConfirmOverwrite)[0]
            if out_file != "":
                if out_file.split(os.sep)[-1] != "":
                    file_name = out_file.split(os.sep)[-1]
                if "." in file_name:
                    if file_name[0] == ".":
                        hidden_file_choice = QtWidgets.QMessageBox.warning(self.book_main_window,
                                                       "CSV file name confirmation",
                                                       "Are you sure you want to create CSV file {0}".format(out_file.split(os.sep)[-1]),
                                                       QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                                                       QtWidgets.QMessageBox.Cancel)
                        if hidden_file_choice == QtWidgets.QMessageBox.Cancel:
                            return
                    if file_name.split(".")[-1] != "csv":
                        file_name += ".csv"
                        out_file += ".csv"
                elif "." not in file_name:
                    file_name += ".csv"
                    out_file += ".csv"
            if os.path.isfile(out_file):
                overwrite_choice = QtWidgets.QMessageBox.warning(self.book_main_window,
                                               "Overwrite file?",
                                               "Are you sure you want to overwrite {0}?".format(out_file.split(os.sep)[-1]),
                                               QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                                               QtWidgets.QMessageBox.Cancel)
                if overwrite_choice == QtWidgets.QMessageBox.Ok:
                    os.remove(out_file)
                else:
                    return
            if out_file != "":

                if mode == "all_tabs":
                    csv_file_handler = open(out_file, "w", newline = "")
                    tab_index = 0
                    while tab_index < self.book_main_window.mainTabWidget.count() - 1:
                        current_top_tab = self.book_main_window.mainTabWidget.widget(tab_index)
                        current_num_table_view = current_top_tab.findChild(QtWidgets.QTableView, "numericalTableView")
                        current_num_table_title_text = current_top_tab.objectName() + " - Numerical Table"
                        current_tex_table_title_text = current_top_tab.objectName() + " - Textual Table"
                        csv_file_writer = csv.writer(csv_file_handler)
                        current_num_table_items = copy.deepcopy(current_num_table_view.model().items)
                        #Remove raw periods
                        for item in current_num_table_items:
                            del(item[1])
                        #Remove empty rows
                        empty_rows_gone = False
                        while not empty_rows_gone:
                            for index, item in enumerate(current_num_table_items):
                                if item[0] is None:
                                    empty_rows_gone = False
                                    current_num_table_items.pop(index)
                            current_rows = []
                            if len(current_num_table_items) > 0:
                                for item in current_num_table_items:
                                    current_rows.append(item[0])
                                    if None in current_rows:
                                        empty_rows_gone = False
                                    else:
                                        empty_rows_gone = True
                            else:
                                empty_rows_gone = True
                        empty_rows_gone = False
                        #Insert index
                        for index, item in enumerate(current_num_table_items):
                            item.insert(0, index + 1)
                        #Insert header
                        current_num_table_items.insert(0, ["#", "CIK", "View", "Entity", "Filing", "Fact", "Context", "Value", "Unit", "Dec"])
                        #Insert tab header
                        current_num_table_items.insert(0, [current_num_table_title_text, "", "", "", "", "", "", "", "", ""])
                        #Remove commas
                        for item in current_num_table_items:
                            for sub_item in item:
                                sub_item = str(sub_item).replace(",", "")
                        #Write rows
                        for item in current_num_table_items:
                            csv_file_writer.writerow(item)

                        tab_index += 1

                elif mode == "single_tab":
                    csv_file_handler = open(out_file, "w", newline = "")
                    tab_index = self.book_main_window.mainTabWidget.currentIndex()
                    current_top_tab = self.book_main_window.mainTabWidget.widget(tab_index)
                    current_num_table_view = current_top_tab.findChild(QtWidgets.QTableView, "numericalTableView")
                    current_num_table_title_text = current_top_tab.objectName() + " - Numerical Table"
                    csv_file_writer = csv.writer(csv_file_handler)
                    current_num_table_items = copy.deepcopy(current_num_table_view.model().items)
                    #Remove raw periods
                    for item in current_num_table_items:
                        del(item[1])
                    #Remove empty rows
                    empty_rows_gone = False
                    while not empty_rows_gone:
                        for index, item in enumerate(current_num_table_items):
                            if item[0] is None:
                                empty_rows_gone = False
                                current_num_table_items.pop(index)
                        current_rows = []
                        if len(current_num_table_items) > 0:
                            for item in current_num_table_items:
                                current_rows.append(item[0])
                                if None in current_rows:
                                    empty_rows_gone = False
                                else:
                                    empty_rows_gone = True
                        else:
                            empty_rows_gone = True
                    empty_rows_gone = False
                    #Insert index
                    for index, item in enumerate(current_num_table_items):
                        item.insert(0, index + 1)
                    #Insert header
                    current_num_table_items.insert(0, ["#", "CIK", "View", "Entity", "Filing", "Fact", "Context", "Value", "Unit", "Dec"])
                    #Insert tab header
                    current_num_table_items.insert(0, [current_num_table_title_text, "", "", "", "", "", "", "", "", ""])
                    #Remove commas
                    for item in current_num_table_items:
                        for sub_item in item:
                            sub_item = str(sub_item).replace(",", "")
                    #Write rows
                    for item in current_num_table_items:
                        csv_file_writer.writerow(item)

                csv_file_handler.close()

            return
        except Exception as err:
            export_utility_logger.error("{0}:BookExporter.exportCsv():{1}".format(str(datetime.datetime.now()), str(err)))
