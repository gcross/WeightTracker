#include <utils.h>

#include <sqlite3.h>

void doOrThrow(const int status, const int ok) {
    if(status != ok)
    {
        throw std::runtime_error(std::string(sqlite3_errstr(status)));
    }
}

QDateTime nowWithoutSeconds()
{
    QDateTime now(QDateTime::currentDateTime());
    QTime now_time(now.time());
    now_time.setHMS(now_time.hour(),now_time.minute(),0,0);
    now.setTime(now_time);
    return now;
}
