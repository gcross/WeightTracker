#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTabWidget>

class MainWindow : public QMainWindow
{
    Q_OBJECT

    QWidget *contents;
    QTabWidget *entry_widgets;

    void doClose();
    void doNew();
    void doOpen();
    void doQuit();

    void openAndAddTab(const QString&filename);

    void viewAsGraph();
    void viewAsList();

public:
    explicit MainWindow(QWidget *parent = 0);
};

#endif // MAINWINDOW_H
