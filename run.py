import sys

from PyQt5 import QtWidgets as QW

class EntryWidget(QW.QWidget):
    def __init__(self):
        QW.QWidget.__init__(self)
        main_box = QW.QVBoxLayout()
        self.setLayout(main_box)

        date_time_field = QW.QDateTimeEdit()
        main_box.addWidget(date_time_field)
        
        weight_panel = QW.QWidget()
        main_box.addWidget(weight_panel)
        weight_panel_box = QW.QHBoxLayout()
        weight_panel.setLayout(weight_panel_box)
        weight_panel_box.addWidget(QW.QLabel("Weight: "))
        self.weight_field = QW.QLineEdit()
        weight_panel_box.addWidget(self.weight_field)
        save_and_clear_button = QW.QPushButton("Save and Clear")
        weight_panel_box.addWidget(save_and_clear_button)

if __name__ == "__main__":
    app = QW.QApplication(sys.argv)
    gui = QW.QMainWindow()
    gui.setCentralWidget(EntryWidget())
    gui.show()
    app.exec_()
