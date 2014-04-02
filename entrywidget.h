#ifndef ENTRYWIDGET_H
#define ENTRYWIDGET_H

#include <QDateTime>
#include <QDateTimeEdit>
#include <QLineEdit>
#include <QString>
#include <QWidget>

#include "sqlite3.h"

class EntryWidget : public QWidget
{
    Q_OBJECT

    QLineEdit *weight_field;
    QDateTimeEdit *date_time_field;

    sqlite3 *database;

    void setToNow();

public:
    explicit EntryWidget(const QString &filename, QWidget *parent = 0);
    ~EntryWidget();

    const QString filename, name;
};

#endif // ENTRYWIDGET_H
