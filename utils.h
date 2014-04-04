#ifndef UTILS_H
#define UTILS_H

#include <QDateTime>

#include "sqlite3.h"

void doOrThrow(int status,int ok = SQLITE_OK);

QDateTime nowWithoutSeconds();

#endif // UTILS_H
