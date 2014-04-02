#include <utils.h>

QDateTime nowWithoutSeconds()
{
    QDateTime now(QDateTime::currentDateTime());
    QTime now_time(now.time());
    now_time.setHMS(now_time.hour(),now_time.minute(),0,0);
    now.setTime(now_time);
    return now;
}
