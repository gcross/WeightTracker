#-------------------------------------------------
#
# Project created by QtCreator 2014-03-29T20:10:03
#
#-------------------------------------------------

QT       += core gui printsupport sql

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

CONFIG += c++11

TARGET = WeightTracker
TEMPLATE = app

include(qcustomplot.pri)
include(sqlite3.pri)

SOURCES += main.cpp \
        mainwindow.cpp \
    entrywidget.cpp \
    utils.cpp

HEADERS  += mainwindow.h \
    entrywidget.h \
    utils.h
