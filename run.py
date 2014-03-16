import os
from os import path
import sqlite3
import sys

from PyQt5 import QtCore
for name in ["DateTime","StandardPaths"]:
    globals()[name] = getattr(QtCore,"Q" + name)

from PyQt5 import QtGui
for name in ["KeySequence"]:
    globals()[name] = getattr(QtGui,"Q" + name)

from PyQt5 import QtWidgets
for name in [
    "Action",
    "Application",
    "ComboBox",
    "DateTimeEdit",
    "FileDialog",
    "GroupBox",
    "HBoxLayout",
    "Label",
    "LineEdit",
    "MainWindow",
    "Menu",
    "MenuBar",
    "MessageBox",
    "PushButton",
    "RadioButton",
    "TabWidget",
    "VBoxLayout",
    "Widget",
  ]:
    globals()[name] = getattr(QtWidgets,"Q" + name)

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

class EntryWidget(Widget):
    def __init__(self,filename,database):
        self.filename = filename
        self.database = database
        self.windows = []

        Widget.__init__(self)
        main_box = VBoxLayout()
        self.setLayout(main_box)

        weight_panel = Widget()
        main_box.addWidget(weight_panel)
        weight_panel_box = HBoxLayout()
        weight_panel.setLayout(weight_panel_box)
        weight_panel_box.addWidget(Label("Weight:"))
        self.weight_field = LineEdit()
        self.weight_field.returnPressed.connect(self.saveAndClear)
        self.weight_field.setFixedWidth(60)
        weight_panel_box.addSpacing(0)
        weight_panel_box.addWidget(self.weight_field)
        weight_panel_box.addSpacing(20)
        weight_panel_box.addStretch()
        save_and_clear_button = PushButton("Save and Clear")
        save_and_clear_button.clicked.connect(self.saveAndClear)
        weight_panel_box.addWidget(save_and_clear_button)

        date_time_panel = Widget()
        main_box.addWidget(date_time_panel)
        date_time_box = HBoxLayout()
        date_time_panel.setLayout(date_time_box)
        date_time_box.addWidget(Label("Date and Time:"))
        self.date_time_field = DateTimeEdit(DateTime.currentDateTime())
        self.date_time_field.setFixedWidth(150)
        date_time_box.addWidget(self.date_time_field)
        push_button = PushButton("Now")
        push_button.clicked.connect(self.setToNow)
        date_time_box.addWidget(push_button)

    def saveAndClear(self):
        timestamp = self.date_time_field.dateTime().toTime_t()
        try:
            weight = float(self.weight_field.text());
        except ValueError:
            MessageBox.information(self,"Error","The given weight value, \"" + self.weight_field.text() + "\", is not a valid number.")
            return
        with withinTransactionFor(self.database) as cursor:
            cursor = self.database.cursor()
            cursor.execute("select null from weights where timestamp = ?",(timestamp,))
            if cursor.fetchone() is not None:
                answer = MessageBox.question(self,"Warning","There is already a weight for the given date.  Would you like to overwrite it?")
                if answer == MessageBox.No:
                    return
                cursor.execute("update weights set weight = ? where timestamp = ?",(weight,timestamp))
            else:
                cursor.execute("insert into weights (timestamp,weight) values (?,?)",(timestamp,weight))
        self.weight_field.setText("")

    def setToNow(self):
        self.date_time_field.setDateTime(DateTime.currentDateTime())

