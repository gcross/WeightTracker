#ifndef ENTRYWIDGET_H
#define ENTRYWIDGET_H

#include <memory>

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

    std::shared_ptr<sqlite3> database;
    std::shared_ptr<sqlite3_stmt> insert_statement;

    void saveAndClear();
    void setToNow();

public:
    explicit EntryWidget(const QString &filename, QWidget *parent = 0);

    const QString filename, name;
};

#endif // ENTRYWIDGET_H
