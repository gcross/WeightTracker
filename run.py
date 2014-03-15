from collections import namedtuple
import os
from os import path
import sqlite3
import sys

from PyQt5 import QtCore as QC
from PyQt5 import QtGui as QG
from PyQt5 import QtWidgets as QW

def withinTransactionFor(database):
    class Transaction(sqlite3.Cursor):
        def __init__(self,*args,**keywords):
            sqlite3.Cursor.__init__(self,*args,**keywords)
        def __enter__(self):
            pass
        def __exit__(self,type,value,traceback):
            self.close()
            database.commit()
            return type
    return database.cursor(Transaction)

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
        self.weight_field.returnPressed.connect(self.saveAndClear)
        self.weight_field.setFixedWidth(60)
        weight_panel_box.addSpacing(0)
        weight_panel_box.addWidget(self.weight_field)
        weight_panel_box.addSpacing(20)
        weight_panel_box.addStretch()
        save_and_clear_button = QW.QPushButton("Save and Clear")
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
        push_button = QW.QPushButton("Now")
        push_button.clicked.connect(self.setToNow)
        date_time_box.addWidget(push_button)

    def saveAndClear(self):
        timestamp = self.date_time_field.dateTime().toTime_t()
        try:
            weight = float(self.weight_field.text());
        except ValueError:
            QW.QMessageBox.information(self,"Error","The given weight value, \"" + self.weight_field.text() + "\", is not a valid number.")
            return
        with withinTransactionFor(self.database) as cursor:
            cursor = self.database.cursor()
            cursor.execute("select null from weights where timestamp = ?",(timestamp,))
            if cursor.fetchone() is not None:
                answer = QW.QMessageBox.question(self,"Warning","There is already a weight for the given date.  Would you like to overwrite it?")
                if answer == QW.QMessageBox.No:
                    return
                cursor.execute("update weights set weight = ? where timestamp = ?",(weight,timestamp))
            else:
                cursor.execute("insert into weights (timestamp,weight) values (?,?)",(timestamp,weight))
        self.weight_field.setText("")

    def setToNow(self):
        self.date_time_field.setDateTime(QC.QDateTime.currentDateTime())

class Cursor(sqlite3.Cursor):
    def __init__(self,*args, **keywords):
        sqlite3.Cursor(self)
    def __enter__(self):
        pass
    def __exit__(self):
        self.close()

def doNew():
    openAndAddTab(QW.QFileDialog.getSaveFileName(main,"New File",documents_directory,"Databases (*.db)")[0])

def doOpen():
    openAndAddTab(QW.QFileDialog.getOpenFileName(main,"Open File",documents_directory,"Databases (*.db)")[0])

def doClose():
    global entry_widgets
    entry_panel = entry_widgets.currentWidget()
    entry_panel.database.close()
    entry_widgets.removeTab(entry_widgets.currentIndex())
    saveTabs()

def doQuit():
    app.exit()

def openAndAddTab(filename):
    filename = filename.strip()
    if len(filename) == 0:
        return
    global database, entry_widgets, main
    for i in range(entry_widgets.count()):
        if(entry_widgets.widget(i).filename == filename):
            QW.QMessageBox.information(main,"Error","The file \"" + filename + "\" has already been opened.")
            return
    database = sqlite3.connect(filename)
    database.execute("create table if not exists weights (timestamp integer, weight real)")
    database.commit()
    entry_widgets.addTab(EntryWidget(filename,database),path.splitext(path.split(filename)[1])[0])
    saveTabs()

def saveTabs():
    global entry_widgets, none_opened_label, path_to_opened
    number_of_widgets = entry_widgets.count()
    with open(path_to_opened + ".tmp","wt") as f:
        filenames = [entry_widgets.widget(i).filename.strip() for i in range(number_of_widgets)]
        f.write('\n'.join(filenames))
    os.rename(path_to_opened + ".tmp",path_to_opened)
    none_opened_label.setVisible(number_of_widgets == 0)

def main():
    global app, documents_directory, entry_widgets, main, none_opened_label, path_to_opened
    app = QW.QApplication(sys.argv)
    app.setApplicationName("WeightTracker")
    app.setApplicationVersion("1.0")

    documents_directory = QC.QStandardPaths.writableLocation(QC.QStandardPaths.DocumentsLocation)

    main = QW.QMainWindow()
    main_panel = QW.QWidget()
    main.setCentralWidget(main_panel)
    main_panel_box = QW.QVBoxLayout()
    main_panel.setLayout(main_panel_box)

    entry_widgets = QW.QTabWidget()
    main_panel_box.addWidget(entry_widgets)

    none_opened_label = QW.QLabel("Use the File menu to open a weight database.")
    none_opened_label.setVisible(False)
    main_panel_box.addWidget(none_opened_label)

    directory_of_opened = QC.QStandardPaths.writableLocation(QC.QStandardPaths.DataLocation)
    if not path.exists(directory_of_opened):
        os.makedirs(directory_of_opened)
    path_to_opened = path.join(directory_of_opened,"opened.lst")

    if path.exists(path_to_opened):
        with open(path_to_opened,"rt") as f:
            filenames_to_open = list(f)
        for filename in filenames_to_open:
            openAndAddTab(filename)

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

    none_opened_label.setVisible(entry_widgets.count() == 0)

    main.show()
    app.exec_()

if __name__ == "__main__":
    main()
