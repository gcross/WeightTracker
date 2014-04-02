#include "entrywidget.h"

#include "utils.h"

#include <QBoxLayout>
#include <QFileInfo>
#include <QLabel>
#include <QMessageBox>
#include <QPushButton>

EntryWidget::EntryWidget(const QString &filename, QWidget *parent) :
    QWidget(parent),
    weight_field(new QLineEdit(this)),
    date_time_field(new QDateTimeEdit(nowWithoutSeconds(),this)),
    database(0),
    filename(filename),
    name(QFileInfo(filename).baseName())
{
    const int status = sqlite3_open(filename.toUtf8().data(),&database);
    if(status != SQLITE_OK)
    {
        throw std::runtime_error(std::string(sqlite3_errstr(status)));
    }

    auto layout = new QVBoxLayout(this);
    setLayout(layout);

    auto weight_box = new QHBoxLayout();
    layout->addLayout(weight_box);
    weight_box->addWidget(new QLabel(tr("Weight:"),this));
    weight_box->addWidget(weight_field);
    auto save_button = new QPushButton(tr("Save and Clear"),this);
    weight_box->addWidget(save_button);

    auto date_time_box = new QHBoxLayout();
    layout->addLayout(date_time_box);
    date_time_box->addWidget(new QLabel(tr("Date and Time:"),this));
    date_time_box->addWidget(date_time_field);
    auto now_button = new QPushButton(tr("Set to Now"),this);
    connect(now_button,&QPushButton::clicked,this,&EntryWidget::setToNow);
    date_time_box->addWidget(now_button);
}

EntryWidget::~EntryWidget()
{
    if(database == nullptr) return;
    sqlite3_close(database);
}

void EntryWidget::setToNow()
{
    date_time_field->setDateTime(nowWithoutSeconds());
}