class DateRangeWidget(Widget):
    def __init__(self):
        Widget.__init__(self)
        box = HBoxLayout()
        self.setLayout(box)

        entry_controls = GroupBox("Date Range")
        box.addWidget(entry_controls)
        entry_controls_box = VBoxLayout()
        entry_controls.setLayout(entry_controls_box)

        since_panel = Widget()
        entry_controls_box.addWidget(since_panel)
        since_panel_box = HBoxLayout()
        since_panel.setLayout(since_panel_box)
        self.since_radio = RadioButton(entry_controls)
        since_panel_box.addWidget(self.since_radio)
        since_panel_box.addWidget(Label("Since"))
        self.duration_field = LineEdit()
        since_panel_box.addWidget(self.duration_field)
        self.units_field = ComboBox()
        since_panel_box.addWidget(self.units_field)
        self.units_field.addItem("days")
        self.units_field.addItem("months")
        self.units_field.addItem("years")
        since_panel_box.addWidget(Label("ago"))

        range_panel = Widget()
        entry_controls_box.addWidget(range_panel)
        range_panel_box = HBoxLayout()
        self.range_radio = RadioButton(entry_controls)
        range_panel_box.addWidget(self.range_radio)
        range_panel_box.addWidget(Label("From"))
        self.from_field = DateTimeEdit()
        range_panel_box.addWidget(self.from_field)
        range_panel_box.addWidget(Label("to"))
        self.to_field = DateTimeEdit()
        range_panel_box.addWidget(self.to_field)

        apply_button = PushButton("Apply")
        box.addWidget(apply_button)

class Cursor(sqlite3.Cursor):
    def __init__(self,*args, **keywords):
        sqlite3.Cursor(self)
    def __enter__(self):
        pass
    def __exit__(self):
        self.close()

class WeightTrackerApplication(Application):
    def __init__(self,argv):
        self.windows = []
        
        Application.__init__(self,argv)
        self.setApplicationName("WeightTracker")
        self.setApplicationVersion("1.0")

        self.documents_directory = StandardPaths.writableLocation(StandardPaths.DocumentsLocation)

        self.main = MainWindow()
        main_panel = Widget()
        self.main.setCentralWidget(main_panel)
        main_panel_box = VBoxLayout()
        main_panel.setLayout(main_panel_box)

        self.entry_widgets = TabWidget()
        main_panel_box.addWidget(self.entry_widgets)

        self.none_opened_label = Label("Use the File menu to open a weight database.")
        self.none_opened_label.setVisible(False)
        main_panel_box.addWidget(self.none_opened_label)

        view_buttons_panel = Widget()
        main_panel_box.addWidget(view_buttons_panel)
        view_buttons_panel_box = HBoxLayout()
        view_buttons_panel.setLayout(view_buttons_panel_box)
        self.list_view_button = PushButton("View/Edit as List")
        self.list_view_button.clicked.connect(self.doList)
        view_buttons_panel_box.addWidget(self.list_view_button)
        self.graph_view_button = PushButton("View as Graph")
        self.graph_view_button.clicked.connect(self.doGraph)
        view_buttons_panel_box.addWidget(self.graph_view_button)

    def exec_(self):
        menu_bar = MenuBar(self.main)

        file_menu = Menu("File")
        for name in ["New","Open","Close","Quit"]:
            if name:
                action = Action(name,self.main)
                action.setShortcut(KeySequence(getattr(KeySequence,name)))
                action.triggered.connect(getattr(self,name))
                file_menu.addAction(action)
            else:
                file_menu.addSeparator()
        menu_bar.addMenu(file_menu)

        directory_of_opened = StandardPaths.writableLocation(StandardPaths.DataLocation)
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
        Application.exec_()

    def New(self):
        self.openAndAddTab(FileDialog.getSaveFileName(self.main,"New File",self.documents_directory,"Databases (*.db)")[0])

    def Open(self):
        self.openAndAddTab(FileDialog.getOpenFileName(self.main,"Open File",self.documents_directory,"Databases (*.db)")[0])

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
                MessageBox.information(self.main,"Error","The file \"" + filename + "\" has already been opened.")
                return
        database = sqlite3.connect(filename)
        database.execute("create table if not exists weights (timestamp integer, weight real)")
        database.commit()
        self.entry_widgets.addTab(EntryWidget(filename,database),path.splitext(path.split(filename)[1])[0])
        self.saveTabs()

    def doList(self):
        list_frame = MainWindow()
        list_frame_panel = Widget()
        list_frame.setCentralWidget(list_frame_panel)
        
        list_frame_box = VBoxLayout()
        list_frame_panel.setLayout(list_frame_box)
        
        date_range_widget = DateRangeWidget()
        list_frame_box.addWidget(date_range_widget)

        list_frame.show()
        
        self.windows.append(list_frame)

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
    app = WeightTrackerApplication(sys.argv)
    app.exec_()
