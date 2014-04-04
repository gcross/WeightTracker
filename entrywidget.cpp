#include "entrywidget.h"

#include "utils.h"

#include <QBoxLayout>
#include <QFileInfo>
#include <QLabel>
#include <QMessageBox>
#include <QPushButton>

#include "sqlite3.h"

EntryWidget::EntryWidget(const QString &filename, QWidget *parent) :
    QWidget(parent),
    weight_field(new QLineEdit(this)),
    date_time_field(new QDateTimeEdit(nowWithoutSeconds(),this)),
    filename(filename),
    name(QFileInfo(filename).baseName())
{
    {
        sqlite3 *_database;
        doOrThrow(sqlite3_open(filename.toUtf8().data(),&_database));
        database.reset(_database,sqlite3_close);
    }

   {
        sqlite3_stmt *create_statement;
        const char *tail;
        const char sql[] = "create table if not exists weights (timestamp integer, weight real)";
        doOrThrow(sqlite3_prepare_v2(database.get(),sql,static_cast<int>(sizeof(sql)),&create_statement,&tail));
        sqlite3_finalize(create_statement);
    }

    {
        sqlite3_stmt *_insert_statement;
        const char *tail;
        const char sql[] = "insert into weights (timestamp,weight) values (?,?)";
        doOrThrow(sqlite3_prepare_v2(database.get(),sql,static_cast<int>(sizeof(sql)),&_insert_statement,&tail));
        insert_statement.reset(_insert_statement,sqlite3_finalize);
    }

    auto layout = new QVBoxLayout(this);
    setLayout(layout);

    auto weight_box = new QHBoxLayout();
    layout->addLayout(weight_box);
    weight_box->addWidget(new QLabel(tr("Weight:"),this));
    connect(weight_field,&QLineEdit::returnPressed,this,&EntryWidget::saveAndClear);
    weight_box->addWidget(weight_field);
    auto save_button = new QPushButton(tr("Save and Clear"),this);
    connect(save_button,&QPushButton::clicked,this,&EntryWidget::saveAndClear);
    weight_box->addWidget(save_button);

    auto date_time_box = new QHBoxLayout();
    layout->addLayout(date_time_box);
    date_time_box->addWidget(new QLabel(tr("Date and Time:"),this));
    date_time_box->addWidget(date_time_field);
    auto now_button = new QPushButton(tr("Set to Now"),this);
    connect(now_button,&QPushButton::clicked,this,&EntryWidget::setToNow);
    date_time_box->addWidget(now_button);
}

void EntryWidget::saveAndClear()
{
    try
    {
        doOrThrow(sqlite3_reset(insert_statement.get()));
        doOrThrow(sqlite3_bind_int64(insert_statement.get(),1,date_time_field->dateTime().toTime_t()));
        bool ok;
        doOrThrow(sqlite3_bind_double(insert_statement.get(),2,weight_field->text().toDouble(&ok)));
        if(!ok)
        {
            QMessageBox::information(
                this,
                tr("Error"),
                tr("The given weight value, \"%1\", is not a valid number.").arg(weight_field->text())
            );
            return;
        }
        doOrThrow(sqlite3_step(insert_statement.get()),SQLITE_DONE);
        weight_field->setText(QString());
    }
    catch (std::exception &e)
    {
        QMessageBox::information(
            this,
            tr("Error Saving Weight"),
            QLatin1String(e.what())
        );
    }
}

void EntryWidget::setToNow()
{
    date_time_field->setDateTime(nowWithoutSeconds());
}
