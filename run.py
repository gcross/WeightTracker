from collections import namedtuple
import os
from os import path
import sqlite3
import sys

from PyQt5 import QtCore as QC
from PyQt5 import QtGui as QG
from PyQt5 import QtWidgets as QW

class EntryWidget(QW.QWidget):
    def __init__(self,filename,database):
        self.filename = filename
        self.database = database

        QW.QWidget.__init__(self)
        main_box = QW.QVBoxLayout()
        self.setLayout(main_box)
        
        weight_panel = QW.QWidget()
        main_box.addWidget(weight_panel)
        weight_panel_box = QW.QHBoxLayout()
        weight_panel.setLayout(weight_panel_box)
        weight_panel_box.addWidget(QW.QLabel("Weight:"))
        self.weight_field = QW.QLineEdit()
        self.weight_field.setFixedWidth(60)
        weight_panel_box.addSpacing(0)
        weight_panel_box.addWidget(self.weight_field)
        weight_panel_box.addSpacing(20)
        weight_panel_box.addStretch()
        save_and_clear_button = QW.QPushButton("Save and Clear")
        save_and_clear_button.setDefault(True)
        save_and_clear_button.clicked.connect(self.saveAndClear)
        weight_panel_box.addWidget(save_and_clear_button)

        date_time_panel = QW.QWidget()
        main_box.addWidget(date_time_panel)
        date_time_box = QW.QHBoxLayout()
        date_time_panel.setLayout(date_time_box)
        date_time_box.addWidget(QW.QLabel("Date and Time:"))
        self.date_time_field = QW.QDateTimeEdit(QC.QDateTime.currentDateTime())
        self.date_time_field.setFixedWidth(150)
        date_time_box.addWidget(self.date_time_field)

    def saveAndClear(self):
        timestamp = self.date_time_field.dateTime().toTime_t()
        try:
            weight = float(self.weight_field.text());
        except ValueError:
            QW.QMessageBox.information(self,"Error","The given weight value, \"" + self.weight_field.text() + "\", is not a valid number.")
            return
        cursor = self.database.cursor()
        cursor.execute("select null from weights where timestamp = ?",(timestamp,))
        if cursor.fetchone() is not None:
            answer = QW.QMessageBox.question(self,"Warning","There is already a weight for the given date.  Would you like to overwrite it?")
            if answer == QW.QMessageBox.No:
                cursor.close()
                return
            cursor.execute("update weights set weight = ? where timestamp = ?",(weight,timestamp))
        else:
            cursor.execute("insert into weights (timestamp,weight) values (?,?)",(timestamp,weight))
        self.database.commit()
        cursor.close()
        self.weight_field.setText("")

def doNew():
    openAndAddTab(QW.QFileDialog.getSaveFileName(main,"New File",documents_directory,"Databases (*.db)")[0])

def doOpen():
    openAndAddTab(QW.QFileDialog.getOpenFileName(main,"Open File",documents_directory,"Databases (*.db)")[0])

def doClose():
    global entry_widgets
    entry_panel = entry_widgets.currentWidget()
    entry_panel.database.close()
    entry_widgets.removeTab(entry_widgets.currentIndex())

def doQuit():
    app.exit()

def openAndAddTab(filename):
    global database, entry_widgets
    database = sqlite3.connect(filename)
    database.execute("create table if not exists weights (timestamp integer, weight real)")
    database.commit()
    entry_widgets.addTab(EntryWidget(filename,database),path.splitext(path.split(filename)[1])[0])

def main():
    global app, documents_directory, entry_widgets, main, path_to_opened
    app = QW.QApplication(sys.argv)
    app.setApplicationName("WeightTracker")
    app.setApplicationVersion("1.0")

    documents_directory = QC.QStandardPaths.writableLocation(QC.QStandardPaths.DocumentsLocation)

    main = QW.QMainWindow()
    entry_widgets = QW.QTabWidget()
    main.setCentralWidget(entry_widgets)

    directory_of_opened = QC.QStandardPaths.writableLocation(QC.QStandardPaths.DataLocation)
    if not path.exists(directory_of_opened):
        os.makedirs(directory_of_opened)
    path_to_opened = path.join(directory_of_opened,"opened.lst")

    if path.exists(path_to_opened):
        with open(opened_path,"rt") as f:
            filenames_to_open = list(f)
        for filename in filenames_to_open:
            connectAndAddTab(filename)

    menu_bar = QW.QMenuBar(main)

    file_menu = QW.QMenu("File")
    for name in ["New","Open","Close","Quit"]:
        if name:
            action = QW.QAction(name,main)
            action.setShortcut(QG.QKeySequence(getattr(QG.QKeySequence,name)))
            action.triggered.connect(globals()["do" + name])
            file_menu.addAction(action)
        else:
            file_menu.addSeparator()
    menu_bar.addMenu(file_menu)

    main.show()
    app.exec_()

if __name__ == "__main__":
    main()
