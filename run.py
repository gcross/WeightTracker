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

class Application(QW.QApplication):
    def __init__(self,argv):
        QW.QApplication.__init__(self,argv)
        self.setApplicationName("WeightTracker")
        self.setApplicationVersion("1.0")

        self.documents_directory = QC.QStandardPaths.writableLocation(QC.QStandardPaths.DocumentsLocation)

        self.main = QW.QMainWindow()
        main_panel = QW.QWidget()
        self.main.setCentralWidget(main_panel)
        main_panel_box = QW.QVBoxLayout()
        main_panel.setLayout(main_panel_box)

        self.entry_widgets = QW.QTabWidget()
        main_panel_box.addWidget(self.entry_widgets)

        self.none_opened_label = QW.QLabel("Use the File menu to open a weight database.")
        self.none_opened_label.setVisible(False)
        main_panel_box.addWidget(self.none_opened_label)

        view_buttons_panel = QW.QWidget()
        main_panel_box.addWidget(view_buttons_panel)
        view_buttons_panel_box = QW.QHBoxLayout()
        view_buttons_panel.setLayout(view_buttons_panel_box)
        self.list_view_button = QW.QPushButton("View/Edit as List")
        self.list_view_button.clicked.connect(self.doList)
        view_buttons_panel_box.addWidget(self.list_view_button)
        self.graph_view_button = QW.QPushButton("View as Graph")
        self.graph_view_button.clicked.connect(self.doGraph)
        view_buttons_panel_box.addWidget(self.graph_view_button)

    def exec_(self):
        menu_bar = QW.QMenuBar(self.main)

        file_menu = QW.QMenu("File")
        for name in ["New","Open","Close","Quit"]:
            if name:
                action = QW.QAction(name,self.main)
                action.setShortcut(QG.QKeySequence(getattr(QG.QKeySequence,name)))
                action.triggered.connect(getattr(self,name))
                file_menu.addAction(action)
            else:
                file_menu.addSeparator()
        menu_bar.addMenu(file_menu)

        directory_of_opened = QC.QStandardPaths.writableLocation(QC.QStandardPaths.DataLocation)
        if not path.exists(directory_of_opened):
            os.makedirs(directory_of_opened)
        self.path_to_opened = path.join(directory_of_opened,"opened.lst")

        if path.exists(self.path_to_opened):
            with open(self.path_to_opened,"rt") as f:
                filenames_to_open = list(f)
            for filename in filenames_to_open:
                self.openAndAddTab(filename)

        self.updateVisibility()

        self.main.show()
        QW.QApplication.exec_()

    def New(self):
        self.openAndAddTab(QW.QFileDialog.getSaveFileName(self.main,"New File",self.documents_directory,"Databases (*.db)")[0])

    def Open(self):
        self.openAndAddTab(QW.QFileDialog.getOpenFileName(self.main,"Open File",self.documents_directory,"Databases (*.db)")[0])

    def Close(self):
        entry_panel = self.entry_widgets.currentWidget()
        entry_panel.database.close()
        self.entry_widgets.removeTab(self.entry_widgets.currentIndex())
        self.saveTabs()

    def Quit(self):
        self.exit()

    def openAndAddTab(self,filename):
        filename = filename.strip()
        if len(filename) == 0:
            return
        for i in range(self.entry_widgets.count()):
            if(self.entry_widgets.widget(i).filename == filename):
                QW.QMessageBox.information(self.main,"Error","The file \"" + filename + "\" has already been opened.")
                return
        database = sqlite3.connect(filename)
        database.execute("create table if not exists weights (timestamp integer, weight real)")
        database.commit()
        self.entry_widgets.addTab(EntryWidget(filename,database),path.splitext(path.split(filename)[1])[0])
        self.saveTabs()

    def doList(self):
        pass

    def doGraph(self):
        pass

    def saveTabs(self):
        number_of_widgets = self.entry_widgets.count()
        with open(self.path_to_opened + ".tmp","wt") as f:
            filenames = [self.entry_widgets.widget(i).filename.strip() for i in range(number_of_widgets)]
            f.write('\n'.join(filenames))
        os.rename(self.path_to_opened + ".tmp",self.path_to_opened)
        self.updateVisibility()

    def updateVisibility(self):
        tab_present = self.entry_widgets.count() > 0
        self.none_opened_label.setVisible(not tab_present)
        self.list_view_button.setEnabled(tab_present)
        self.graph_view_button.setEnabled(tab_present)

if __name__ == "__main__":
    Application(sys.argv).exec_()
