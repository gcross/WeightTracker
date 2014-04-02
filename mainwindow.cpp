#include "mainwindow.h"

#include "entrywidget.h"

#include <QApplication>
#include <QBoxLayout>
#include <QFileDialog>
#include <QMessageBox>
#include <QMenu>
#include <QMenuBar>
#include <QPushButton>
#include <QStandardPaths>

#include <stdexcept>

#include <sqlite3.h>

static const auto documents_directory = QStandardPaths::writableLocation(QStandardPaths::DocumentsLocation);

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    contents(new QWidget(this)),
    entry_widgets(new QTabWidget(contents))
{
    setCentralWidget(contents);
    auto layout = new QVBoxLayout(contents);
    contents->setLayout(layout);

    layout->addWidget(entry_widgets);

    auto buttons = new QHBoxLayout();
    layout->addLayout(buttons);

    auto list_button = new QPushButton(tr("View as List"),contents);
    QObject::connect(list_button,&QPushButton::clicked,this,&MainWindow::viewAsList);
    buttons->addWidget(list_button);

    auto graph_button = new QPushButton(tr("View as Graph"),contents);
    QObject::connect(graph_button,&QPushButton::clicked,this,&MainWindow::viewAsGraph);
    buttons->addWidget(graph_button);

    setFixedSize(minimumSize());

    auto menu_bar = new QMenuBar(this);

    auto file_menu = new QMenu(tr("File"));
    menu_bar->addMenu(file_menu);

    #define CREATE_FILE_MENU_ACTION(name) \
        { \
            auto action = new QAction(#name,this); \
            action->setShortcut(QKeySequence::name); \
            connect(action,&QAction::triggered,this,&MainWindow::do ## name); \
            file_menu->addAction(action); \
        }

    CREATE_FILE_MENU_ACTION(Close)
    CREATE_FILE_MENU_ACTION(New)
    CREATE_FILE_MENU_ACTION(Open)
    CREATE_FILE_MENU_ACTION(Quit)

    #undef CREATE_FILE_MENU_ACTION
}

void MainWindow::doClose()
{
    if(entry_widgets->count() == 0) doQuit();
    entry_widgets->removeTab(entry_widgets->currentIndex());
}

void MainWindow::doNew()
{
    openAndAddTab(QFileDialog::getSaveFileName(this,tr("Create New Database"),documents_directory,tr("Weight Databases (*.db)")));
}

void MainWindow::doOpen()
{
    openAndAddTab(QFileDialog::getOpenFileName(this,tr("Open Existing Database"),documents_directory,tr("Weight Databases (*.db)")));
}

void MainWindow::doQuit()
{
    qApp->closeAllWindows();
}

void MainWindow::openAndAddTab(const QString &filename)
{
    if(filename.isNull()) return;
    for(int i = 0; i < entry_widgets->count(); ++i)
    {
        if(static_cast<EntryWidget*>(entry_widgets->widget(i))->filename == filename) {
            QString message(tr("The file "));
            message += QString(QChar('='));
            message += filename;
            message += QString(QChar('"'));
            message += tr(" has already been opened");
            QMessageBox::information(this,tr("Error"),message);
            return;
        }
    }

    try {
        auto entry_widget = new EntryWidget(filename,this);
        entry_widgets->addTab(entry_widget,entry_widget->name);
        entry_widgets->setCurrentIndex(entry_widgets->count()-1);
    }
    catch(const std::runtime_error &e)
    {
        QMessageBox::information(this,tr("Error"),e.what());
    }
}

void MainWindow::viewAsGraph()
{
}

void MainWindow::viewAsList()
{
}
